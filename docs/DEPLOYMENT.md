# Deployment and clean-checkout verification

## Local

```bash
git clone <repository-url>
cd greenhill_food_coop
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python run.py
```

## Docker

```bash
docker compose up --build
```

Browse to `http://127.0.0.1:8000`.

## Verification

```bash
pytest -q
```

The application creates `data/greenhill.db` on first start and seeds fictional demo users/products.
