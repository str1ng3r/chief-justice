FROM python:3.11.2-slim-buster as builder-image

ENV POETRY_VERSION="1.4.1"

COPY pyproject.toml poetry.lock ./

RUN pip install "poetry==$POETRY_VERSION" & python -m venv /venv

RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin


FROM python:3.11.2-slim-buster as runner-image

COPY --from=builder-image /venv /venv

WORKDIR /app

COPY . .

ENV VIRTUAL_ENV="/venv"
ENV PATH="/venv/bin:${PATH}"

ENTRYPOINT ["python3", "main.py"]