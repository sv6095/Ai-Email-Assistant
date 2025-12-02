# AI Email Assistant

An intelligent email management application powered by Google Gemini AI that helps you manage your Gmail inbox through natural language commands. Read, summarize, categorize, and generate replies to your emails using conversational AI.

## Features

- 🤖 **AI-Powered Email Summarization** - Get concise summaries of your emails using Google Gemini AI
- 💬 **Natural Language Commands** - Interact with your emails using plain English
- 📝 **Smart Reply Generation** - Generate contextually appropriate email replies
- 📊 **Email Categorization** - Automatically categorize emails into Work, Personal, Promotions, Urgent, and Other
- 📅 **Daily Email Digest** - Get a summary of all emails received today
- 🔍 **Email Search** - Search through your inbox with natural language queries
- 🗑️ **Email Management** - Delete emails with simple commands
- 🔐 **Secure Authentication** - OAuth 2.0 authentication with Google

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google Gmail API** - Email access and management
- **Google Gemini AI** - Natural language processing and email intelligence
- **JWT** - Secure token-based authentication
- **Python-JOSE** - JWT encoding/decoding

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Node.js 18+** and npm
- **Google Cloud Project** with:
  - Gmail API enabled
  - OAuth 2.0 credentials configured
  - Gemini API enabled

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd email-assistant
```

### 2. Backend Setup

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
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

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
   - Add authorized redirect URI: `http://localhost:8000/auth/callback`
   - Copy the Client ID and Client Secret to your `.env` file
5. Get your Gemini API key:
   - Go to "APIs & Services" > "Credentials"
   - Create API key for Gemini API
   - Add it to your `.env` file

## Running the Application

### Start the Backend Server

1. Navigate to the backend directory:
```bash
cd backend
```

2. Activate your virtual environment (if not already activated)

3. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

### Start the Frontend Development Server

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Start the development server:
```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173`

## Usage

1. **Access the Application**: Open `http://localhost:5173` in your browser
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

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `FRONTEND_URL` | Frontend application URL | No (default: http://localhost:5173) |
| `BACKEND_URL` | Backend API URL | No (default: http://localhost:8000) |

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys and secrets secure
- Use strong, randomly generated `JWT_SECRET_KEY`
- The application uses OAuth 2.0 for secure authentication
- JWT tokens expire after 7 days

## Development

### Backend Development

- The backend uses FastAPI with automatic API documentation
- Access API docs at `http://localhost:8000/docs` (Swagger UI)
- Alternative docs at `http://localhost:8000/redoc` (ReDoc)

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

- React

