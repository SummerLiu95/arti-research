FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY migrations/ migrations/
COPY pipeline/ pipeline/
COPY api/ api/
COPY scripts/bootstrap.sh scripts/bootstrap.sh
RUN chmod +x scripts/bootstrap.sh

EXPOSE 8000
CMD ["sh", "scripts/bootstrap.sh"]
