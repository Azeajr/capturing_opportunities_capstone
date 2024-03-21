import structlog
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import get_config

config = get_config()

log = structlog.get_logger()

router = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{model_name}/{uuid}/{filename}")
async def get_model(model_name: str, uuid: str, filename: str):
    model_path = config.MODELS_FOLDER / model_name / uuid / filename

    if not model_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(model_path))
