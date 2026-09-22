# Configuration Management

## Purpose

This document records the configuration-management approach used for the Greenhill Food Co-op project.

## Repository and branches

The source repository is managed in GitHub.

- `main` is the stable branch.
- `feature/zhihe-zhang` is the Assessment 2 development branch.
- Assessment 3 work can use Jira story branches such as `feature/MSD426GXUST34-5-place-order`.

Development changes are committed in small functional groups instead of one final bulk commit. Pull requests are used before work is merged into `main`.

## Configuration items

The main configuration items are:

| Item | Purpose |
| --- | --- |
| `.env.example` | Documents supported application environment variables |
| `.gitignore` | Prevents local environments, databases, secrets and editor files from being committed |
| `requirements.txt` | Pins the Python dependency ranges used by the application |
| `.github/workflows/tests.yml` | Runs automated tests for feature pushes and pull requests |
| `Dockerfile` | Defines the application container image |
| `docker-compose.yml` | Defines repeatable local deployment and persistent data volume |
| `docs/DEPLOYMENT.md` | Records deployment and health-check steps |
| `CHANGELOG.md` | Records functional changes by project version |

## Environment configuration

The application uses environment variables for application name, session secret, database path and debug mode. A sample file is provided as `.env.example`.

Sensitive or machine-specific values must not be committed in a real `.env` file. The repository ignores `.env` and local SQLite database files.

## Version control

Commit messages use a short type and description, for example:

```text
feat: add member ordering workflow
test: add automated application tests
ci: add automated test workflow
chore: add docker deployment configuration
```

The commit history separates configuration, database, authentication, service, coordinator, member, packing, test, CI and deployment changes so that changes can be reviewed independently.

## Automated verification

Local automated tests are run with:

```bash
pytest -q
```

GitHub Actions runs the same automated tests for pushes to `main` and `feature/**`, and for pull requests targeting `main`.

The tests cover password handling, HTTP access, order rules and both unit-based and weight-based pricing.

## Deployment configuration

The repository contains Docker deployment configuration.

```bash
docker compose up --build
```

The application health endpoint is:

```text
/api/health
```

Deployment details are maintained in `docs/DEPLOYMENT.md`.

## Change control

Changes follow this sequence:

```text
change identified
→ development branch
→ implementation
→ local test
→ commit and push
→ automated CI
→ pull request
→ review
→ merge to main
→ release/tag when appropriate
```

If a defect or configuration issue is found, the correction is recorded as a separate commit rather than rewriting previous history.

## Backup and recovery

GitHub provides the remote source repository. Local application data is stored in SQLite under `data/`; the Docker Compose configuration mounts this directory outside the container so it survives container recreation.

For a real deployment, database backups should be taken independently of the application container.

## Current Assessment 2 status

Completed configuration-management items include structured commits, feature branching, environment configuration, dependency management, automated tests, GitHub Actions and Docker deployment configuration.

The pull request, review/merge evidence and final release/tag are completed later in the workflow and should be captured separately as evidence.
