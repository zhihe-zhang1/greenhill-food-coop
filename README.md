# Greenhill Food Co-op Ordering System — A3 Scrum Edition

A complete runnable Python web application for **ISYS3001 Assessment 3**, continuing the same Greenhill Food Co-op project used for A2. The software is paired with Jira/Scrum evidence rather than replacing it: the team should still create the official Product Backlog, Sprint Backlog, story states, assignments and release records in Jira.

## A3 functionality

Everything in the A2 edition plus:

- Round operational report with sprint/release evidence-friendly metrics.
- Packing completion indicator.
- Downloadable CSV round report.
- Command-line CSV export script.
- Release-readiness page.
- Additional automated tests for reports, packing and access-controlled APIs.
- Jira mapping, project charter, backlog starter, sprint plan, meeting memo, test plan, release plan, review/retrospective, handover and peer-review guidance.

## Run

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
python run.py
```

Open <http://127.0.0.1:8000>.

## Demo accounts

| Role | Login | Password |
|---|---|---|
| Coordinator | `coordinator@greenhill.local` | `Coordinator123!` |
| Packer | `packer@greenhill.local` | `Packer123!` |
| Member | `member@greenhill.local` | `Member123!` |

## Automated tests

```bash
pytest -q
```

## Export a round

```bash
python scripts/export_round.py --round 35 --output round_35.csv
```

## Scrum workflow

Use one Jira project for the team. A typical story flow is:

```text
Product Backlog → Sprint Backlog → In Progress → Review/Test → Done
```

Use one Git branch per Jira story, for example:

```text
feature/GHC-12-packing-sheet
```

The Definition of Done should be enforced through Jira acceptance criteria, automated tests, Pull Request review, successful clean-checkout execution, updated Jira state and recorded decisions.

## A3 support documents

See `docs/` for the project charter, Jira mapping, product backlog starter, sprint plan, meeting memo, test plan, release plan, sprint review/retrospective, handover and peer-review guidance.

These files are starter/evidence documents. Jira and Confluence remain the team's official collaboration records where required by the assessment.
