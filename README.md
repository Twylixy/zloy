# @zloy_bot
The simple chat manager bot for Telegram's group.

## Requirements
* Docker
* Docker Compose
* Poetry package manager (for develop)

## Deploy
Before deploying make sure that you've configure `.env` file correctly. Detailed information about `.env` files configuration descibed in `ENVCONF.md`
### Develop
```bash
docker-compose -f docker-compose.dev.yml -p zloy up --build -d

#if it has already been built before
docker-compose -f docker-compose.dev.yml -p zloy up -d
```
### Production
```bash
docker-compose -f docker-compose.prod.yml -p zloy up --build -d

# if it has already been built before
docker-compose -f docker-compose.prod.yml -p zloy up -d
```

## Features
  * Channel mentions detector
  * Ban anonymous users
  * Auto-moderation system (links, channel mentions)
