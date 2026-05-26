"""
role.py
-------
Roles define what a user is allowed to do in the system.
Examples: "admin", "analyst", "manager"

This is the simplest model — no foreign keys, no relationships.
Perfect starting point to understand how ORM models work.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.session import Base


class Role(Base):
    __tablename__ = "roles"  # this becomes the table name in MySQL

    # Columns — each Column() becomes one column in the table
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at  = Column(DateTime, server_default=func.now())