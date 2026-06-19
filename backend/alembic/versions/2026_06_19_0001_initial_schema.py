"""initial schema: users, ingredients, recipes, recipe_ingredients, shopping_list_items

Revision ID: 0001
Revises:
Create Date: 2026-06-19

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("user_id", sa.CHAR(36), primary_key=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(128), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # ingredients
    op.create_table(
        "ingredients",
        sa.Column("ingredient_id", sa.CHAR(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.CHAR(36),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="other"),
        sa.Column("quantity", sa.Float, nullable=False, server_default="0"),
        sa.Column("unit", sa.String(16), nullable=False, server_default="个"),
        sa.Column("storage_location", sa.String(32), nullable=False, server_default="fridge"),
        sa.Column("purchase_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True, index=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    # recipes
    op.create_table(
        "recipes",
        sa.Column("recipe_id", sa.CHAR(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.CHAR(36),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("cook_time", sa.Integer, nullable=True),
        sa.Column("calories", sa.Float, nullable=True),
        sa.Column("servings", sa.Integer, nullable=True),
        sa.Column("steps", sa.JSON, nullable=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("source", sa.String(16), nullable=False, server_default="local"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # recipe_ingredients
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column(
            "recipe_id",
            sa.CHAR(36),
            sa.ForeignKey("recipes.recipe_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("ingredient_name", sa.String(128), nullable=False),
        sa.Column("amount", sa.String(64), nullable=True),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default=sa.text("1")),
    )

    # shopping_list_items
    op.create_table(
        "shopping_list_items",
        sa.Column("item_id", sa.CHAR(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.CHAR(36),
            sa.ForeignKey("users.user_id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("quantity", sa.String(64), nullable=False, server_default="1个"),
        sa.Column("checked", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("shopping_list_items")
    op.drop_table("recipe_ingredients")
    op.drop_table("recipes")
    op.drop_table("ingredients")
    op.drop_table("users")
