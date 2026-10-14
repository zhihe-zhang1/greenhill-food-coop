# Test Evidence — Member B (会员端与下单流程)

| | |
|---|---|
| Project | Greenhill Food Co-op — ISYS3001 Assessment 3 |
| Author | Member B (Moran0405) |
| Stories covered | MSD426GXUST34-7, -8, -9, -10 |
| Test framework | pytest + FastAPI TestClient (`httpx`) |
| Test data | `app/db.py::seed_demo()` into a throw-away SQLite DB per session (`tests/conftest.py`) |
| Command | `python -m pytest tests/ -q` |
| Latest result | **48 passed** (integrated `main` after merging PRs -7/-8/-9/-10) |

---

## 1. Testing strategy

| Level | Method | Where |
|---|---|---|
| Unit | White-box, direct function calls | `tests/test_pricing.py`, `tests/test_security.py` |
| Service/integration | Grey-box, service layer against the seeded DB | `tests/test_order_rules.py` |
| System | Black-box, HTTP through the real ASGI app | `tests/test_member_browse.py`, `tests/test_member_order_ui.py`, `tests/test_security.py` |

Testing types used: functional, regression, security/access-control, input-validation.
Each defect found is pinned by a regression test so it cannot silently return.

## 2. Test scenarios (member scope)

| Scenario | Related story | Purpose |
|---|---|---|
| TS-M1 | -7 | Secure sign-in, session handling and CSRF protection |
| TS-M2 | -7 | Role isolation — members cannot reach coordinator pages |
| TS-M3 | -8 | Browse the current round's catalogue and personal history |
| TS-M4 | -9 | Order capture, edit and cancel under pricing rules |
| TS-M5 | -9 | Round price snapshot is authoritative for settlement |
| TS-M6 | -10 | Member order screens render correctly behind authentication |

## 3. Test cases (summary)

| Test case | Scenario | Level | Asserts |
|---|---|---|---|
| `test_password_hash_round_trip` | TS-M1 | Unit | hash is not plaintext and verifies correctly |
| `test_hash_uses_pbkdf2_and_a_random_salt` | TS-M1 | Unit | PBKDF2 prefix; identical passwords → different digests |
| `test_verify_password_rejects_malformed_encodings` | TS-M1 | Unit | malformed hashes return False, never raise |
| `test_csrf_token_is_stable_within_a_session_and_strictly_validated` | TS-M1 | Unit | token issued once, tampering rejected |
| `test_login_rejects_wrong_password` | TS-M1 | System | wrong password refused, session not opened |
| `test_login_rejects_unknown_account` | TS-M1 | System | unknown email refused |
| `test_login_rejects_a_stale_csrf_token` | TS-M1 | System | invalid CSRF → 403 (DEF-001) |
| `test_logout_clears_the_session` | TS-M1 | System | after logout `/member` → 401 |
| `test_anonymous_visitors_are_blocked_from_the_member_area` | TS-M2 | System | anonymous → 401 |
| `test_member_role_cannot_open_the_coordinator_area` | TS-M2 | System | member → 403 (DEF-001) |
| `test_packer_role_cannot_open_the_member_area` | TS-M2 | System | packer → 403 (DEF-001) |
| `test_member_pages_require_login` | TS-M3 | System | 401 for dashboard/products |
| `test_dashboard_shows_greeting_current_round_and_history` | TS-M3 | System | round, greeting and history render |
| `test_products_page_lists_the_current_round_catalogue` | TS-M3 | System | catalogue + snapshot wording |
| `test_products_for_round_only_returns_available_active_items` | TS-M3 | Service | unavailable/inactive filtered out |
| `test_unavailable_product_disappears_from_the_member_view` | TS-M3 | System | coordinator toggle hides the product |
| `test_member_order_saves_and_prices` | TS-M4 | Service | order persists and totals correctly |
| `test_closed_round_rejects_edit` | TS-M4 | Service | closed round cannot be edited |
| `test_editing_an_order_replaces_its_lines` | TS-M4 | Service | re-saving replaces old lines |
| `test_empty_or_all_zero_order_is_rejected` | TS-M4 | Service | no empty orders |
| `test_member_can_cancel_their_own_order_in_an_open_round` | TS-M4 | Service | cancel works (DEF-002) |
| `test_member_cannot_cancel_another_members_order` | TS-M4 | Service | ownership enforced |
| `test_closed_round_blocks_cancellation` | TS-M4 | Service | closed round cannot cancel |
| `test_order_prices_from_the_round_snapshot_not_the_live_catalogue` | TS-M5 | Service | live price change does not alter totals |
| `test_unit_pricing` / `test_weight_pricing` | TS-M5 | Unit | unit and kg maths |
| `test_weight_quantity_rounds_half_up_to_milli` | TS-M5 | Unit | half-up rounding |
| `test_weight_total_rounds_half_up_to_cents` | TS-M5 | Unit | half-up cent rounding |
| `test_unit_total_requires_a_whole_number_of_items` | TS-M5 | Unit | fractional units rejected |
| `test_non_positive_and_blank_quantities_become_zero` | TS-M5 | Unit | blank/zero handling (DEF-003) |
| `test_non_numeric_quantity_is_a_clean_value_error` | TS-M5 | Unit | bad input → ValueError (DEF-003) |
| `test_money_formats_cents_for_display` | TS-M5 | Unit | currency formatting |
| `test_order_form_requires_login` | TS-M6 | System | 401 |
| `test_order_form_lists_products_behind_a_csrf_protected_save` | TS-M6 | System | form renders with CSRF |
| `test_order_form_switches_to_edit_mode_once_an_order_exists` | TS-M6 | System | edit vs create mode |
| `test_order_submission_without_a_valid_csrf_token_is_ignored` | TS-M6 | System | CSRF-protected POST |
| `test_order_detail_renders_lines_total_and_cancel_option` | TS-M6 | System | detail page + cancel button |
| `test_order_detail_bounces_back_for_an_order_that_is_not_yours` | TS-M6 | System | foreign order redirected |

