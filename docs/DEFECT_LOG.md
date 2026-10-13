# Defect Log

| | |
|---|---|
| Project | Greenhill Food Co-op — ISYS3001 Assessment 3 |
| Maintained by | Member B (Moran0405) — member & ordering scope |
| Test suite | `pytest tests/` |

All three defects below were discovered by the member-side test suite written for
stories MSD426GXUST34-7/8/9/10 and fixed in the same pull requests.

---

## DEF-001 — 越权访问返回 500 而不是 403 页面

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-7 (登录与访问安全) |
| **Found by** | `tests/test_security.py::test_member_role_cannot_open_the_coordinator_area` |
| **Severity / Priority** | High / High |
| **Status** | Fixed |

**Symptom** — A logged-in member requesting `/coordinator` gets HTTP 500 instead of a 403 page.

**Steps to reproduce**
1. Log in as `member@greenhill.local` / `Member123!`.
2. Request `/coordinator`.
3. Observe HTTP 500.

**Root cause** — Three handlers returned a `(Response, status_code)` tuple. Starlette calls the
returned object as an ASGI app (`await response(scope, receive, sender)`), so a tuple raises
`TypeError: 'tuple' object is not callable`:

- `app/main.py` — 403 handler
- `app/main.py` — 404 handler
- `app/routers/auth.py` — invalid-CSRF branch on `POST /login`

**Fix** — Build the response, set `response.status_code`, and return the response object.

**Retest** — `test_member_role_cannot_open_the_coordinator_area`,
`test_packer_role_cannot_open_the_member_area`,
`test_login_rejects_a_stale_csrf_token` → all pass with 403.

**Touches shared file** — `app/main.py` requires review by zhihe-zhang1 per team convention.

---

## DEF-002 — 会员永远无法取消订单

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-9 (会员订单与价格规则) |
| **Found by** | `tests/test_order_rules.py::test_member_can_cancel_their_own_order_in_an_open_round` |
| **Severity / Priority** | High / High |
| **Status** | Fixed |

**Symptom** — Cancelling an order inside a wide-open round always fails with
`OrderError: Closed-round orders cannot be cancelled.` The order stays `submitted`.

**Steps to reproduce**
1. Log in as a member and save an order in the open round.
2. Open the order detail page and press **Cancel order**.

**Root cause** — `app/services/order_service.py::cancel_order` passes the joined row straight to
`round_is_editable()`. The query is `SELECT o.*, r.status round_status …`, so `row['status']` is the
**order** status (`submitted`), never the round status. `round_is_editable` therefore always saw
`'submitted' != 'open'` and rejected every cancellation.

**Fix** — Read the round window from `round_status`:

```python
if not round_is_editable({'status': order['round_status'], 'closes_at': order['closes_at']}):
```

**Retest** — `test_member_can_cancel_their_own_order_in_an_open_round`,
`test_closed_round_blocks_cancellation`,
`test_member_cannot_cancel_another_members_order` → all pass.

**Impact** — Directly violated the acceptance criterion "能在允许状态修改/取消订单".

---

## DEF-003 — 空白数量导致计价函数抛出底层异常

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-9 (会员订单与价格规则) |
| **Found by** | `tests/test_pricing.py::test_non_positive_and_blank_quantities_become_zero` |
| **Severity / Priority** | Low / Low |
| **Status** | Fixed |

**Symptom** — `quantity_to_milli('   ', 'kg')` raises `decimal.InvalidOperation` instead of
returning `0`. An empty field submits `''` and returns `0`, but a whitespace-only field crashes.

**Root cause** — `str(value or '0').strip()` turns a whitespace-only string into `''`, and
`Decimal('')` raises `InvalidOperation`.

**Fix** — Guard blank input before parsing and translate non-numeric input into a clean
`ValueError`:

```python
raw = str(value if value is not None else '').strip()
if not raw: return 0
try: q = Decimal(raw)
except InvalidOperation: raise ValueError('Quantity must be a number.')
if not q.is_finite(): raise ValueError('Quantity must be a number.')
```

**Retest** — `test_non_positive_and_blank_quantities_become_zero`,
`test_non_numeric_quantity_is_a_clean_value_error` → pass.

---

## Summary

| ID | Story | Severity | Status |
|---|---|---|---|
| DEF-001 | -7 | High | Fixed |
| DEF-002 | -9 | High | Fixed |
| DEF-003 | -9 | Low | Fixed |

Two of the three were **functional blockers** hidden behind pre-existing tests that never exercised
the 403/404 paths or the cancel path. Regression tests for each are now permanent.
