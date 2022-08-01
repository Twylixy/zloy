# Env configuration
The **.env** configuration files for that project are separated into 2 files (develop and production). Following explanainsion will help you to configure them.

## Bot Settings
The following variables sets up Bot
```
TOKEN - Bot's Telegram token (string)
VIOLATIONS_LIMIT - Defines max violations count, that user can have (int)
DATABASE_HOST - Database host (string)
DATABASE_PORT - Database port (int)
DATABASE_USER - Database username (string)
DATABASE_PASSWORD - Database password (string)
DATABASE_NAME - Database name (string)
```
---
<br>

## Docker Settings
Variables for Docker Compose.\

### Database
Variables for Docker's database container \
**POSTGRES_PASSWORD** required
```
POSTGRES_USER - Database user (string)
POSTGRES_PASSWORD - User's password (string)
POSTGRES_DB - Database name (string)
```
