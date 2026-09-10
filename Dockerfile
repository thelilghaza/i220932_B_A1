FROM python:3.11-slim

WORKDIR /app

ARG VERSION="1.0.0"
ARG COMMIT_SHA="unknown"
ARG BUILD_DATE=""

LABEL org.opencontainers.image.title="student-ml-api" \
      org.opencontainers.image.description="ML inference service for student prediction API" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${COMMIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.authors="thelilghaza" \
      org.opencontainers.image.source="https://github.com/thelilghaza/i220932_B_A1"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VERSION .
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
