# AI Email Assistant 

## What is This?

The AI Email Assistant is an intelligent email management tool that lets you interact with your Gmail inbox using natural language. Instead of manually reading and sorting emails, just tell the app what you want to do—like "summarize my emails from today" or "generate a professional reply to John"—and it handles it for you using Google Gemini AI. It's like having a personal email assistant powered by artificial intelligence.

## What Can It Do?

- **Summarize Emails** - Get the key points from your emails instantly
- **Chat with Your Inbox** - Use natural language to ask questions and give commands
- **Generate Smart Replies** - Let AI help you write professional responses
- **Organize Emails** - Automatically categorize emails (Work, Personal, Promotions, etc.)
- **Get Daily Digest** - See everything important from today in one place
- **Search Intelligently** - Find emails using natural language, not keywords
- **Manage Emails** - Delete and organize with simple voice or text commands
- **Secure Login** - Sign in safely with your Google account

## Technologies We Used

**Backend Stack:**
- **FastAPI** - A modern, fast Python web framework for building APIs
- **Google Gemini AI** - The AI engine that understands and processes your emails
- **Google Gmail API** - Official API to access your Gmail safely
- **Python-JOSE** - Library for creating secure authentication tokens
- **JWT (JSON Web Tokens)** - For secure, stateless user sessions

**Frontend Stack:**
- **React 19** - JavaScript library for building the user interface
- **Vite** - Super-fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Lucide React** - Beautiful icon library

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 18+** and npm
- **Google Cloud Project** with Gmail API and Gemini API enabled

## Getting Started - Quick Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd email-assistant
```

### 2. Set Up Google Cloud Credentials

**Here's the key part:** You need to set up OAuth credentials so the app can access your Gmail safely.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Search for and enable these APIs:
   - Gmail API
   - Google Generative AI API (for Gemini)
4. Create OAuth 2.0 credentials:
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add this authorized redirect URI:
     - `https://ai-email-assistant-g4go.onrender.com/auth/callback`
   - **Important:** Always use the backend Render URL for OAuth callbacks so Google sends the authorization code directly to the API instead of any local environment.
   - Save your **Client ID** and **Client Secret**—you'll need these soon
5. Generate a Gemini API key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy this key

### 3. Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the project root (`email-assistant/.env`) with the following variables:
```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# JWT Secret Key (generate a random secret key)
JWT_SECRET_KEY=your_jwt_secret_key

# API URLs
FRONTEND_URL=https://ai-email-assistant-pxbe.vercel.app
BACKEND_URL=https://ai-email-assistant-g4go.onrender.com

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the frontend directory with the following variable:
```env
# Backend API URL
VITE_API_BASE_URL=https://ai-email-assistant-g4go.onrender.com
```

### 4. Google Cloud Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Gemini API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add the authorized redirect URI `https://ai-email-assistant-g4go.onrender.com/auth/callback`
   - Copy the Client ID and Client Secret to your `.env` file
5. Get your Gemini API key:
   - Go to "APIs & Services" > "Credentials"
   - Create API key for Gemini API
   - Add it to your `.env` file

## Running the Application

### Backend Server (Hosted)

- Production API: `https://ai-email-assistant-g4go.onrender.com`
- Interactive docs:
  - Swagger UI: `https://ai-email-assistant-g4go.onrender.com/docs`
  - ReDoc: `https://ai-email-assistant-g4go.onrender.com/redoc`

### Frontend Application (Hosted)

- Production UI: `https://ai-email-assistant-pxbe.vercel.app`

> If you need to run the project locally for development, set your own `FRONTEND_URL` and `BACKEND_URL` in `.env` to match your environment before starting the servers.

## Usage

1. **Access the Application**: Open `https://ai-email-assistant-pxbe.vercel.app` in your browser
2. **Login**: Click "Login with Google" to authenticate with your Google account
3. **Grant Permissions**: Authorize the application to access your Gmail
4. **Start Chatting**: Use natural language commands to interact with your emails

### Example Commands

- `"Show me my last 5 emails"`
- `"Categorize my emails"`
- `"Give me today's email digest"`
- `"Generate replies for my emails"`
- `"Reply to email number 2"`
- `"Delete email number 3"`
- `"Search for emails from john@example.com"`

## Project Structure

