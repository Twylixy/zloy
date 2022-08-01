from datetime import datetime

import peewee

from app.repositories.base import BaseRepository


class ViolationRepository(BaseRepository):
    id = peewee.PrimaryKeyField()
    telegram_id = peewee.BigIntegerField(null=False)
    admin_telegram_id = peewee.BigIntegerField(null=False)
    violation_level = peewee.IntegerField(null=False)
    has_urls = peewee.BooleanField(null=False)
    urls = peewee.TextField(null=False)
    has_user_mentions = peewee.BooleanField(null=False)
    user_mentions = peewee.TextField(null=False)
    has_channel_mentions = peewee.BooleanField(null=False)
    channel_mentions = peewee.TextField(null=False)
    reason = peewee.TextField(null=False)
    violated_at = peewee.DateTimeField(null=False, default=datetime.now)

    class Meta:
        db_table = "violations"
