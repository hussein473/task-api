# Task API

A small CRUD API for managing a to-do list, built with FastAPI. Tasks are stored in memory (no database yet) and can be created, read, updated, and deleted through the endpoints below. Comes with interactive Swagger UI documentation for testing everything in the browser.

## How to run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` in your browser to see and test the API, or use `curl` against `http://localhost:8000`.

## Endpoints

| Method | Path            | Description                          |
|--------|-----------------|---------------------------------------|
| GET    | `/`             | API info                              |
| GET    | `/health`       | Health check                          |
| GET    | `/tasks`        | List all tasks (supports `?done=` and `?search=` filters) |
| GET    | `/tasks/{id}`   | Get one task                          |
| POST   | `/tasks`        | Create a task                         |
| PUT    | `/tasks/{id}`   | Update a task                         |
| DELETE | `/tasks/{id}`   | Delete a task                         |
| GET    | `/stats`        | Task counts (total/done/open)         |
| POST   | `/reset`        | Reset to the 3 example tasks          |

## Example request

```
$ curl -i http://localhost:8000/tasks
HTTP/1.1 200 OK
date: Tue, 22 Sep 2026 12:08:28 GMT
server: uvicorn
content-length: 133
content-type: application/json

[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Write README","done":false},{"id":3,"title":"Push to GitHub","done":true}]
```

## Swagger UI

![Swagger UI](swagger.png)

## The mortality experiment

Restarting the server resets all tasks back to the original 3 seed tasks — anything created, updated, or deleted during a session is lost. This is because the data lives only in memory (a Python list), not in a database or file, so nothing survives the process ending. This is the reason a real database gets introduced next week.
