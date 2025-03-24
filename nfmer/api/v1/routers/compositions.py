from fastapi import APIRouter, Depends, HTTPException

from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import CompositionPublic, CompositionPublicFull

router = APIRouter(prefix="/compositions", tags=["compositions"])


@router.get("/", response_model=list[CompositionPublic])
def get_compositions(search_term: str = None, db: DatabaseHandler = Depends(get_db)) -> list[CompositionPublic]:
    if search_term:
        return db.search_compositions_by_name(search_term)
    else:
        return db.get_all_compositions()


@router.get("/{composition_id}", response_model=CompositionPublicFull)
def get_composition(composition_id: int, db: DatabaseHandler = Depends(get_db)):
    composition = db.get_composition_by_id(composition_id)
    if not composition:
        raise HTTPException(status_code=404, detail="Composition not found")
    return composition
