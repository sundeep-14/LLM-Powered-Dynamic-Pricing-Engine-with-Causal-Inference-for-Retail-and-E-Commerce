"""
user.py
-------
Stores user accounts. Each user has one role.
Passwords are stored as bcrypt hashes — NEVER plain text.

This model introduces two new concepts:
1. ForeignKey  — links to another table (roles)
2. relationship — lets you access related data in Python
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database.session import Base


class User(Base):
    __tablename__ = "users"

    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(100), unique=True, nullable=False, index=True)
    email            = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password  = Column(String(255), nullable=False)
    is_active        = Column(Boolean, default=True)
    role_id          = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at       = Column(DateTime, server_default=func.now())
    updated_at       = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    role           = relationship("Role", backref="users")
    activity_logs  = relationship("ActivityLog", back_populates="user")