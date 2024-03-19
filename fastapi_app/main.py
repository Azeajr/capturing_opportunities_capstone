from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_config
from app.routers import uploads

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
    "http://localhost:8000", # fastapi
    "http://localhost:3000", # react
    "http://localhost:5173", # svelte
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(uploads.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    content = """
<head>
<title>Upload Images</title>
<script src="static/js/htmx.min.js"></script>
</head>

<body>
<form hx-encoding="multipart/form-data" hx-post="/uploads/training_images" hx-target="#training_output" hx-swap="innerHTML">
    <input name="files" type="file" multiple>
    <input type="submit">
</form>
<div id=training_output style="overflow: auto; height: 30%; width: 90%; border: 1px solid black; margin: 10px; padding: 10px;">
</div>
<form hx-encoding="multipart/form-data" hx-post="/uploads/collection_images" hx-target="#collection_output" hx-swap="innerHTML">
    <input name="files" type="file" multiple>
    <input type="submit">
</form>
<div id="collection_output" style="overflow: auto; height: 30%; width: 90%; border: 1px solid black; margin: 10px; padding: 10px;">
</div>
</body>
    """
    return HTMLResponse(content=content)
