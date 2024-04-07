FROM python:3.11-slim AS base

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml  ./poetry.lock /tmp/

RUN poetry export -f requirements.txt --output requirements.txt

FROM python:3.11-slim

WORKDIR /code

COPY --from=base /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# ENTRYPOINT ["uvicorn", "app.main:app",  "--host=0.0.0.0", "--port=8000" ]
CMD ["uvicorn", "app.main:app",  "--host","0.0.0.0", "--port", "8000"]