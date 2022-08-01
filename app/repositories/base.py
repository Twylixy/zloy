import os

import peewee

from app.helpers.errors import FailedToConnectToDatabaseError


class BaseRepository(peewee.Model):
    class Meta:
        database = peewee.PostgresqlDatabase(
            host=os.getenv("DATABASE_HOST", "database"),
            port=os.getenv("DATABASE_PORT", 5432),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
            database=os.getenv("DATABASE_NAME", "postgres"),
        )

        try:
            database.connect()
        except peewee.OperationalError as error:
            raise FailedToConnectToDatabaseError(error)
        finally:
            database.close()
