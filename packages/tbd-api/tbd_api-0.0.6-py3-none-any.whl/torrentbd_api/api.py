import pathlib
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .active import get_online_users
from .profile import get_user_profile
from .schema import OnlineUsersResponse
from .search import search_torrents
from .version import __version__

app = FastAPI(
    title="TorrentBD API",
    version=__version__,
    description="Unofficial API for TorrentBD",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage() -> FileResponse:
    """Serve the HTML homepage"""
    html_file = static_dir / "index.html"
    return FileResponse(html_file)


@app.get("/api")
def root() -> dict[str, Any]:
    return {
        "info": {
            "title": "TorrentBD API",
            "version": __version__,
            "description": "Unofficial API for TorrentBD",
        },
        "endpoints": {
            "search": {
                "path": "/search",
                "method": "GET",
                "description": "Search for torrents on TorrentBD",
            },
            "profile": {
                "path": "/profile",
                "method": "GET",
                "description": "Get user profile information",
            },
            "online": {
                "path": "/online",
                "method": "GET",
                "description": "Get the list of online users",
            },
        },
        "documentation": {"swagger": "/docs", "redoc": "/redoc"},
    }


@app.get("/search")
def search(
    query: str = Query(..., description="Search term"), page: int = 1
) -> dict[str, Any]:
    """Search for torrents on TorrentBD."""
    result = search_torrents(query, page)
    return {"result": result}


@app.get("/profile")
def profile() -> dict[str, Any]:
    """Get user profile information."""
    result = get_user_profile()
    return {"result": result}


@app.get("/online", response_model=OnlineUsersResponse)
def list_online_users() -> OnlineUsersResponse:
    """Get the list of online users."""
    users = get_online_users()
    return OnlineUsersResponse(count=len(users), users=users)
