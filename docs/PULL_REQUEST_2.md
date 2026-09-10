# Pull Request #2: Feature / Model Metadata & Release v1.1.0

**Source Branch:** `feature/model-metadata`  
**Target Branch:** `main`  
**Related Issue / Task:** Assignment 1 — Parts 18 to 21 (Model metadata iteration and version 1.1.0 release)

---

## Summary
This pull request updates the `student-ml-api` microservice to version `1.1.0`. It enriches the `/health` endpoint response with model metadata (`model_version: "model-1"` and `application_version: "1.1.0"`), updates the test suite, and bumps the release version in `VERSION`.

---

## Changes
- **API Health Endpoint Update (`app.py`)**:
  - Updated `GET /health` endpoint response payload:
    ```json
    {
      "status": "healthy",
      "application": "student-ml-api",
      "application_version": "1.1.0",
      "model_version": "model-1"
    }
    ```
- **Version Descriptor (`VERSION`)**:
  - Bumped version from `1.0.0` to `1.1.0`.
- **Test Suite Updates (`tests/test_app.py`)**:
  - Updated `test_health_endpoint()` assertions to validate `application_version` and `model_version`.
  - Maintained complete regression coverage for `/predict` endpoint.

---

## Testing Performed
- **Automated Tests**: Executed `pytest -v tests/test_app.py` — all 5 test cases passing.
- **Docker Validation**:
  - Built image locally: `docker build -t student-ml-api:1.1.0 .`
  - Validated `/health` response:
    ```bash
    curl http://localhost:5000/health
    # Output: {"application":"student-ml-api","application_version":"1.1.0","model_version":"model-1","status":"healthy"}
    ```

---

## Docker Impact
- Reused cached Python runtime and dependency layers (`pip install`).
- Layer build time: ~0.5s due to cache hit.
- Image size remains identical.

---

## Checklist
- [x] Application runs locally
- [x] Tests pass locally
- [x] Docker image builds successfully
- [x] No credentials are committed
- [x] API health endpoint works
- [x] Code is ready for review
