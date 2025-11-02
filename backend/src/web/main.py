from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, JSONResponse
from src.web.api.v1.api import api_router

app = FastAPI(
    title="FastAPI", 
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/healthz")
def health_check() -> str:
    return "Healthy!"


@app.get("/")
def root() -> str:
    return "Welcome to the investment lens portal!"