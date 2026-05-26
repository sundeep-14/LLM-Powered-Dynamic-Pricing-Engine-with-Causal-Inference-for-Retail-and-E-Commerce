"""
Import all models here so Alembic can find them automatically.
When you run alembic revision --autogenerate it reads this file
and generates the correct SQL for all your tables.
"""

from database.models.role import Role
from database.models.user import User
from database.models.product import Product
from database.models.pricing import Pricing
from database.models.competitor import Competitor
from database.models.causal_result import CausalResult
from database.models.report import Report
from database.models.activity_log import ActivityLog