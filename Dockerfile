FROM python:3.12-slim

WORKDIR /app

LABEL org.opencontainers.image.description="ProofFrame sponsor evidence judge demo"

COPY pyproject.toml README.md ./
COPY src ./src
COPY apps ./apps
COPY tasks.json ./tasks.json
COPY docs/assets ./docs/assets

ARG INSTALL_EXTRAS=""
RUN if [ -n "$INSTALL_EXTRAS" ]; then \
      pip install --no-cache-dir ".[${INSTALL_EXTRAS}]"; \
    else \
      pip install --no-cache-dir .; \
    fi

EXPOSE 8088

CMD ["sh", "-c", "uvicorn proofframe.app:app --host 0.0.0.0 --port ${PORT:-8088}"]