## 4. Traceability matrix

| Story | Scenario | Test files | Test cases | Status |
|---|---|---|---|---|
| MSD426GXUST34-7 登录与访问安全 | TS-M1, TS-M2 | `tests/test_security.py` | 11 | Covered |
| MSD426GXUST34-8 会员商品浏览与面板 | TS-M3 | `tests/test_member_browse.py` | 5 | Covered |
| MSD426GXUST34-9 会员订单与价格规则 | TS-M4, TS-M5 | `tests/test_order_rules.py`, `tests/test_pricing.py` | 19 | Covered |
| MSD426GXUST34-10 会员界面与业务单测 | TS-M6 | `tests/test_member_order_ui.py` | 6 | Covered |

Every member story has at least one automated test; the two High-severity defects are each
pinned by a dedicated regression case.

## 5. Results

| Run | Result |
|---|---|
| Initial suite (before member tests) | 14 passed |
| After PR -7 (login & access security) | 24 passed |
| After PR -8 (member browsing) | 19 passed on the branch / 29 integrated |
| After PR -9 (orders & pricing) | 27 passed on the branch / 42 integrated |
| After PR -10 (member UI) | 20 passed on the branch |
| **Integrated `main` (all four merged)** | **48 passed, 0 failed** |

## 6. Defects found and fixed

| ID | Story | Severity | Status | Regression test |
|---|---|---|---|---|
| DEF-001 | -7 | High | Fixed | `test_member_role_cannot_open_the_coordinator_area` |
| DEF-002 | -9 | High | Fixed | `test_member_can_cancel_their_own_order_in_an_open_round` |
| DEF-003 | -9 | Low | Fixed | `test_non_positive_and_blank_quantities_become_zero` |

See `docs/DEFECT_LOG.md` for full reproduction steps and root-cause analysis.

## 7. Remaining quality limitations

- No automated browser/UI test (Playwright/Cypress); screen checks are server-rendered HTML assertions.
- Compatibility and usability testing for the member flow are performed manually and evidenced by screenshots.
- `seed_demo()` data is shared across the session, so order tests restore any round/product state they mutate;
  a per-test transactional fixture would isolate them further.
