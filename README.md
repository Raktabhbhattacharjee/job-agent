# 🎯 AI Job & Internship Agent

An end-to-end, AI-powered career co-pilot designed to streamline tech internship and job hunting. The agent analyzes candidate resumes, scrapes live job opportunities across **LinkedIn India**, **Internshala**, and **RemoteOK** (100% ban-proof), evaluates company expectations and **DSA requirements** via Groq LLMs, and ranks jobs by personalized fit score.

---

## 🚀 Key Features

* **📄 AI Resume Intelligence**:
  * Upload your PDF resume; parsed via `PyMuPDF`.
  * Analyzed by Groq LLM (`llama-3.3-70b`) into a structured candidate profile: extracted tech skills, past project accomplishments, and identified target roles.

* **🇮🇳 Live Indian Internship & Global Job Ingestion**:
  * **LinkedIn India**: Uses public guest endpoints with **zero login required** (0% ban risk) to pull live tech internships in Bengaluru, Hyderabad, Gurugram, Mumbai, Pune, and remote India.
  * **Internshala**: Scrapes student-friendly Indian internships, extracting verified **INR stipends** (`Rs. 15,000 - 1,50,000 /month`) and direct apply links.
  * **RemoteOK**: Pulls global remote roles via fast JSON API or headless Chromium browser (`Playwright`).

* **🧠 DSA Requirement & Role Expectations Analyzer**:
  * Groq categorizes every internship into:
    * **🟢 Low DSA (Project Focused)**: Practical framework development (FastAPI, React, Django), REST APIs, Git, and take-home tasks. No LeetCode puzzles.
    * **🟡 Moderate DSA**: Standard problem solving (arrays, strings, basic hashmaps, basic SQL).
    * **🔴 Heavy DSA**: Demanding algorithmic rounds (Trees, Graphs, Dynamic Programming, LeetCode Medium/Hard).
  * Automatically extracts **"What the Company Builds"** and **"Intern Expectations"** (3–4 bulleted deliverables).

* **📊 Personalized Match Engine & Gap Advisor**:
  * Cross-references the candidate's skills against each job's requirements.
  * Generates a **Match Score (0–100%)**, highlights **Matched Skills**, and identifies **Missing Skills** to study before applying.

* **⚡ Unified Search & Scrape Toolbar**:
  * Type any skill or role (e.g., `Python`, `React`, `FastAPI`, `Django`, `Full Stack`) and hit **Search & Scrape** to query your database and fetch live postings simultaneously.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Frontend["Frontend (React + Vite + Tailwind CSS)"]
        UI1["Resume Uploader & Profile Viewer"]
        UI2["Job Board with DSA Filters & Drawer"]
        UI3["AI Recommendations & Match Gauge"]
    end

    subgraph Backend["Backend (FastAPI + SQLAlchemy + Alembic)"]
        R1["/resumes & /analysis"]
        R2["/jobs (Search & Multi-Portal Scraper)"]
        R3["/recommendations"]
        DB[(PostgreSQL Database)]
    end

    subgraph External["External Services & Portals"]
        LNK["LinkedIn India (Guest API)"]
        ISH["Internshala Scraper"]
        ROK["RemoteOK API / Playwright"]
        GROQ["Groq LLM (llama-3.3-70b)"]
    end

    UI1 --> R1
    UI2 --> R2
    UI3 --> R3

    R1 --> GROQ
    R2 --> LNK
    R2 --> ISH
    R2 --> ROK
    R2 --> GROQ

    R1 --> DB
    R2 --> DB
    R3 --> DB
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic Settings, Uvicorn |
| **Database** | PostgreSQL |
| **AI / LLM** | Groq API (`llama-3.3-70b-versatile` / `openai/gpt-oss-20b`), PyMuPDF (`fitz`) |
| **Web Scraping** | `httpx`, `BeautifulSoup4`, `Playwright` (Headless Chromium) |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide Icons, Axios |

---

## 📂 Project Structure

