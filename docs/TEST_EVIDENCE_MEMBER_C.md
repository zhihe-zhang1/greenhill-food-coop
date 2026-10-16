# Test Evidence - member C (XiaohanMa)

**Scope:** GHC-A3-11 packing flow, GHC-A3-12 automated tests and CI, GHC-A3-13 run/deployment
configuration, GHC-A3-14 test deliverables and configuration management.
**Command:** `pytest tests/ -q`　**Result:** **80 passed** (baseline 48 before this work; 32 tests added).
**Reproduced on:** Python 3.13 locally, Python 3.11 and 3.12 in GitHub Actions.

## 1. Test cases added or extended

| # | File | Test case | Level | Covers |
|---|---|---|---|---|
| 1 | `tests/test_packing.py` | `test_packing_sheet_requires_a_packing_or_coordinator_role` | HTTP | 401 anonymous, 403 member, 200 packing team |
| 2 | `tests/test_packing.py` | `test_unknown_round_returns_not_found` | HTTP | DEF-008 error handling |
| 3 | `tests/test_packing.py` | `test_packer_records_a_short_packed_weight_for_a_kg_product` | HTTP | actual weight, note visible on the sheet |
| 4 | `tests/test_packing.py` | `test_fractional_quantity_is_rejected_for_a_unit_product` | HTTP | unit vs kg rule |
| 5 | `tests/test_packing.py` | `test_non_numeric_quantity_is_reported_instead_of_failing` | HTTP | DEF-008 input handling |
| 6 | `tests/test_packing.py` | `test_blank_or_zero_quantity_is_not_recorded_as_packed` | HTTP | DEF-007 |
| 7 | `tests/test_packing.py` | `test_cancelled_order_lines_cannot_be_packed` | HTTP | DEF-006 |
| 8 | `tests/test_packing.py` | `test_cancelled_order_is_not_listed_on_the_packing_sheet` | HTTP | cancelled orders excluded |
| 9 | `tests/test_packing.py` | `test_forged_csrf_token_cannot_change_packed_quantity` | HTTP | CSRF protection + feedback |
| 10 | `tests/test_packing.py` | `test_unknown_line_returns_not_found_instead_of_a_broken_redirect` | HTTP | DEF-008 |
| 11 | `tests/test_packing.py` | `test_successful_pack_is_audited_and_printed_on_the_sheet` | HTTP | audit trail |
| 12 | `tests/test_api.py` | `test_totals_api_rejects_anonymous_and_member` | HTTP | access control |
| 13 | `tests/test_api.py` | `test_totals_api_is_available_to_the_packing_team` | HTTP | intended access rule |
| 14 | `tests/test_api.py` | `test_totals_api_payload_contract` | HTTP | JSON contract, per-kg total |
| 15 | `tests/test_api.py` | `test_totals_api_for_an_unknown_round_returns_an_empty_payload` | HTTP | edge case |
| 16 | `tests/test_api.py` | `test_totals_api_excludes_cancelled_orders` | HTTP | totals correctness |
| 17 | `tests/test_api.py` | `test_totals_api_uses_the_round_price_snapshot_when_a_product_price_changes` | HTTP | frozen price rule |
| 18 | `tests/test_http.py` | `test_login_rejects_a_wrong_password` | HTTP | no session on failure |
| 19 | `tests/test_http.py` | `test_login_rejects_a_forged_csrf_token` | HTTP | 403 on forged token |
| 20 | `tests/test_http.py` | `test_anonymous_visitor_is_redirected_to_the_login_page` | HTTP | landing page |
| 21 | `tests/test_http.py` | `test_each_role_lands_on_its_own_home_page` | HTTP | role routing |
| 22 | `tests/test_http.py` | `test_logout_clears_the_session` | HTTP | session lifecycle |
| 23 | `tests/test_http.py` | `test_unknown_url_renders_the_404_page` | HTTP | error page |
| 24 | `tests/test_reports.py` | `test_report_and_csv_require_the_coordinator_role` | HTTP | 401/403 on reports |
| 25 | `tests/test_reports.py` | `test_report_for_an_unknown_round_redirects_to_the_round_list` | HTTP | edge case |
| 26 | `tests/test_reports.py` | `test_csv_for_an_unknown_round_returns_not_found` | HTTP | edge case |
| 27 | `tests/test_reports.py` | `test_report_shows_the_round_totals_and_completion` | HTTP | report content |
| 28 | `tests/test_reports.py` | `test_csv_export_is_downloadable_and_prefixed_for_excel` | HTTP | BOM + filename |
| 29 | `tests/test_reports.py` | `test_csv_export_excludes_cancelled_orders` | Unit | CSV correctness |
| 30 | `tests/test_reports.py` | `test_round_metrics_report_packing_completion` | Unit | packing percentage |
| 31 | `tests/test_reports.py` | `test_round_metrics_ignore_cancelled_orders` | Unit | metrics correctness |
| 32 | `tests/conftest.py` | shared `login`, `logout`, `csrf_of`, `new_round`, `place_order` fixtures | - | test isolation |

