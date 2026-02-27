# Docker Usage

## Run with Docker Compose

```bash
docker compose up --build
```

App URL: `http://localhost:8501`

`docker-compose.yml` already includes:
- bind mount: `.:/app`
- hot reload: `--server.runOnSave=true` + `--server.fileWatcherType=poll`

## Optional: Docker Compose Watch

```bash
docker compose watch
```

This uses `develop.watch` and syncs file changes to `/app`.

## Run with Docker CLI

```bash
docker build -t excel-analyzer .
docker run --rm -p 8501:8501 --name excel-analyzer excel-analyzer
```

To use bind mount with Docker CLI:

```bash
docker run --rm -p 8501:8501 -v "$(pwd):/app" --name excel-analyzer excel-analyzer
```

## Stop

```bash
docker compose down
```

## Important

If you add/update dependencies in `requirements.txt`, rebuild the image:

```bash
docker compose up --build
```
