FROM python:3.13-slim
ENV POETRY_VIRTUAL_ENVS_CREATE=false

WORKDIR backend/
COPY . .

RUN pip install poetry
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi
RUN poetry install

EXPOSE 8000
CMD poetry run fastapi run backend/app.py --host 0.0.0.0