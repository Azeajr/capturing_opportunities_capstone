from typing import Any, Iterator

import structlog
from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import get_config
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

    # return {"filenames": [file.filename for file in files]}
    return {
        "data": {
            "type": "modelTraining",
            "attributes": {
                "status": "completed",
            },
        },
        "meta": {
            "message": "Model training completed successfully",
        },
    }


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

    return {
        "data": [
            {
                "type": "imageComparisonResults",
                "attributes": {
                    "imagePath": path,
                    "score": score,
                },
            }
            for path, score in scored_paths
        ],
        "meta": {
            "totalResults": len(scored_paths),
            "modelUsed": settings.MODEL,
            "message": "Image comparison completed successfully",
        },
        "links": {
            "self": str(settings.IMAGE_COLLECTION_FOLDER),
        },
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
