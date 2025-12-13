# AI-Powered Skill Gap Analyser

An intelligent resume analysis tool that identifies skill gaps and provides personalized recommendations for career growth.

## Features

- 📄 **Resume Analysis**: Upload your PDF resume for AI-powered analysis
- 🎯 **Skill Gap Detection**: Identifies missing skills for your target role
- 📊 **ATS Score**: Get your resume's ATS compatibility score
- 💡 **Smart Suggestions**: Receive actionable improvement recommendations
- 🎥 **Learning Resources**: Get YouTube tutorial links for missing skills

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Flask + Python
- **AI**: OpenRouter API (using Amazon Nova Micro)
- **PDF Processing**: pdfplumber, PyPDF2, pytesseract

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- OpenRouter API Key (get one at https://openrouter.ai/)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Add your OpenRouter API key to `.env`:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   SECRET_KEY=your-secret-key-for-sessions
   ```

6. Run the backend server:
   ```bash
   python app.py
   ```

   The backend will start at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (optional - defaults to localhost:5000):
   ```
   VITE_API_URL=http://localhost:5000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

   The frontend will start at `http://localhost:5173`

## API Endpoints

### Resume Analysis
- `POST /analyze-resume` - Upload and analyze a resume PDF
  - Form data: `resume` (PDF file), `target_role` (string)

### Authentication
- `POST /auth/signup` - Create a new account
- `POST /auth/login` - Login to existing account
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user

### Health
- `GET /health` - API health check

## Usage

1. Visit the application at `http://localhost:5173`
2. Click on "Scan" to upload your resume
3. Upload a PDF resume and enter your target job role
4. View your skill gap analysis on the dashboard

## Optional: Redis Caching

For improved performance, you can optionally enable Redis caching:

1. Install Redis on your system
2. Start Redis server
3. The application will automatically use Redis if available

## License

MIT