from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.user import UserCreate, UserLogin, UserOut, Token
from services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email_or_username,
    get_current_user,
)
from utils.security import create_access_token
from config import settings
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing = get_user_by_email_or_username(db, payload.email, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    user = create_user(db, payload.username, payload.email, payload.password)
    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    expires = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 if payload.remember_me else None
    token = create_access_token(subject=str(user.id), expires_minutes=expires)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
