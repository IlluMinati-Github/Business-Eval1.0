# Full Stack Next.js + FastAPI Project

This is a full-stack application using Next.js for the frontend and FastAPI for the backend.

## Project Structure

```
.
├── frontend/          # Next.js frontend
└── backend/          # FastAPI backend
    ├── app/
    │   └── main.py
    └── venv/         # Python virtual environment
```

## Setup Instructions

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at http://localhost:3000

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend will be available at http://localhost:8000

## API Documentation

Once the backend is running, you can access:
- API documentation at http://localhost:8000/docs
- Alternative API documentation at http://localhost:8000/redoc

## Features

- Frontend: Next.js with TypeScript and Tailwind CSS
- Backend: FastAPI with Python
- CORS enabled for local development
- Basic health check endpoint
- Modern UI with responsive design 