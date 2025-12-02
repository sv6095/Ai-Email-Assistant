# JWT utilities
from fastapi import HTTPException, Header
from jose import jwt, JWTError
import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

def get_current_user(authorization: str = Header(None)):
    """
    Dependency to extract and validate user from JWT
    
    Usage in routes:
    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"user": user}
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        
        # Check expiration
        import time
        if payload.get("exp") and payload["exp"] < time.time():
            raise HTTPException(status_code=401, detail="Token expired")
        
        return payload
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_gmail_credentials(user: dict):
    """
    Extract Gmail credentials from user JWT payload
    
    Returns Google Credentials object for API calls
    """
    from google.oauth2.credentials import Credentials
    from datetime import datetime
    
    creds = Credentials(
        token=user.get("access_token"),
        refresh_token=user.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    
    return creds
