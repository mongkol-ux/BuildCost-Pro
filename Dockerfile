FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY apps/api/requirements.txt ./apps/api/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r apps/api/requirements.txt \
    && useradd --create-home --uid 10001 appuser

COPY apps/api/src ./apps/api/src
COPY apps/api/migrations ./apps/api/migrations

RUN chown -R appuser:appuser /app
USER appuser

WORKDIR /app/apps/api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
