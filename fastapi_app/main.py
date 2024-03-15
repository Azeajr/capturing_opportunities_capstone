from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(uploads.router)


@app.get("/")
async def root():
    content = """
<head>
<title>Upload Images</title>
<script src="/static/js/htmx.min.js"></script>
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
