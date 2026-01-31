from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from nfmer.db_handler import DatabaseHandler, get_db

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="nfmer/api/templates")


@router.get("/", response_class=HTMLResponse, name="index")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/search/", response_class=HTMLResponse, name="search_results")
def search_results(
    request: Request,
    q: str = "",
    type: str = "composers",
    db: DatabaseHandler = Depends(get_db),
):
    if type == "composers":
        results = db.search_composers_by_name(q) if q else []
    else:
        results = db.search_compositions_by_name(q) if q else []
    return templates.TemplateResponse(
        "partials/search_results.html",
        {"request": request, "results": results, "search_type": type, "query": q},
    )


@router.get("/composers/{composer_id}/", response_class=HTMLResponse, name="composer_detail")
def composer_detail(
    request: Request,
    composer_id: int,
    db: DatabaseHandler = Depends(get_db),
):
    composer = db.get_composer_by_id(composer_id)
    if not composer:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Composer not found"},
            status_code=404,
        )
    return templates.TemplateResponse(
        "composer_detail.html",
        {"request": request, "composer": composer},
    )


@router.get("/compositions/{composition_id}/", response_class=HTMLResponse, name="composition_detail")
def composition_detail(
    request: Request,
    composition_id: int,
    db: DatabaseHandler = Depends(get_db),
):
    composition = db.get_composition_by_id(composition_id)
    if not composition:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Composition not found"},
            status_code=404,
        )
    return templates.TemplateResponse(
        "composition_detail.html",
        {"request": request, "composition": composition},
    )
