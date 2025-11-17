from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .api import complaints, documents, auth # Import auth router
from .db import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db() # Initialize database on startup

app.include_router(auth.router, prefix="/api/auth") # Include auth router
app.include_router(complaints.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

# Serve static files from the "frontend" directory
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())