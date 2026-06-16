<![CDATA[# 🧠 AI-Powered Skill Gap Analyser

An intelligent, full-stack resume analysis platform that leverages AI to identify skill gaps, generate personalized learning roadmaps, and help you land your target role.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)

---

## ✨ Features

- 📄 **Resume Upload & Parsing** — Upload a PDF resume; text is extracted via pdfplumber, PyPDF2 & pytesseract (OCR fallback).
- 🤖 **AI-Powered Analysis** — OpenRouter API (Amazon Nova Micro) evaluates your resume against a target role.
- 📊 **ATS Score** — Get a compatibility score showing how well your resume passes Applicant Tracking Systems.
- 🎯 **Skill Gap Detection** — Identifies missing technical & soft skills for your desired position.
- 🗺️ **Skill Roadmap** — Receive a prioritised, step-by-step learning path to bridge the gap.
- 🎥 **Learning Resources** — Curated YouTube tutorials for each missing skill.
- 📈 **Progress Tracking** — Mark skills as *not started*, *in progress*, or *completed* and monitor growth over time.
- 👤 **User Profiles** — Persistent accounts with analysis history, statistics, and profile customisation.
- ⚡ **Redis Caching** — Optional Redis integration for faster repeat analyses.

---

## 🏗️ Tech Stack

| Layer              | Technology                                            |
| ------------------ | ----------------------------------------------------- |
| **Frontend**       | React 18 · Vite · Tailwind CSS · Framer Motion        |
| **3D / Charts**    | Three.js (react-three-fiber) · Chart.js               |
| **Backend**        | Flask 3.0 · Flask-SQLAlchemy · Flask-CORS              |
| **Database**       | SQLite (default) · any SQLAlchemy-supported DB         |
| **AI**             | OpenRouter API (Amazon Nova Micro)                     |
| **PDF Processing** | pdfplumber · PyPDF2 · pytesseract · pdf2image          |
| **Caching**        | Redis (optional)                                       |
| **Deployment**     | Vercel (frontend) · Render (backend)                   |

---

## 📁 Project Structure

```
AI-Powered-Skill-gap-Analyser/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory (create_app), CORS, blueprint registration
│   │   ├── models.py            # SQLAlchemy models (User, Analysis, LearningProgress)
│   │   ├── routes/
│   │   │   ├── auth.py          # Signup, login, logout, session management
│   │   │   ├── analysis.py      # Resume upload, AI analysis, analysis CRUD
│   │   │   ├── profile.py       # User profile & statistics
│   │   │   └── learning.py      # Learning progress tracking
│   │   └── services/
│   │       ├── ai_analyzer.py   # OpenRouter AI integration & caching
│   │       └── pdf_extractor.py # PDF text extraction & structuring
│   ├── run.py                   # Application entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── Procfile                 # Render deployment
│   ├── render.yaml
│   └── runtime.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Router & page layout
│   │   ├── components/
│   │   │   ├── Home.jsx         # Landing page with 3D background
│   │   │   ├── Scan.jsx         # Resume upload & analysis trigger
│   │   │   ├── Dashboard.jsx    # Analysis results & visualisations
│   │   │   ├── Profile.jsx      # User profile & history
│   │   │   ├── SkillRoadmap.jsx # Interactive learning roadmap
│   │   │   ├── SkillRadar.jsx   # Radar chart skill visualisation
│   │   │   ├── Login.jsx        # Login page
│   │   │   ├── SignUp.jsx       # Registration page
│   │   │   ├── About.jsx        # About page
│   │   │   ├── Blog.jsx         # Blog / resources
│   │   │   ├── Contact.jsx      # Contact form
│   │   │   └── ...
│   │   └── api/                 # API client utilities
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── vercel.json              # Vercel deployment config
│   └── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+
- **Python** 3.9+
- **OpenRouter API Key** — get one free at [openrouter.ai](https://openrouter.ai/)

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create & activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your keys:
#   OPENROUTER_API_KEY=sk-or-...
#   SECRET_KEY=<random-secret>

# 5. Start the server
python run.py
```

The backend starts at **http://localhost:5000**.

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment (optional — defaults to localhost:5000)
cp .env.example .env

# 4. Start the dev server
npm run dev
```

The frontend starts at **http://localhost:5173**.

---

## 📡 API Reference

### Health

| Method | Endpoint  | Description         |
| ------ | --------- | ------------------- |
| GET    | `/`       | API status check    |
| GET    | `/health` | Health check        |

### Authentication (`/auth`)

| Method | Endpoint       | Description              |
| ------ | -------------- | ------------------------ |
| POST   | `/auth/signup` | Create a new account     |
| POST   | `/auth/login`  | Login (returns session)  |
| POST   | `/auth/logout` | Logout (clears session)  |
| GET    | `/auth/me`     | Get current user profile |

### Resume Analysis

| Method | Endpoint                    | Description                                      |
| ------ | --------------------------- | ------------------------------------------------ |
| POST   | `/analyze-resume`           | Upload PDF + target role → AI analysis            |
| GET    | `/analyses/history`         | Paginated analysis history (`?page=1&per_page=10`) |
| GET    | `/analyses/<id>`            | Get specific analysis details                    |
| DELETE | `/analyses/<id>`            | Delete an analysis                               |

### User Profile (`/profile`)

| Method | Endpoint   | Description                             |
| ------ | ---------- | --------------------------------------- |
| GET    | `/profile/` | Get profile with stats & latest analysis |
| PUT    | `/profile/` | Update profile fields                    |

### Learning Progress (`/learning`)

| Method | Endpoint                     | Description                          |
| ------ | ---------------------------- | ------------------------------------ |
| GET    | `/learning/progress`         | Get all learning items (grouped)     |
| POST   | `/learning/progress`         | Add a skill to track                 |
| PUT    | `/learning/progress/<id>`    | Update skill status / notes          |
| DELETE | `/learning/progress/<id>`    | Remove a skill from tracking         |

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable            | Required | Default                  | Description                        |
| ------------------- | -------- | ------------------------ | ---------------------------------- |
| `OPENROUTER_API_KEY` | ✅       | —                        | API key for AI analysis            |
| `SECRET_KEY`        | ✅       | (insecure default)       | Flask session secret               |
| `DATABASE_URL`      | ❌       | `sqlite:///skillgap.db`  | SQLAlchemy database URI            |
| `FRONTEND_URL`      | ❌       | —                        | Production frontend URL for CORS   |
| `REDIS_HOST`        | ❌       | `localhost`              | Redis host for caching             |
| `REDIS_PORT`        | ❌       | `6379`                   | Redis port                         |

### Frontend (`frontend/.env`)

| Variable       | Required | Default                 | Description          |
| -------------- | -------- | ----------------------- | -------------------- |
| `VITE_API_URL` | ❌       | `http://localhost:5000` | Backend API base URL |

---

## 🌐 Deployment

### Frontend → Vercel

The repo includes a `vercel.json` for zero-config deployment:

1. Connect your GitHub repo to [Vercel](https://vercel.com)
2. Set the root directory to `frontend`
3. Add the `VITE_API_URL` environment variable pointing to your backend

### Backend → Render

The repo includes `Procfile`, `render.yaml`, and `runtime.txt`:

1. Connect your GitHub repo to [Render](https://render.com)
2. Set the root directory to `backend`
3. Configure environment variables (`OPENROUTER_API_KEY`, `SECRET_KEY`, `FRONTEND_URL`)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
]]>