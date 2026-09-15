FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY src/backend/requirements.txt ./src/backend/requirements.txt
RUN pip install --no-cache-dir -r src/backend/requirements.txt

# Copy the full source tree so src.backend.* imports resolve correctly
COPY src/ ./src/

# Expose data directory (populated via volume mount in docker-compose)
# /app/src/data will be used by _find_data_dir() as the "sibling" path;
# /app/data is also checked when volume-mounted.

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "python src/backend/db_init.py && uvicorn src.backend.main:app --host 0.0.0.0 --port 8000"]
