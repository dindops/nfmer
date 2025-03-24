from fastapi import APIRouter, Depends, HTTPException

from nfmer.db_handler import DatabaseHandler, get_db
from nfmer.models import ComposerPublic, ComposerPublicFull

router = APIRouter(prefix="/composers", tags=["composers"])


@router.get("/", response_model=list[ComposerPublic])
def get_composers(search_term: str = None, db: DatabaseHandler = Depends(get_db)) -> list[ComposerPublic]:
    if search_term:
        return db.search_composers_by_name(search_term)
    else:
        return db.get_all_composers()


@router.get("/{composer_id}", response_model=ComposerPublicFull)
def get_composer(composer_id: int, db: DatabaseHandler = Depends(get_db)) -> ComposerPublicFull:
    composer = db.get_composer_by_id(composer_id)
    if not composer:
        raise HTTPException(status_code=404, detail="Composer not found")
    return composer
