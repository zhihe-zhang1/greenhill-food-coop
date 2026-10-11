# Configuration management notes

## Controlled artefacts

- Python source under `app/`
- HTML/CSS/JS under `app/templates` and `app/static`
- dependency list in `requirements.txt`
- environment example in `.env.example`
- Docker configuration
- automated tests
- CI workflow
- README and change log

## Environment strategy

`APP_SECRET` and database path come from environment variables. Real secrets and runtime databases are ignored by Git. The repository contains only `.env.example` with illustrative values.

## Data/configuration strategy

SQLite provides a zero-service local development database. The database is generated from schema code, and demo content can be recreated with `scripts/reset_db.py`, so no developer-specific database file is required in Git.

## Price history rule

When a round is created, each active product and its current base price are copied into `round_products`. Updating a product price later changes future rounds only, preserving historical prices for existing orders.
