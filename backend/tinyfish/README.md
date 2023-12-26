# Sync jobs management for TinyFish based on the danswer connectors
Only depend on the connectors of the `danswer` package, not the full `danswer` package.
1. danswer/backend/danswer/configs/constants.py
2. danswer/backend/danswer/connectors/*

# APIs
```text
post /api/v1/sync/start
post /api/v1/sync/stop/{sync_id}
```


# [Optional] debug danswer backend, background task and frontend
https://github.com/danswer-ai/danswer/blob/main/CONTRIBUTING.md

## start vespa index db and relational db
```bash
cd ./deployment/docker_compose
docker compose -f docker-compose.dev.yml -p danswer-stack up -d index relational_db
```

## initial db
```bash
cd ./backend
alembic upgrade head
```


## start to debug danswer backend
```bash

cd ./backend
mkdir tmp
mkdir tmp/vespa
mkdir tmp/vespa/dynamic_config
mkdir tmp/file_connector

cd ./backend/danswer/document_index/vespa/app_config
zip -r ../vespa-app.zip .
move ./backend/danswer/document_index/vespa/vespa-app.zip ./tmp/vespa/vespa-app.zip
```

config the .env file
```
AUTH_TYPE=google_oauth
SECRET=secret
GOOGLE_OAUTH_CLIENT_ID=xxxxxxxxxxx
GOOGLE_OAUTH_CLIENT_SECRET=xxxxxxxxxxx
VESPA_DEPLOYMENT_ZIP=./tmp/vespa/vespa-app.zip
DYNAMIC_CONFIG_DIR_PATH=./tmp/vespa/dynamic_config
FILE_CONNECTOR_TMP_STORAGE_PATH=./tmp/file_connector
TOKENIZERS_PARALLELISM=false
```

```bash
cd ./backend

# start the danswer backend
python ./danswer/main.py

# start the danswer background sync task
python ./danswer/background/update.py

# start the danswer frontend
cd ./frontend
npm install
npm run dev
```


# ngrok
```bash
ngrok http 3808 --domain=turkey-glowing-firefly.ngrok-free.app 80
```
