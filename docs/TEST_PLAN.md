# Test Plan

**Project:** Greenhill Food Co-op Ordering System (ISYS3001 Assessment 3)
**Test owner:** XiaohanMa (member C - testing, review and release phase)
**Suite:** `pytest tests/` - 80 automated tests

## 1. Scope

**In scope:** authentication and role separation; member browsing and ordering; order rules and
unit-vs-kilogram pricing; packing and packed quantities; coordinator totals; round report, metrics
and CSV export; access-controlled totals API; deployment configuration (clean start, listen address).

**Out of scope:** load and performance testing, browser automation, accessibility audit, penetration
testing, payment or notification flows (not implemented), third-party systems.

## 2. Test levels and methods

| Level | Method | Where |
|---|---|---|
| Unit | Direct calls to service functions (`pricing`, `order`, `metrics`, `csv`, `security`) | `tests/test_pricing.py`, `tests/test_order_rules.py`, `tests/test_security.py`, `tests/test_reports.py` |
| Integration (HTTP) | FastAPI test client driving real routes, sessions, CSRF and templates | `tests/test_http.py`, `tests/test_api.py`, `tests/test_packing.py`, `tests/test_member_*.py` |
| Manual acceptance | Each story demonstrated against its Given/When/Then criteria in the sprint review | `docs/SPRINT_REVIEW_RETRO.md` |
| Deployment verification | Clean checkout start, `/api/health` poll, container build and health check | `docs/DEPLOYMENT.md` |
| Continuous integration | `.github/workflows/tests.yml` - pytest on Python 3.11 and 3.12 plus a Docker image build | GitHub Actions |

## 3. Test data and environment

- Every run builds a throwaway SQLite database in a temporary directory (`tests/conftest.py`), then
  seeds fictional users, products and one open round. No developer data is touched.
- Tests that need order data create their own round through the `new_round` fixture, so no test
  depends on rows another test created.
- Demo accounts: coordinator, packer and member (see the README). They are fictional.

## 4. Entry and exit criteria

**Entry:** the branch builds, `pip install -r requirements.txt` succeeds, the schema is created.

**Exit (all must hold before a story is moved to Done):**

1. every acceptance criterion of the story has been exercised by an automated test or demonstrated
   manually in the sprint review;
2. the whole suite passes on the branch and in CI;
3. the negative path is covered - unauthorised access, closed round, cancelled order, invalid or
   missing CSRF token, invalid quantity;
4. no known defect can lose an order, mis-price a line or prevent startup;
5. the pull request has been reviewed and approved by another team member.

## 5. What the suite covers

| Area | Representative cases |
|---|---|
| Session and roles | anonymous `/packing/...` returns 401; member requesting a coordinator page returns 403; each role lands on its own home page; logout clears the session |
| Login form | wrong password shows an error and creates no session; forged CSRF token is rejected with 403 |
| Orders and pricing | frozen round price; unit products reject fractional quantities; kilogram products accept three decimals; closed-round edits refused |
| Packing | packer records an actual weight (short supply) with initials and note; blank, zero or non-numeric input changes nothing; cancelled order lines cannot be packed; unknown line returns 404; forged CSRF token changes nothing; a successful pack is audited |
| Reporting | round report and CSV require the coordinator role; CSV carries a UTF-8 BOM and a download filename; cancelled orders never appear in the report, the CSV or the metrics; packing completion percentage |
| API | totals API rejects anonymous and member callers, serves the coordinator and packing team, keeps the payload contract, returns an empty payload for an unknown round, and prices from the round snapshot |
| Deployment | application starts from a clean checkout; `/api/health` returns `{"status":"ok"}`; `APP_HOST`/`APP_PORT` control the listen address |

## 6. Defect management

1. Any failure found while testing is recorded in `docs/DEFECT_LOG.md` with severity, steps to
   reproduce, root cause and the fix commit.
2. A regression test is committed with the fix; the defect is only closed when that test passes.
3. Severity scale: **High** = data loss, wrong money, unusable feature or security failure;
   **Medium** = incorrect reporting or missing guard on a business rule; **Low** = misleading
   feedback or cosmetic behaviour.
4. The sprint review re-runs the whole suite and retests every defect fixed during the sprint.

## 7. Known limitations

- Tests run against SQLite only; the Docker image is built in CI but not exercised end to end.
- No browser-level or accessibility testing, and no load testing (deliberate for a single-process
  teaching application).
- The audit log and some coordinator pages are verified manually rather than by automated tests.
