FROM python:3.12-slim

# Required for PDF and image parsing in unstructured:
# - libgl1, libglib2.0-0: needed by OpenCV (cv2) for layout detection models
# - tesseract-ocr, poppler-utils: OCR and PDF rendering for scanned documents
# - libmagic1, file: MIME type detection (used by unstructured)
# - gcc, g++, make: build tools (needed by some packages or when installing from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc \
    g++ \
    make \
    libmagic1 \
    file \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml .env.example ./

RUN cp -n .env.example .env || true

ENV UV_HTTP_TIMEOUT=120

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /home/appuser/.cache/uv /home/appuser/nltk_data && \
    chown -R appuser:appuser /app /home/appuser

RUN uv venv && \
    uv pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .

COPY classifier/ ./classifier/
COPY main.py api.py settings.py ./

COPY documents/ ./documents/

RUN mkdir -p output && chown -R appuser:appuser output

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

USER appuser
RUN python -c "import nltk; nltk.download('punkt', download_dir='/home/appuser/nltk_data')"

EXPOSE 5000

ENV NLTK_DATA=/home/appuser/nltk_data

CMD ["python", "api.py"]