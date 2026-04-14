# isis_project_unicompass

## Docker

The app is containerized and runs on port `8081` (not `8000`).

Build and run:

```bash
docker compose up --build
```

Open:

- `http://127.0.0.1:8081/` - frontend
- `http://127.0.0.1:8081/docs` - FastAPI docs

Stop:

```bash
docker compose down
```