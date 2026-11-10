from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Import custom modules
from auth import supabase, verify_token, get_token
import repository
from db import init_db

app = FastAPI(title="Task API", version="1.0")
init_db()

# --- Global Error Handler (Keeps error responses in JSON format) ---
@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


# --- Schemas for Tasks (A3) ---
class TaskCreate(BaseModel):
    title: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# --- Schemas for Auth (A4) ---
class AuthInput(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


# ==========================================
# A3 - TASK ROUTES (Public for now)
# ==========================================

@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    return repository.get_all_tasks(done, search)


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = repository.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/tasks", status_code=201, summary="Create a task")
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    return repository.create_task(payload.title.strip())


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, payload: TaskUpdate):
    current = repository.get_task_by_id(task_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is None and payload.done is None:
        raise HTTPException(status_code=400, detail="Provide at least one of: title, done")
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="title cannot be empty")
    new_title = payload.title.strip() if payload.title is not None else current["title"]
    new_done = payload.done if payload.done is not None else current["done"]
    return repository.update_task(task_id, new_title, new_done)


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    if not repository.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@app.get("/stats", summary="Task counts")
def stats():
    return repository.get_stats()


@app.post("/reset", summary="Reset to the 3 example tasks")
def reset():
    repository.reset_tasks()
    return {"status": "reset"}


# ==========================================
# A4 - AUTHENTICATION ROUTES
# ==========================================

@app.get("/public/info", summary="Public information", tags=["Auth"])
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.post("/auth/signup", status_code=201, summary="Create a new user", tags=["Auth"])
def signup(data: AuthInput):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    try:
        res = supabase.auth.sign_up({"email": data.email, "password": data.password})
        return {"user": res.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", summary="Login and get JWT", tags=["Auth"])
def login(data: AuthInput):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    try:
        res = supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")


@app.get("/protected/profile", summary="Read private profile data", tags=["Protected"])
def get_profile(user=Depends(verify_token)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


@app.get("/protected/dashboard", summary="A second protected route", tags=["Protected"])
def get_dashboard(user=Depends(verify_token)):
    return {
        "message": f"Welcome to your dashboard, {user.email}!"
    }


@app.post("/auth/logout", status_code=204, summary="Logout", tags=["Protected"])
def logout(token: str = Depends(get_token), user=Depends(verify_token)):
    try:
        supabase.auth.admin.sign_out(token)
    except Exception as e:
        # If Supabase admin fails, we still return 204 to the client so they can clear their token
        print(f"Supabase signout warning: {e}")
    return None