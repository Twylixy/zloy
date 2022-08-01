import os

import peewee

from app.repositories.base import BaseRepository
from app.repositories.violations import ViolationRepository


def init_database() -> None:
    database = peewee.PostgresqlDatabase(
        host=os.getenv("DATABASE_HOST", "database"),
        port=os.getenv("DATABASE_PORT", 5432),
        user=os.getenv("DATABASE_USER", "postgres"),
        password=os.getenv("DATABASE_PASSWORD", "postgres"),
        database=os.getenv("DATABASE_NAME", "postgres"),
    )

    database.create_tables(
        [
            ViolationRepository,
        ]
    )