```
email-assistant/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routers/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # Chat and email processing endpoints
│   │   └── emails.py          # Email-specific endpoints
│   ├── services/
│   │   ├── gemini_service.py  # Gemini AI integration
│   │   ├── gmail_service.py   # Gmail API operations
│   │   └── nlp_service.py     # Natural language processing
│   └── utils/
│       └── jwt.py             # JWT token utilities
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service functions
│   │   └── hooks/             # Custom React hooks
│   ├── package.json           # Node.js dependencies
│   └── vite.config.js         # Vite configuration
└── .env                       # Environment variables (create this)
```

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Google OAuth login
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/me` - Get current user information
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

### Chat
- `POST /chat/message` - Process natural language message
- `POST /chat/action` - Execute specific actions (send reply, delete email, etc.)

## Environment Variables

Here's what each variable does and where to get it:

| Variable | Description | How to Get It | Required |
|----------|-------------|---------------|----------|
| `GOOGLE_CLIENT_ID` | Your Google OAuth app ID | Google Cloud Console → Credentials | Yes |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth app secret | Google Cloud Console → Credentials | Yes |
| `JWT_SECRET_KEY` | Secret key for signing authentication tokens | Generate a random string (use `python -c "import secrets; print(secrets.token_hex(32))"`) | Yes |
| `GEMINI_API_KEY` | API key for Google Gemini AI | Google Cloud Console → APIs & Services → Credentials | Yes |
| `FRONTEND_URL` | Where your frontend is hosted | Your frontend deployment URL (e.g., Vercel) | No (default: https://ai-email-assistant-pxbe.vercel.app) |
| `BACKEND_URL` | Where your backend is hosted | Your backend deployment URL (e.g., Render) | No (default: https://ai-email-assistant-g4go.onrender.com) |
| `VITE_API_BASE_URL` | Backend URL for frontend to call (frontend .env only) | Same as BACKEND_URL | No (default: https://ai-email-assistant-g4go.onrender.com) |

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys and secrets secure
- Use strong, randomly generated `JWT_SECRET_KEY`
- The application uses OAuth 2.0 for secure authentication
- JWT tokens expire after 7 days

## Assumptions & Known Limitations

### Assumptions

- **Gmail Account Required** - Users must have an active Google account with Gmail enabled
- **API Quotas** - This project uses Google API quotas. Ensure your Google Cloud project has sufficient quota for Gmail API and Gemini API requests
- **Network Connectivity** - The application requires internet connectivity to authenticate with Google and call Gemini API
- **Browser Support** - Frontend is tested on modern browsers (Chrome, Firefox, Safari, Edge)
- **Email Format** - Email processing works best with standard email formats; complex HTML emails may have variable results

### Known Limitations

- **Email Volume** - Initial email loading may take time with very large inboxes (1000+ emails)
- **AI Response Time** - Gemini API calls may take 2-5 seconds per request depending on load
- **Rich Text Support** - The app currently handles plain text and basic HTML emails. Complex formatting may not render perfectly
- **Attachment Handling** - Email attachments are detected but not downloadable through the UI
- **Rate Limiting** - Google APIs have rate limits. High-volume usage may be throttled
- **Language Support** - Natural language processing is optimized for English; other languages may have variable results
- **OAuth Token Expiry** - Users need to re-authenticate if OAuth tokens expire (typically after 7 days of inactivity)
- **Email Deletion** - Deleted emails go to Gmail trash; permanent deletion is not supported

## Development

### Backend Development

- The backend uses FastAPI with automatic API documentation
- Access API docs at `https://ai-email-assistant-g4go.onrender.com/docs` (Swagger UI)
- Alternative docs at `https://ai-email-assistant-g4go.onrender.com/redoc` (ReDoc)

### Frontend Development

- Hot module replacement is enabled in development mode
- ESLint is configured for code quality
- Tailwind CSS is used for styling

## Building for Production

### Backend

The backend can be deployed using any ASGI-compatible server (e.g., Gunicorn, uvicorn):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

Build the frontend for production:

```bash
cd frontend
npm run build
```

The production build will be in the `frontend/dist` directory.

## Troubleshooting

### Common Issues

1. **OAuth Error**: Make sure your redirect URI matches exactly in Google Cloud Console
2. **Gmail API Error**: Ensure Gmail API is enabled in your Google Cloud project
3. **Gemini API Error**: Verify your Gemini API key is correct and the API is enabled
4. **CORS Error**: Check that `FRONTEND_URL` in `.env` matches your frontend URL
