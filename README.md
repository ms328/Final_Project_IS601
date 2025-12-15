📊 FastAPI Calculations Application

Final Project – IS601 (Fall 2025)
Author: Megha Saju
Docker Hub: https://hub.docker.com/r/msaju20

📌 Project Overview

This project is a full-stack FastAPI web application that allows authenticated users to perform mathematical calculations, view and manage their calculation history, and analyze their usage through a Calculation History & Reporting feature.

The application demonstrates professional backend development practices, including:

RESTful API design

JWT-based authentication and authorization

SQLAlchemy ORM with PostgreSQL

Pydantic validation

Automated testing (unit, integration, and E2E)

Docker containerization

CI/CD with GitHub Actions

This project fulfills all requirements for the IS601 Final Project – Advanced Feature Integration.

🚀 Features
🔐 Authentication & Security

User registration and login

Secure password hashing with bcrypt

JWT access and refresh tokens

Protected routes using FastAPI dependencies

🧮 Calculation Management (BREAD)

Browse: View all calculations

Read: View individual calculations

Edit: Update calculation inputs and recompute results

Add: Create new calculations

Delete: Remove calculations

Supported calculation types:

Addition

Subtraction

Multiplication

Division

📈 **New Advanced Feature: Calculation Reports & Analytics**

**The final project feature** provides comprehensive usage analytics for authenticated users:

**Backend API (`/reports/usage`)**:
- **Total calculations**: Count of all calculations performed by user
- **Breakdown by type**: Number of additions, subtractions, multiplications, divisions
- **Average result**: Mean value of all calculation results
- Protected by JWT authentication
- User-isolated data (each user only sees their own stats)

**Front-End Integration**:
- Real-time stats display on dashboard
- Automatically updates when calculations are created or deleted
- Clean, professional UI with Tailwind CSS

**Testing Coverage**:
- **4 Integration tests**: API functionality, database queries, authorization, user isolation
- **3 E2E tests**: Full workflow, empty state, average calculation accuracy
- Total: **105 passing tests, 85% code coverage**

This feature demonstrates:
- ✅ New database queries (aggregation with SQLAlchemy)
- ✅ RESTful API endpoint design
- ✅ Pydantic schema validation
- ✅ Comprehensive test coverage (unit, integration, E2E)
- ✅ Seamless front-end/back-end integration

🧱 Tech Stack
Layer	Technology
Backend	FastAPI, Python
Database	PostgreSQL
ORM	SQLAlchemy
Validation	Pydantic
Auth	JWT, OAuth2
Front-End	HTML, Tailwind CSS, JavaScript
Testing	Pytest, Playwright
Containerization	Docker, Docker Compose
CI/CD	GitHub Actions
🗂 Project Structure
app/
├── auth/               # Authentication dependencies
├── core/               # Configuration & security
├── database.py         # DB session & engine
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic schemas
├── main.py             # FastAPI app & routes
templates/              # HTML templates
static/                 # CSS & JS
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
├── e2e/                # Playwright E2E tests
docker-compose.yml
Dockerfile
README.md

🐳 Running the Application with Docker (Recommended)
1️⃣ Pull the Image from Docker Hub
docker pull msaju20/module14_is601

2️⃣ Run with Docker Compose
docker-compose up --build


Services started:

FastAPI app → http://localhost:8000

PostgreSQL → port 5432

pgAdmin → http://localhost:5050

💻 Running Locally (Without Docker)
1️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Set Environment Variables

Create a .env file:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key

4️⃣ Start the Server
uvicorn app.main:app --reload


Visit:

App: http://localhost:8000

API Docs: http://localhost:8000/docs

🧪 Running Tests
Run All Tests
pytest

With Coverage Report
pytest --cov=app --cov-report=html --cov-report=term

Run Slow (E2E) Tests
pytest --run-slow

**Test Coverage Summary** (105 tests, 85% coverage):

**Unit tests** (20 tests): Calculation logic for addition, subtraction, multiplication, division

**Integration tests** (72 tests):
- Database operations & connections
- User authentication & registration
- Calculation CRUD operations
- **Reports API** (4 tests): usage stats, authorization, user isolation
- Pydantic schema validation

**E2E tests** (14 tests):
- Full user registration & login flow
- Calculation CRUD via API
- **Reports endpoint** (3 tests): stats accuracy, authentication, average calculation

Integration tests for database & routes

Playwright E2E tests for UI workflows

📊 **Reports Feature Tests**:
- Integration: 4 tests (empty state, multiple calculations, unauthorized access, user isolation)
- E2E: 3 tests (full workflow, authentication requirement, average calculation accuracy)

🔁 CI/CD Pipeline

GitHub Actions pipeline automatically:

Runs all tests

Builds Docker image

Pushes image to Docker Hub (msaju20) on success

This ensures consistent, production-ready deployments.

📽 Video Demo

A 5–6 minute demo video accompanies this project, demonstrating:

User authentication

Calculation creation & history

Reporting feature

API routes

Tests & Docker setup

🧠 Learning Outcomes Addressed

CLO3: Automated testing

CLO4: CI/CD with GitHub Actions

CLO9: Docker containerization

CLO10: REST API development

CLO11: SQL database integration

CLO12: JSON validation with Pydantic

CLO13: Secure authentication practices