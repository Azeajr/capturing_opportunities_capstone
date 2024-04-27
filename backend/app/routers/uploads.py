import shutil
from typing import Any, Iterator
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile

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


@router.get("/session")
async def get_session_id():
    return {"data": {"type": "sessionId", "attributes": {"sessionId": str(uuid4())}}}


@router.post("/training_images/{session_id}")
async def upload_training_images_with_model_name(
    session_id: str,
    file: UploadFile,
    request: Request,
    response: Response,
):
    log.info("request", url=request.url, method=request.method, headers=request.headers)

    upload_path = config.SESSIONS_FOLDER / session_id / "training_images" / "raw"
    upload_path.mkdir(parents=True, exist_ok=True)

    image_path = upload_path / file.filename
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    response.headers["X-Session-Id"] = session_id
    return {
        "data": {
            "type": "uploadResults",
            "attributes": {
                "sessionId": session_id,
                "status": "completed",
            },
        },
        "meta": {
            "message": "Training image uploaded successfully",
        },
    }


@router.get("/training_images/{session_id}/{model_name}")
async def start_training_with_model_name(
    session_id: str,
    model_name: str,
    request: Request,
    response: Response,
):
    match model_name:
        case "auto_encoder":
            model: MlABC = AutoEncoder(session_id=session_id)
        case "svm":
            model: MlABC = SVM(session_id=session_id)
        case _:
            raise HTTPException(status_code=404, detail="Model not found")

    log.info("request", url=request.url, method=request.method, headers=request.headers)

    upload_path = config.SESSIONS_FOLDER / session_id / "training_images" / "raw"
    upload_path.mkdir(parents=True, exist_ok=True)

    model_path = model.process_training_images(upload_path)

    response.headers["X-Session-Id"] = session_id
    return {
        "data": {
            "type": "trainingResults",
            "attributes": {
                "sessionId": session_id,
                "status": "completed",
                "collectionApiEndpoint": f"/uploads/collection_images{model_path}",
            },
        },
        "meta": {
            "message": "Training image uploaded successfully",
        },
    }


@router.post("/collection_images/{session_id}")
async def upload_collection_images(
    session_id: str, file: UploadFile, response: Response
):
    upload_path = config.SESSIONS_FOLDER / session_id / "collection_images"
    upload_path.mkdir(parents=True, exist_ok=True)

    image_path = upload_path / file.filename
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    response.headers["X-Session-Id"] = session_id
    return {
        "data": {
            "type": "uploadResults",
            "attributes": {
                "sessionId": session_id,
                "status": "completed",
            },
        },
        "meta": {
            "message": "Collection image uploaded successfully",
        },
    }


@router.get("/collection_images/{session_id}/{model_name}")
async def start_collection_image_processing_with_model_name(
    session_id: str, model_name: str, response: Response
):
    match model_name:
        case "auto_encoder":
            model: MlABC = AutoEncoder(session_id=session_id, is_training=False)
        case "svm":
            model: MlABC = SVM(session_id=session_id, is_training=False)
        case _:
            raise HTTPException(status_code=404, detail="Model not found")

    upload_path = config.SESSIONS_FOLDER / session_id / "collection_images"
    scored_paths: Iterator[tuple[str, Any]] = model.process_collection_images(
        upload_path
    )
    shutil.rmtree(config.SESSIONS_FOLDER / session_id, ignore_errors=True)

    scored_paths = list(scored_paths)

    response.headers["X-Session-Id"] = session_id
    response.headers["X-Image-Count"] = str(len(scored_paths))

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
            "sessionId": session_id,
            "totalResults": len(scored_paths),
            "modelUsed": model_name,
            "message": "Image comparison completed successfully",
        },
        "links": {
            "self": str(upload_path),
        },
    }
