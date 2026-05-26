# LLM-DPECI — LLM-Powered Dynamic Pricing Engine with Causal Inference

A modular end-to-end pricing framework combining causal machine learning,
Bayesian Optimization, and RAG-based LLM report generation for retail
and e-commerce, as described in our research paper published in IJSRED
Volume 9, Issue 3, May-June 2026.

---

## Team Structure

| Member | Role | Guide |
|---|---|---|
| Member 1 | Frontend Developer | frontend/ |
| Member 2 | Backend Developer | README_BACKEND.md |
| Member 3 | Data and Causal Inference | README_CAUSAL.md |
| Member 4 | Database Engineer | database/ |

---

## Project Architecture

Frontend (React + Tailwind)
↓
Backend (FastAPI)
↓
Database Layer
↓
MySQL (Docker Container)

---

## Quick Start — All Members

### Step 1: Clone the project

git clone https://github.com/sundeep-14/LLM-Powered-Dynamic-Pricing-Engine-with-Causal-Inference-for-Retail-and-E-Commerce.git
cd LLM-Powered-Dynamic-Pricing-Engine-with-Causal-Inference-for-Retail-and-E-Commerce

### Step 2: Set up environment variables
cp .env.example .env
Then open .env and fill in your actual credentials.

### Step 3: Install database dependencies
pip install sqlalchemy pymysql alembic passlib bcrypt==4.0.1
pip install python-jose python-dotenv "pydantic[email]"

### Step 4: Start MySQL with Docker
docker-compose up -d

### Step 5: Run migrations
python -m alembic upgrade head

### Step 6: Seed starter data
python -m database.init_db

### Step 7: Verify everything works
python test_queries.py

---

## Database Tables

| Table | Purpose |
|---|---|
| users | User accounts and login credentials |
| roles | User roles — admin, analyst, manager |
| products | Products being priced by the engine |
| pricing | Price recommendations and actual outcomes |
| causal_results | DML price elasticity estimates from DoWhy + EconML |
| competitor_pricing | Competitor price snapshots for confounders |
| reports | LLM-generated pricing strategy reports |
| activity_logs | Full audit trail of all system actions |

---

## Key Commands

| Command | Purpose |
|---|---|
| docker-compose up -d | Start MySQL container |
| docker-compose down | Stop MySQL container |
| docker ps | Check container status |
| python -m alembic upgrade head | Apply all migrations |
| python -m alembic revision --autogenerate -m "msg" | Create new migration |
| python -m database.init_db | Seed starter data |
| python test_queries.py | Test all database queries |

---

## Member Guides

- Backend Developer → README_BACKEND.md
- Data and Causal Inference Engineer → README_CAUSAL.md

---

## Database Connection
Host:      localhost
Port:      3307
Database:  llm_dpeci
User:      dpeci_user
Password:  (see .env file)

---

## References

This project implements the LLM-DPECI framework proposed in:
Sundeep Kumar P, Harish Patil, Pratibha S, Sai Shivani K, Anita Patil.
"LLM-Powered Dynamic Pricing Engine with Causal Inference for Retail
and E-Commerce." IJSRED, Volume 9, Issue 3, May-June 2026.