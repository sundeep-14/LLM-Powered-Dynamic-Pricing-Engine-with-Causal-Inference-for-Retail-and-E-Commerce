"""
repositories/user_repo.py
--------------------------
All database operations for Users.
"""

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.models.user import User
from database.schemas.user import UserCreate, UserUpdate
from typing import Optional, List

# tells passlib to use bcrypt for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── PASSWORD HELPERS ───────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Converts plain text password to bcrypt hash."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Returns True if plain password matches the stored hash."""
    return pwd_context.verify(plain, hashed)


# ── CREATE ─────────────────────────────────────────────────────────

def create_user(db: Session, data: UserCreate) -> User:
    """
    Insert a new user into the database.
    Hashes the password before saving — plain text never touches the DB.
    """
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role_id=data.role_id,
    )
    db.add(user)      # stages the insert
    db.commit()       # executes INSERT INTO users...
    db.refresh(user)  # reloads object so id and created_at are populated
    return user


# ── READ ───────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Pagination — skip and limit control which page of results you get.
    Page 1: skip=0,   limit=10  → rows 1-10
    Page 2: skip=10,  limit=10  → rows 11-20
    Page 3: skip=20,  limit=10  → rows 21-30
    """
    return db.query(User).offset(skip).limit(limit).all()


# ── UPDATE ─────────────────────────────────────────────────────────

def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    if data.is_active is not None:
        user.is_active = data.is_active
    db.commit()
    db.refresh(user)
    return user


# ── DELETE ─────────────────────────────────────────────────────────

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# ── AUTH ───────────────────────────────────────────────────────────

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Returns User if credentials are valid, None if not.
    Called during login.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user