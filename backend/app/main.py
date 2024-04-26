import shutil
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_config
from app.logger import setup_logging
from app.middleware import TimingAndLoggingMiddleware
from app.routers import models, uploads

config = get_config()


shutil.rmtree(config.UPLOADS_FOLDER, ignore_errors=True)
shutil.rmtree(config.MODELS_FOLDER, ignore_errors=True)
config.UPLOADS_FOLDER.mkdir(parents=True, exist_ok=True)
config.MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
config.ANALYTICS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

setup_logging()


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",  # fastapi
    "http://localhost:3000",  # react
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TimingAndLoggingMiddleware)


app.include_router(uploads.router)
app.include_router(models.router)

static_folder = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=static_folder), name="static")


@app.get("/")
async def root():
    content = """
<head>
  <title>Upload Images</title>
  <script src="static/js/htmx.min.js"></script>
</head>

<body>
  <form
    hx-encoding="multipart/form-data"
    hx-post="/uploads/training_images"
    hx-target="#training_output"
    hx-swap="innerHTML"
  >
    <input name="files" type="file" multiple />
    <input type="submit" />
  </form>
  <div
    id="training_output"
    style="
      overflow: auto;
      height: 30%;
      width: 90%;
      border: 1px solid black;
      margin: 10px;
      padding: 10px;
    "
  ></div>
  <form
    hx-encoding="multipart/form-data"
    hx-post="/uploads/collection_images"
    hx-target="#collection_output"
    hx-swap="innerHTML"
  >
    <input name="files" type="file" multiple />
    <input type="submit" />
  </form>
  <div
    id="collection_output"
    style="
      overflow: auto;
      height: 30%;
      width: 90%;
      border: 1px solid black;
      margin: 10px;
      padding: 10px;
    "
  ></div>
</body>

    """
    return HTMLResponse(content=content)


@app.get("/{model}")
async def dynamic_model_interface(model: str):
    if model not in ["auto_encoder", "svm"]:
        return {"error": "Model not found"}
    javascript = """
<script>
document.addEventListener("DOMContentLoaded", function (event) {
  console.log("DOM fully loaded and parsed");
  document
    .getElementById("training_output")
    .addEventListener("htmx:afterSwap", function (evt) {
      console.log("htmx:afterSwap event fired");
      try {
        var responseJson = JSON.parse(this.innerText); // Assuming the server response is correctly formatted JSON
        this.innerText = JSON.stringify(responseJson, null, 2);

        var collectionApiEndpoint =
          responseJson.data.attributes.collectionApiEndpoint;
        var newAction = collectionApiEndpoint;
        console.log("New hx-post URL:", newAction);
        // Ensure the form selector accurately matches your form
        var formToUpdate = document.querySelector(
          'form[hx-post="/uploads/collection_images"]'
        );
        if (formToUpdate) {
          formToUpdate.setAttribute("hx-post", newAction);
          console.log("hx-post attribute updated successfully");
          htmx.process(formToUpdate); // Re-process the form to update the action attribute
        } else {
          console.log("Form not found with the specified hx-post attribute");
        }
      } catch (error) {
        console.error(
          "Error parsing JSON response or updating hx-post attribute:",
          error
        );
      }
    });

  document
    .getElementById("collection_output")
    .addEventListener("htmx:afterSwap", function (evt) {
      console.log("htmx:afterSwap event fired");
      try {
        var responseJson = JSON.parse(this.innerText); // Assuming the server response is correctly formatted JSON
        this.innerText = JSON.stringify(responseJson, null, 2);
      } catch (error) {
        console.error(
          "Error parsing JSON response or updating hx-post attribute:",
          error
        );
      }
    });
});
</script>
"""

    content = f"""
<head>
  <title>Upload Images</title>
  <script src="static/js/htmx.min.js"></script>
  {javascript}
</head>
<body>
  <form
    hx-encoding="multipart/form-data"
    hx-post="/uploads/training_images/{model}"
    hx-target="#training_output"
    hx-swap="innerHTML"
  >
    <input name="files" type="file" multiple />
    <input type="submit" />
  </form>
  <pre
    id="training_output"
    style="
      overflow: auto;
      height: 30%;
      width: 90%;
      border: 1px solid black;
      margin: 10px;
      padding: 10px;
    "
  ></pre>
  <form
    hx-encoding="multipart/form-data"
    hx-post="/uploads/collection_images"
    hx-target="#collection_output"
    hx-swap="innerHTML"
  >
    <input name="files" type="file" multiple />
    <input type="submit" />
  </form>
  <pre
    id="collection_output"
    style="
      overflow: auto;
      height: 30%;
      width: 90%;
      border: 1px solid black;
      margin: 10px;
      padding: 10px;
    "
  ></pre>
</body>
    """
    return HTMLResponse(content=content)
