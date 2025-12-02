# Authentication router
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import requests
import os
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])
# .env is in project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()
# ====== ENV CONFIG ======

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

REDIRECT_URI = f"{BACKEND_URL}/auth/callback"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI],
    }
}


# ======= HELPERS =======

def create_jwt_token(user_data: dict, tokens: dict) -> str:
    payload = {
        "user_id": user_data.get("id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture"),

        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token"),
        "token_expiry": tokens.get("expires_in"),

        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7),
        "jti": secrets.token_urlsafe(32),
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def verify_state(expected: str, received: str):
    if not expected or expected != received:
        raise HTTPException(400, "Invalid OAuth state")


# ======= ROUTES =======

@router.get("/login")
def google_login(request: Request):
    try:
        # Validate client config before creating flow
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                500, 
                "OAuth client credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file."
            )
        
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        auth_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes=False,  # force full re-consent
            prompt="consent"
        )

        request.session["oauth_state"] = state

        return RedirectResponse(auth_url)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"OAuth start failed: {e}")


@router.get("/callback")
def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    if error:
        return RedirectResponse(f"{FRONTEND_URL}/login?error={error}")

    if not code:
        return RedirectResponse(f"{FRONTEND_URL}/login?error=missing_code")

    try:
        verify_state(request.session.get("oauth_state"), state)

        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        flow.fetch_token(code=code)
        creds = flow.credentials

        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {creds.token}"}
        ).json()

        tokens = {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token,
            "expires_in": creds.expiry.timestamp() if creds.expiry else None,
        }

        jwt_token = create_jwt_token(userinfo, tokens)

        return RedirectResponse(f"{FRONTEND_URL}/dashboard?token={jwt_token}")

    except Exception as e:
        print("OAuth Error:", e)
        return RedirectResponse(f"{FRONTEND_URL}/login?error=auth_failed")


@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
        )

        from google.auth.transport.requests import Request as GoogleRequest
        creds.refresh(GoogleRequest())

        return {
            "access_token": creds.token,
            "expires_in": (creds.expiry - datetime.utcnow()).total_seconds()
            if creds.expiry else None,
        }

    except Exception as e:
        raise HTTPException(401, f"Failed to refresh token: {e}")


@router.post("/logout")
def logout(token: str):
    res = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": token},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )

    if res.status_code != 200:
        raise HTTPException(400, "Failed to revoke token")

    return {"message": "Logged out"}


@router.get("/me")
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")

    token = auth.split()[1]

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "name": payload.get("name"),
            "picture": payload.get("picture"),
        }

    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

