from typing import Any, Iterator

from fastapi.responses import FileResponse
import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import get_config
from app.database import SessionLocal, engine
from app.services.auto_encoder import AutoEncoder
from app.services.base import MlABC
from app.services.svm import SVM

settings = get_config()

log = structlog.get_logger()

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    responses={404: {"description": "Not found"}},
)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

if settings.MODEL == "auto_encoder":
    ml: MlABC = AutoEncoder()
else:
    ml: MlABC = SVM()


@router.post("/training_images")
async def upload_training_images(files: list[UploadFile], request: Request):
    log.info("request", url=request.url, method=request.method, headers=request.headers)

    for image in files:
        image_path = settings.TRAINING_IMAGES_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    ml.process_training_images(settings.TRAINING_IMAGES_FOLDER)

    return {"filenames": [file.filename for file in files]}


@router.post("/collection_images")
# async def upload_collection_images(files: list[UploadFile], db: Session = Depends(get_db)):
async def upload_collection_images(files: list[UploadFile]):
    for image in files:
        image_path = settings.IMAGE_COLLECTION_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    scored_paths: Iterator[tuple[str, Any]] = ml.process_collection_images(
        settings.IMAGE_COLLECTION_FOLDER
    )

    scored_paths = list(scored_paths)

    # for path, score in scored_paths:
    #     scored_path = schemas.ScoredPathCreate(path=path, score=score)
    #     db_scored_path = crud.create_scored_path(db, scored_path=scored_path)
    

    return {
        "filenames": [file.filename for file in files],
        "scored_paths": scored_paths,
    }


@router.get("/<folder>/<filename>")
async def get_image(folder: str, filename: str):
    if folder == "training_images":
        image_path = settings.TRAINING_IMAGES_FOLDER / filename
    elif folder == "collection_images":
        image_path = settings.IMAGE_COLLECTION_FOLDER / filename
    else:
        raise HTTPException(status_code=404, detail="Folder not found")

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(image_path))

# @router.get("/users/", tags=["users"])
# async def read_users():
#     return [{"username": "Rick"}, {"username": "Morty"}]


# @router.get("/users/me", tags=["users"])
# async def read_user_me():
#     return {"username": "fakecurrentuser"}


# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}