```text
job-agent/
├── app/
│   ├── core/
│   │   └── config.py               # Settings & environment configuration
│   ├── database/
│   │   ├── base.py                 # SQLAlchemy declarative base
│   │   └── session.py              # DB engine and session generator
│   ├── models/
│   │   ├── resume.py               # Resume model
│   │   ├── resume_analysis.py      # LLM-extracted candidate profile
│   │   └── job.py                  # Job model (DSA level, expectations, company intel)
│   ├── schemas/
│   │   ├── resume.py               # Resume upload & analysis schemas
│   │   ├── job.py                  # Job & scrape schemas
│   │   └── recommendation.py       # Fit recommendation schemas
│   ├── services/
│   │   ├── file_service.py         # File storage & UUID generation
│   │   ├── parser_service.py       # PDF text extraction (PyMuPDF)
│   │   ├── groq_service.py         # Groq LLM profile extraction & DSA analysis
│   │   ├── scraper_service.py      # Multi-portal scrapers (LinkedIn, Internshala, RemoteOK)
│   │   ├── job_service.py          # Job deduplication and bulk persistence
│   │   └── recommendation_service.py # Scoring and skill-gap matching engine
│   ├── routers/
│   │   ├── resume.py               # POST /resumes/upload
│   │   ├── analysis.py             # POST/GET /analysis/{resume_id}
│   │   ├── jobs.py                 # POST /jobs/scrape, GET /jobs/
│   │   └── recommendations.py      # GET /recommendations/{resume_id}
│   └── main.py                     # FastAPI application entrypoint & CORS
├── alembic/                        # PostgreSQL schema migrations
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx    # Drag-and-drop PDF upload & profile card
│   │   │   ├── JobBoard.jsx        # Search & scrape toolbar, DSA filter, company drawer
│   │   │   └── Recommendations.jsx # Match gauge, matched/missing skills, fit rationale
│   │   ├── services/
│   │   │   └── api.js              # Axios API client
│   │   ├── App.jsx                 # Top-level navigation & state management
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── pyproject.toml                  # Python dependencies managed via uv
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
* **Python 3.13+** (or installed via [`uv`](https://github.com/astral-sh/uv))
* **Node.js 18+** & `npm`
* **PostgreSQL** running locally on port `5432`
* **Groq API Key** (Free from [console.groq.com](https://console.groq.com/))

### 2. Configure Environment Variables
Create a `.env` file in the root `job-agent/` directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job-agent
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Backend Setup
From the project root:

```bash
# 1. Install dependencies via uv
uv sync

# 2. Run database migrations
uv run alembic upgrade head

# 3. (Optional) Install Playwright Chromium browser
uv run playwright install chromium

# 4. Start the FastAPI backend server
uv run uvicorn app.main:app --reload
```
*API will be running at:* `http://127.0.0.1:8000`  
*Swagger Documentation:* `http://127.0.0.1:8000/docs`

### 4. Frontend Setup
From the `frontend/` directory:

```bash
cd frontend

# 1. Install npm packages
npm install

# 2. Start the Vite development server
npm run dev
```
*Frontend will be running at:* `http://localhost:5173`

---

## 📖 How to Use

1. **Upload Resume**:
   * Open `http://localhost:5173`.
   * Drag & drop your PDF resume on the **Resume Analyzer** tab and click **Analyze with AI**.
   * View your skills, experience summary, and target roles extracted by Groq.
2. **Search & Scrape Internships**:
   * Switch to the **Job Board** tab.
   * Make sure **🇮🇳 India Internships** is selected.
   * Type any role or skill (e.g. `Python`, `React`, `Django`, `Full Stack`) into the search bar and press **Enter** or click **Search & Scrape**.
   * It will fetch live opportunities from LinkedIn India & Internshala, analyze DSA expectations, and save them.
3. **Filter by DSA Level**:
   * Click **🟢 Low DSA (Dev/Project)** to see positions where you are evaluated on practical projects, clean code, and frameworks rather than competitive programming rounds.
4. **Inspect Company Intel**:
   * Click **"What They Build & Expect"** on any job card to read what the company is creating and view intern deliverables.
5. **Review AI Recommendations**:
   * Switch to the **AI Matches** tab to see jobs ranked by compatibility with your resume, along with a list of missing skills to master.

---

## 📜 License
MIT License. Built for developers, students, and engineers looking for their next career step.
