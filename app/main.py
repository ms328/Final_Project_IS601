"""
FastAPI Main Application Module

This module defines the main FastAPI application, including:
- Application initialization and configuration
- API endpoints for user authentication
- API endpoints for calculation management (BREAD operations)
- Report / History feature endpoints
- Web routes for HTML templates
- Database table creation on startup
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
import uvicorn

# Application imports
from app.database import Base, get_db, engine
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.calculation import Calculation
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse
from app.schemas.calculation import (
    CalculationBase,
    CalculationResponse,
    CalculationUpdate,
)

# 🔹 NEW: Report routes
from app.routes import reports


# ------------------------------------------------------------------------------
# Database startup
# ------------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    yield


# ------------------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------------------
app = FastAPI(
    title="Calculations API",
    description="API for managing calculations with history reporting",
    version="1.0.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(reports.router)

# Static files & templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ------------------------------------------------------------------------------
# Web Routes
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, tags=["web"])
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse, tags=["web"])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, tags=["web"])
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/dashboard/view/{calc_id}", response_class=HTMLResponse, tags=["web"])
def view_calc(request: Request, calc_id: str):
    return templates.TemplateResponse(
        "view_calculation.html",
        {"request": request, "calc_id": calc_id},
    )


@app.get("/dashboard/edit/{calc_id}", response_class=HTMLResponse, tags=["web"])
def edit_calc(request: Request, calc_id: str):
    return templates.TemplateResponse(
        "edit_calculation.html",
        {"request": request, "calc_id": calc_id},
    )


# ------------------------------------------------------------------------------
# Health
# ------------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


# ------------------------------------------------------------------------------
# Authentication
# ------------------------------------------------------------------------------
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    try:
        user = User.register(
            db, user_create.dict(exclude={"confirm_password"})
        )
        db.commit()
        db.refresh(user)
        return user
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    auth = User.authenticate(
        db, user_login.username, user_login.password
    )
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    return TokenResponse(
        access_token=auth["access_token"],
        refresh_token=auth["refresh_token"],
        token_type="bearer",
        expires_at=expires_at,
        user_id=auth["user"].id,
        username=auth["user"].username,
        email=auth["user"].email,
        first_name=auth["user"].first_name,
        last_name=auth["user"].last_name,
        is_active=auth["user"].is_active,
        is_verified=auth["user"].is_verified,
    )


@app.post("/auth/token", tags=["auth"])
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    auth = User.authenticate(db, form.username, form.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": auth["access_token"],
        "token_type": "bearer",
    }


# ------------------------------------------------------------------------------
# Calculations (BREAD)
# ------------------------------------------------------------------------------
@app.post(
    "/calculations",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def create_calculation(
    data: CalculationBase,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        calc = Calculation.create(
            calculation_type=data.type,
            user_id=current_user.id,
            inputs=data.inputs,
        )
        calc.result = calc.get_result()

        db.add(calc)
        db.commit()
        db.refresh(calc)
        return calc
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/calculations",
    response_model=List[CalculationResponse],
    tags=["calculations"],
)
def list_calculations(
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .order_by(Calculation.created_at.desc())
        .all()
    )


@app.get(
    "/calculations/{calc_id}",
    response_model=CalculationResponse,
    tags=["calculations"],
)
def get_calculation(
    calc_id: str,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == calc_uuid,
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    return calc


@app.put(
    "/calculations/{calc_id}",
    response_model=CalculationResponse,
    tags=["calculations"],
)
def update_calculation(
    calc_id: str,
    update: CalculationUpdate,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == UUID(calc_id),
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    if update.inputs is not None:
        calc.inputs = update.inputs
        calc.result = calc.get_result()

    calc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calc)
    return calc


@app.delete(
    "/calculations/{calc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["calculations"],
)
def delete_calculation(
    calc_id: str,
    current_user=Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    calc = (
        db.query(Calculation)
        .filter(
            Calculation.id == UUID(calc_id),
            Calculation.user_id == current_user.id,
        )
        .first()
    )

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(calc)
    db.commit()


# ------------------------------------------------------------------------------
# Run
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
