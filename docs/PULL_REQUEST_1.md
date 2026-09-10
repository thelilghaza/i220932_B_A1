# Pull Request #1: Feature / Prediction API & Automated CI Pipeline

**Source Branch:** `feature/prediction-api`  
**Target Branch:** `main`  
**Related Issue / Task:** Assignment 1 — Parts 1 to 15 (Initial API implementation, CI, and Containerization)

---

## Summary
This pull request introduces the initial production-ready implementation of the `student-ml-api` microservice. It establishes a Flask-based inference API supporting `/health` and `/predict` endpoints, an automated unit test suite with `pytest`, a production-hardened multi-stage `Dockerfile` with standard OCI labels, and a dual-workflow GitHub Actions CI/CD setup for PR validation and tag-based release publishing.

---

## Changes
- **API Implementation (`app.py`)**:
  - Implemented `GET /health` returning service health, application name, and version (`1.0.0`).
  - Implemented `POST /predict` accepting `{"value": <number>}` and returning `{"input": <number>, "prediction": <number * 2>}`.
  - Added strict payload validation rejecting missing fields, non-JSON payloads, and non-numeric inputs with HTTP 400.
  - Bound application to host `0.0.0.0` on port `5000` to support containerized network ingress.
- **Automated Testing Suite (`tests/test_app.py`)**:
  - Implemented automated tests covering health check schema, valid prediction, missing payload keys, string inputs, and boolean edge cases.
  - Configured test fixture with Flask `test_client` for isolated test runs.
- **Containerization (`Dockerfile`, `.dockerignore`)**:
  - Pinned base image to `python:3.11-slim` (explicit non-latest version).
  - Enforced optimal layer ordering (`COPY requirements.txt` prior to application code) for Docker cache reuse.
  - Added OCI metadata labels (`org.opencontainers.image.*`) for build traceability.
  - Excluded development and virtual environment files via `.dockerignore`.
- **Continuous Integration (`.github/workflows/ci.yml`)**:
  - Configured pipeline on `pull_request` targeting `main`.
  - Runs checkout, Python 3.11 setup, dependency installation, pytest suite, and Docker build check.
  - Does **not** publish images to registry (PR validation only).
- **Automated Release Workflow (`.github/workflows/release.yml`)**:
  - Configured pipeline triggered only on semantic tags (`v*.*.*`).
  - Automatically derives semantic version without hardcoding.
  - Authenticates to GitHub Container Registry (GHCR) and publishes versioned, latest, and commit SHA tags.

---

## Testing Performed
- **Unit Tests**: Executed `pytest -v tests/test_app.py` locally — 5/5 tests passed in 0.13s.
- **Local Container Verification**:
  - Built image: `docker build -t student-ml-api:1.0.0 .`
  - Ran container: `docker run -d --name student-ml-api -p 5000:5000 student-ml-api:1.0.0`
  - Queried `GET /health`: returned HTTP 200 `{"application":"student-ml-api","status":"healthy","version":"1.0.0"}`
  - Queried `POST /predict` with `{"value": 10}`: returned HTTP 200 `{"input":10,"prediction":20}`
- **Deliberate Failure Validation (Part 6)**:
  - Injected deliberate test failure (`assert data["status"] == "wrong"`).
  - Verified CI fails as expected.
  - Reverted failure with `fix: correct health endpoint test`.

---

## Docker Impact
- **Base Image:** `python:3.11-slim` (Debian Bookworm base, ~130MB, minimal attack surface).
- **Layer Optimization:** Dependency installation cached across source code modifications.
- **Ports:** Exposes port `5000` directly.
- **Environment:** Production container runtime without development tools or test caches.

---

## Checklist
- [x] Application runs locally
- [x] Tests pass locally (`pytest`)
- [x] Docker image builds successfully
- [x] No credentials are committed
- [x] API health endpoint works
- [x] Code is ready for review
