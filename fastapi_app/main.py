from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app import crud, models, schemas
from app.config import get_config
from app.database import SessionLocal, engine
from app.routers import uploads

models.Base.metadata.create_all(bind=engine)

config = get_config()

config.TRAINING_IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)
config.IMAGE_COLLECTION_FOLDER.mkdir(parents=True, exist_ok=True)
for file in config.TRAINING_IMAGES_FOLDER.glob("*"):
    file.unlink()
for file in config.IMAGE_COLLECTION_FOLDER.glob("*"):
    file.unlink()

app = FastAPI()


app.include_router(uploads.router)


@app.get("/")
async def root():
    content = """
<head>
<title>Upload Images</title>
</head>

<body>
<form action="/uploads/training_images" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploads/collection_images" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
