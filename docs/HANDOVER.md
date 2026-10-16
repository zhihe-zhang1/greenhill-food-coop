# Handover

**Project:** Greenhill Food Co-op Ordering System
**Repository:** https://github.com/zhihe-zhang1/greenhill-food-coop
**Release handed over:** v1.0.0
**Handover prepared by:** XiaohanMa (testing, review and release phase), reviewed by the team

## Delivered against scope

| Capability | Jira story | Verified by |
|---|---|---|
| Login / logout, password hashing, CSRF, role-based access control | GHC-A3-07 | `tests/test_security.py` (11 tests), manual 403 check |
| Member dashboard and current-round product browsing | GHC-A3-08 | `tests/test_member_browse.py` (5 tests), manual walkthrough |
| Member order create / edit / cancel with unit-vs-kg pricing from the frozen round price | GHC-A3-09 | `tests/test_pricing.py` (11), `tests/test_order_rules.py` (8) |
| Member order form and order detail screens | GHC-A3-10 | `tests/test_member_order_ui.py` (6 tests) |
| Packing sheet and packed quantity recording | GHC-A3-11 | `tests/test_packing.py`, manual packing walkthrough |
| Coordinator totals, audit trail and restricted totals API | GHC-A3-04 | `tests/test_api.py`, coordinator totals page |
| Operational report, packing completion and CSV export | GHC-A3-05 | `tests/test_reports.py`, CSV download |

Full regression: `pytest -q` -> **48 passed**. The CI workflow `.github/workflows/tests.yml` runs
the same suite on every push and pull request.

## Not delivered

| Item | Reason |
|---|---|
| Online payments | Out of scope; kept in the product backlog (priority 11) |
| Supplier portal integration | Out of scope; depends on an external system (priority 12) |
| SMS / email pickup notification | Out of scope for this assessment (priority 13) |
| Accounting export / integration | Out of scope; CSV export already covers the immediate need (priority 14) |
| Mobile application | Out of scope; the responsive web page covers the assessed workflow (priority 15) |

## Setup

1. `git clone https://github.com/zhihe-zhang1/greenhill-food-coop.git`
2. `python -m venv .venv` then activate it (`.venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`
4. `python run.py` and open <http://127.0.0.1:8000>
5. `pytest -q` to reproduce the test result reported above.

Demand accounts (demo data only, never reused outside a demo environment):

| Role | Login | Password |
|---|---|---|
| Coordinator | `coordinator@greenhill.local` | `Coordinator123!` |
| Packer | `packer@greenhill.local` | `Packer123!` |
| Member | `member@greenhill.local` | `Member123!` |

The SQLite database is generated from the schema code; `scripts/reset_db.py` recreates a clean
database and demo content.

## Known issues

| ID | Severity | Status | Note |
|---|---|---|---|
| DEF-001 | High | Fixed and retested | 403/404 handlers returned a tuple, so authorisation failures surfaced as HTTP 500 |
| DEF-002 | High | Fixed and retested | `cancel_order` read the order status instead of the round status, so cancellation always failed |
| DEF-003 | Low | Fixed and retested | Blank quantity raised `decimal.InvalidOperation` instead of returning 0 |

Open assumptions and limitations:

- Single-process SQLite deployment; concurrent write load is not supported.
- The frozen round price is authoritative for historical orders; product price changes apply to
  future rounds only.
- Packing records the quantity actually packed; a shortfall is visible in the report but no
  automatic member notification is sent.

## Configuration

- `APP_SECRET` and the database path come from environment variables; `.env.example` documents them
  with illustrative values only.
- No real credentials are stored in the repository. Rotate any token that was ever shared in a chat
  or email before handing the project on.
- `.gitignore` excludes the virtual environment, local database files and editor folders.

## Recommended next sprint

| Priority | Backlog item | Rationale |
|---|---|---|
| 1 | Pickup notification (email or SMS) | Members currently have to check the site; notification is the highest-value usability gap |
| 2 | Online payment or deposit capture | Removes manual settlement at pickup and reduces coordinator workload |
| 3 | Accounting export beyond CSV | The CSV covers reporting, but reconciliation still needs manual formatting |
| 4 | Supplier portal integration | Largest effort; only worth committing once volumes justify it |

## Maintenance notes

- Keep `main` protected and runnable; use one branch per Jira story (`feature/<jira-key>-<name>`)
  and merge only after a different team member has approved the pull request.
- Extend `docs/DEFECT_LOG.md` for every defect found after handover, and add a regression test with
  the fix.
- Tag each stable milestone (`v1.1.0`, ...) and record the release notes in `CHANGELOG.md`.
