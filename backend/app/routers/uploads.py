from pathlib import Path
from typing import Any, Iterator

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.auth import verify_api_key
from app.config import get_config
from app.services.auto_encoder import AutoEncoder
from app.services.base import MlABC
from app.services.svm import SVM

config = get_config()

log = structlog.get_logger()

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    dependencies=[Depends(verify_api_key)],
)


if config.MODEL == "auto_encoder":
    ml: MlABC = AutoEncoder()
else:
    ml: MlABC = SVM()


@router.post("/training_images")
async def upload_training_images(files: list[UploadFile], request: Request):
    log.info("request", url=request.url, method=request.method, headers=request.headers)

    for image in files:
        image_path = config.TRAINING_IMAGES_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    model_path = ml.process_training_images(config.TRAINING_IMAGES_FOLDER)

    return {
        "data": {
            "type": "modelTraining",
            "attributes": {
                "status": "completed",
                "modelUuid": model_path.parent.name if model_path else None,
                "modelApiEndpoint": model_path,
            },
        },
        "meta": {
            "message": "Model training completed successfully",
        },
    }


@router.post("/training_images/{model_name}")
async def upload_training_images_with_model_name(
    model_name: str, files: list[UploadFile], request: Request
):
    match model_name:
        case "auto_encoder":
            model: MlABC = AutoEncoder()
        case "svm":
            model: MlABC = SVM()
        case _:
            raise HTTPException(status_code=404, detail="Model not found")

    log.info("request", url=request.url, method=request.method, headers=request.headers)

    for image in files:
        image_path = config.TRAINING_IMAGES_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    model_path = model.process_training_images(config.TRAINING_IMAGES_FOLDER)

    return {
        "data": {
            "type": "modelTraining",
            "attributes": {
                "status": "completed",
                "modelName": model_name,
                "modelUuid": model_path.parent.name if model_path else None,
                "modelApiEndpoint": f"/models{model_path}",
                "collectionApiEndpoint": f"/uploads/collection_images{model_path}",
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
        image_path = config.IMAGE_COLLECTION_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    scored_paths: Iterator[tuple[str, Any]] = ml.process_collection_images(
        config.IMAGE_COLLECTION_FOLDER
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
            "modelUsed": config.MODEL,
            "message": "Image comparison completed successfully",
        },
        "links": {
            "self": str(config.IMAGE_COLLECTION_FOLDER),
        },
    }


@router.post("/collection_images/{model_name}/{model_path}/{filename}")
# async def upload_collection_images(files: list[UploadFile], db: Session = Depends(get_db)):
async def upload_collection_images_with_model_uuid(
    model_name: str, model_path: Path, filename: Path, files: list[UploadFile]
):
    match model_name:
        case "auto_encoder":
            model: MlABC = AutoEncoder(model_path=model_path / filename)
        case "svm":
            model: MlABC = SVM(model_path=model_path / filename)
        case _:
            raise HTTPException(status_code=404, detail="Model not found")

    for image in files:
        image_path = config.IMAGE_COLLECTION_FOLDER / image.filename

        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

    scored_paths: Iterator[tuple[str, Any]] = model.process_collection_images(
        config.IMAGE_COLLECTION_FOLDER
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
            "modelUsed": model_name,
            "message": "Image comparison completed successfully",
        },
        "links": {
            "self": str(config.IMAGE_COLLECTION_FOLDER),
        },
    }


@router.get("/{folder}/{filename}")
async def get_image(folder: str, filename: str, request: Request):
    log.info("request", url=request.url, method=request.method, headers=request.headers)
    if folder == "training_images":
        image_path = config.TRAINING_IMAGES_FOLDER / filename
    elif folder == "collection_images":
        image_path = config.IMAGE_COLLECTION_FOLDER / filename
    else:
        raise HTTPException(status_code=404, detail="Folder not found")

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(image_path))
