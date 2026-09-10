# Part 26 — Failure Analysis Report

This document records the deliberate reproduction, diagnosis, evidence, and corrective action for three failure modes as mandated by Part 26 of the assignment rubric.

---

## Failure Mode 1: Failed Pytest Suite in CI Pipeline

### 1. Symptom
During Pull Request validation on GitHub Actions (or during local verification), the CI job `ci-pipeline` fails abruptly at step `Unit Tests (Pytest)` with exit code 1. The Pull Request check reports red (`FAILED`), blocking the merge.

### 2. Root Cause
An assertion failure in `tests/test_app.py` where expected response values differed from actual returned values:
```python
assert data["status"] == "wrong"
```
Because `data["status"]` is `"healthy"`, Python evaluates the assertion to `False` and raises an unhandled `AssertionError`, causing `pytest` to exit with code 1.

### 3. Evidence

![GitHub Actions CI Failed Check](screenshots/part6_ci_failed.png)

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/thelilghaza/MLOps/i220932_B_A1
collected 5 items

tests/test_app.py::test_health_endpoint FAILED                           [ 20%]
tests/test_app.py::test_predict_success PASSED                           [ 40%]
tests/test_app.py::test_predict_missing_input PASSED                     [ 60%]
tests/test_app.py::test_predict_invalid_input PASSED                     [ 80%]
tests/test_app.py::test_predict_boolean_input PASSED                     [100%]

=================================== FAILURES ===================================
_____________________________ test_health_endpoint _____________________________
client = <FlaskClient <Flask 'app'>>

    def test_health_endpoint(client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
>       assert data["status"] == "wrong"
E       AssertionError: assert 'healthy' == 'wrong'

tests/test_app.py:18: AssertionError
=========================== short test summary info ============================
FAILED tests/test_app.py::test_health_endpoint - AssertionError: assert 'healthy' == 'wrong'
========================= 1 failed, 4 passed in 0.15s ==========================
```

### 4. Correction
1. Correct the invalid test assertion in `tests/test_app.py`:
   ```python
   assert data["status"] == "healthy"
   ```
2. Commit the fix with a conventional commit message:
   ```bash
   git commit -m "fix: correct health endpoint test"
   git push origin feature/prediction-api
   ```
3. Re-running `pytest` yields 5/5 passed, and the CI status turns green (`SUCCESS`):

   ![GitHub Actions CI Passed Check](screenshots/part6_ci_passed.png)

---

## Failure Mode 2: Application Bound to `127.0.0.1` (Container Loopback Isolation)

### 1. Symptom
The Docker container starts without errors and `docker ps` reports status `Up`. However, attempting to reach the API from the host machine via `curl http://localhost:5000/health` immediately fails with:
`curl: (56) Recv failure: Connection reset by peer` or `curl: (52) Empty reply from server`.

### 2. Root Cause
In `app.py`, the Flask application was started with:
```python
app.run(host="127.0.0.1", port=5000)
```
Inside a Linux network namespace (which Docker creates for each container), `127.0.0.1` binds solely to the loopback interface (`lo`). Docker's bridge network directs incoming forwarded packets from the host (`0.0.0.0:5000`) to the container's virtual ethernet interface (`eth0`, e.g., `172.17.0.4`). Because no application is listening on `eth0:5000`, the container's kernel network stack rejects the incoming SYN packets or resets the connection.

### 3. Evidence
```text
$ docker run -d --name test-bound-127 -p 5005:5000 student-ml-api:1.0.0 \
    python -c "from flask import Flask; app=Flask('x'); app.add_url_rule('/health', 'h', lambda: 'ok'); app.run(host='127.0.0.1', port=5000)"
7cc338ef606b8c2ef8035d91255ab60c04834dd5b21cd5abbdc424c8dc32ec92

$ curl -i http://localhost:5005/health
curl: (56) Recv failure: Connection reset by peer
```

### 4. Correction
1. Configure Flask to bind to `0.0.0.0` (`INADDR_ANY`), allowing the socket to accept connections on all network interfaces including `eth0`:
   ```python
   if __name__ == "__main__":
       app.run(host="0.0.0.0", port=5000)
   ```
2. After rebuilding and running with `host="0.0.0.0"`, `curl http://localhost:5000/health` returns HTTP 200 OK with the full payload.

---

## Failure Mode 3: Missing Module Dependency at Import Time

### 1. Symptom
The application crashes immediately during startup with `ModuleNotFoundError: No module named 'flask'` or pytest execution crashes with:
`ModuleNotFoundError: No module named 'app'`.

### 2. Root Cause
1. In Python virtual environments, if dependencies listed in `requirements.txt` are omitted or the PYTHONPATH does not include the project root, the Python runtime cannot locate the package inside `site-packages` or `sys.path`.
2. Specifically, when `pytest` executes from a subdirectory or without editable install, the current working directory might not be in `sys.path`.

### 3. Evidence
```text
ImportError while importing test module '/home/thelilghaza/MLOps/i220932_B_A1/tests/test_app.py'.
tests/test_app.py:2: in <module>
    from app import app
E   ModuleNotFoundError: No module named 'app'
=========================== short test summary info ============================
ERROR tests/test_app.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

### 4. Correction
1. Add explicit repository path resolution to `tests/test_app.py`:
   ```python
   import sys, os
   sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
   ```
2. Ensure `requirements.txt` explicitly locks dependencies:
   ```text
   flask>=3.0.0
   pytest>=8.0.0
   ```
3. In Dockerfile, ensure `COPY requirements.txt .` and `RUN pip install --no-cache-dir -r requirements.txt` execute prior to copying source code.
