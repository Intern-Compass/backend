from sqlalchemy import Table, Column, Integer, String, Float

from src.db import metadata, engine

intern_table = Table(
    "intern",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("email", String),
    Column("phone_number", String),
    Column("desired_division", String),
    Column("status", String),
    Column("rating", Float, default=0.0),
)

metadata.create_all(engine)