## 2. Traceability matrix

| Story | Acceptance criterion | Test case(s) |
|---|---|---|
| GHC-A3-11 Packing sheet and packed quantities | Given a submitted order, When the packing sheet is opened by the packing team, Then every line shows the requested quantity and an input for the actual packed quantity | #1, #3, #8 |
| GHC-A3-11 | Given a per-kilogram product, When a short weight is recorded, Then the actual weight, initials and note are stored and shown on the sheet | #3, #11 |
| GHC-A3-11 | Given a per-unit product, When a fractional quantity is entered, Then it is rejected and nothing is stored | #4, #5 |
| GHC-A3-11 | Given a cancelled order, When a packed quantity is submitted for one of its lines, Then the change is refused and the line stays unpacked | #7, #8 |
| GHC-A3-12 Tests and CI | Given any change, When CI runs on the branch, Then the whole suite runs on Python 3.11 and 3.12 and a test failure blocks the merge | `.github/workflows/tests.yml` (test + docker jobs) |
| GHC-A3-12 | Given an unauthorised caller, When a protected route or API is requested, Then the response is 401 or 403 and no data is returned | #1, #12, #24 |
| GHC-A3-12 | Given a forged or missing CSRF token, When a state-changing form is posted, Then nothing changes and the caller is told why | #9, #19 |
| GHC-A3-12 | Given a round with orders, When the totals API is called, Then quantities and money follow the round price snapshot and exclude cancelled orders | #16, #17 |
| GHC-A3-13 Run and deployment | Given a clean checkout, When the application is started, Then it serves `/api/health` with `{"status":"ok"}` | Deployment verification (§3) |
| GHC-A3-13 | Given a container deployment, When the image is built and run with a published port, Then the application is reachable from outside the container | DEF-004 fix, `APP_HOST=0.0.0.0`, Dockerfile / compose |
| GHC-A3-14 Test and configuration deliverables | Given the repository, When a reviewer reads the test plan, defect log and configuration-management notes, Then each story maps to tests and each defect to a regression test | This document, `TEST_PLAN.md`, `DEFECT_LOG.md`, `CONFIGURATION_MANAGEMENT.md` |

## 3. Recorded results

```
$ pytest tests/ -q
80 passed, 1 warning in 39.48s
```

| Test file | Cases |
|---|---|
| `tests/test_packing.py` | 12 |
| `tests/test_security.py` | 11 |
| `tests/test_pricing.py` | 11 |
| `tests/test_reports.py` | 10 |
| `tests/test_http.py` | 9 |
| `tests/test_api.py` | 8 |
| `tests/test_order_rules.py` | 8 |
| `tests/test_member_order_ui.py` | 6 |
| `tests/test_member_browse.py` | 5 |
| **Total** | **80** |

Deployment verification (`docs/DEPLOYMENT.md`):

```
$ pytest -q                                     -> 80 passed
$ curl -s http://127.0.0.1:8000/api/health      -> {"status":"ok"}
$ APP_HOST=0.0.0.0 APP_PORT=8123 python run.py  -> Uvicorn running on http://0.0.0.0:8123
$ GET /login                                    -> 200 (sign-in page rendered)
```

## 4. Defects found by this work

| ID | Severity | Summary | Regression test |
|---|---|---|---|
| DEF-004 | High | The container bound loopback, so a published port never reached the application | Deployment verification above |
| DEF-005 | Medium | No `.dockerignore`, so `venv/` and a local database were copied into the image | Docker image build (CI) |
| DEF-006 | High | A cancelled order's lines still accepted packed quantities | #7 |
| DEF-007 | Medium | A blank or zero packed quantity was stored, reporting an unpacked line as packed | #6 |
| DEF-008 | Medium | Invalid CSRF tokens and unknown line ids failed silently (no feedback, malformed redirect) | #9, #10 |

Before the fixes in `app/routers/packing.py`, five of the new packing tests failed; after the fixes
the file passes 12/12. Full detail: `docs/DEFECT_LOG.md`.

## 5. Retest and regression

- Every defect above was fixed together with at least one regression test in the same pull request.
- The suite is re-run after each merge; a red suite blocks the pull request from being merged.
- No defect from the member-side scope (DEF-001 to DEF-003) was reintroduced by this work.
