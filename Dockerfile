FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY apps ./apps

RUN pip install --no-cache-dir ".[integrations]"

EXPOSE 8088

CMD ["uvicorn", "proofframe.app:app", "--host", "0.0.0.0", "--port", "8088"]
