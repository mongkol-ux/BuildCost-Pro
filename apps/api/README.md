# BuildCost Pro API

## Run locally

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Health endpoint: `GET /health`

## Test

```bash
cd apps/api
pytest
```
