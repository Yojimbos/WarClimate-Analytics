FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY sample_data /app/sample_data
COPY pyproject.toml README.md /app/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh
RUN pip install --upgrade pip && pip install .

USER app

EXPOSE 8000

CMD ["/app/entrypoint.sh"]

