from fastapi import APIRouter

router = APIRouter()

@router.get("/", response_model=dict)
async def read_root() -> dict:
    return {"message": "Aspect-Based Review Analyzer API"}
