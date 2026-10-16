# Defect Log

| | |
|---|---|
| Project | Greenhill Food Co-op — ISYS3001 Assessment 3 |
| Maintained by | Member B (Moran0405) — member & ordering scope; Member C (XiaohanMa) — packing, test, deployment scope |
| Test suite | `pytest tests/` |

DEF-001 – DEF-003 were discovered by the member-side test suite written for
stories MSD426GXUST34-7/8/9/10 and fixed in the same pull requests.
DEF-004 – DEF-008 were discovered by the packing, reporting and deployment test
suite written for stories MSD426GXUST34-11/12/13/14 and fixed in the same pull
requests.

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
| DEF-004 | -13 | High | Fixed |
| DEF-005 | -13 | Medium | Fixed |
| DEF-006 | -11 | High | Fixed |
| DEF-007 | -11 | Medium | Fixed |
| DEF-008 | -11 | Medium | Fixed |

Two of the first three were **functional blockers** hidden behind pre-existing tests that never
exercised the 403/404 paths or the cancel path. Regression tests for each are now permanent.

---

# Member C — packing, test and deployment scope

## DEF-004 — 容器内服务只监听 127.0.0.1，端口无法从宿主机访问

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-13 (打包与部署配置) |
| **Found by** | `docker compose up` 后 `curl http://localhost:8000/api/health` 连接被拒 |
| **Severity / Priority** | High / High |
| **Status** | Fixed |

**Symptom** — The container starts and logs "Uvicorn running on http://127.0.0.1:8000", but every
request from the host is refused. The deployment acceptance criterion "容器启动后服务可访问"
cannot be met.

**Steps to reproduce**
1. `docker build -t greenhill . && docker run -p 8000:8000 greenhill`
2. `curl http://localhost:8000/api/health`
3. Observe `curl: (7) Failed to connect` while the container log shows the server is "running".

**Root cause** — `run.py` called `uvicorn.run(app, host='127.0.0.1', port=8000)` with the loopback
address hard-coded. Inside a container, 127.0.0.1 is the container's own network namespace, so the
published port is never bound. The same line also blocked `APP_HOST`/`APP_PORT` overrides, so
nothing in `docker-compose.yml` could correct it.

**Fix** — Read host and port from configuration and default the container to all interfaces:

```python
# app/config.py
host=_env('APP_HOST', '127.0.0.1')
port=_env_int('APP_PORT', '8000')

# run.py
uvicorn.run('app.main:app', host=settings.host, port=settings.port, reload=False)

# Dockerfile
ENV APP_HOST=0.0.0.0 APP_PORT=8000
EXPOSE 8000
```

**Retest** — `docker compose up --build` → `curl -fsS http://localhost:8000/api/health` returns
`{"status":"ok"}`; `docker inspect --format '{{.State.Health.Status}}'` reports `healthy`.

**Impact** — The deliverable was not deployable at all; this blocked the Sprint 3 deployment goal.

---

## DEF-005 — 缺少 .dockerignore，构建上下文包含虚拟环境与数据库

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-13 (打包与部署配置) |
| **Found by** | `docker build` 构建上下文体积审查 |
| **Severity / Priority** | Medium / Medium |
| **Status** | Fixed |

**Symptom** — The Docker build sends the whole working tree, including `venv/` (~200 MB),
`data/*.db`, `__pycache__` and local secrets, producing a slow build and a bloated image. A
developer's local `app.db` could be baked into the image layer.

**Root cause** — No `.dockerignore` existed, so Docker used the repository root as the whole
build context and could `COPY . .` anything sitting in the directory.

**Fix** — Added `.dockerignore` excluding virtual environments, caches, the local database,
environment files and editor metadata:

```
venv/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.env
.env.*
data/
*.db
.git/
.idea/
.vscode/
```

**Retest** — `docker build` context shrinks from ~200 MB to under 1 MB; `docker run --rm greenhill
ls /app/data` no longer shows a pre-existing database; a container started from the image creates a
fresh `app.db` on first request.

**Impact** — Slow builds and a risk of leaking local data/secrets into a published image.

---

## DEF-006 — 已取消订单的订单行仍可被分拣员打包

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-11 (分拣与打包流程) |
| **Found by** | `tests/test_packing.py::test_cancelled_order_lines_cannot_be_packed` |
| **Severity / Priority** | High / High |
| **Status** | Fixed |

**Symptom** — A member cancels an order. The order correctly disappears from the packing sheet, but
the update endpoint has no idea the order is cancelled, so it still accepts a packed quantity for any
of its lines. The line is persisted with a non-zero `packed_milli` against an order the member has
already withdrawn, and that quantity then flows into the packing completion metric and the CSV
export. The list view and the update path disagreed about the same order.

**Steps to reproduce**
1. Log in as `member@greenhill.local` and place an order in an open round.
2. Log in as `coordinator@greenhill.local`, open `/packing/round/<id>` and note the line id.
3. Back as the member, cancel that order (status becomes `cancelled`).
4. POST a packed quantity for the line id — the form still works if the sheet was left open, and a
   crafted POST works regardless:
   `curl -b cookies -d 'packed_qty=1&initials=BN&note=x&csrf_token=<token>' /packing/line/<line_id>`
5. The response flashes "Packed quantity saved." and `order_lines.packed_milli` is now non-zero for
   an order the member has already cancelled.

**Root cause** — The update query joined `orders` only to read the round id, never selecting
`o.status`, so the handler had no status to test and wrote the value unconditionally. `packing_rows()`
already filtered on `o.status='submitted'`, which is why the sheet itself looked correct and the hole
stayed invisible in normal use.

**Fix** — Select the order status in the update query and refuse the update server-side:

```python
LINE_SQL = '''SELECT ol.*, o.round_id, o.status order_status, p.sale_type
              FROM order_lines ol
              JOIN round_products rp ON rp.id = ol.round_product_id
              JOIN products p ON p.id = rp.product_id
              JOIN orders o ON o.id = ol.order_id
              WHERE ol.id = ?'''
# update handler
if row['order_status'] == 'cancelled':
    flash(request, 'This order was cancelled, so its lines cannot be packed.', 'error')
    return back
```

**Retest** — `test_cancelled_order_lines_cannot_be_packed` passes, and it is one of the 5 tests that
fail when `app/routers/packing.py` is reverted to the pre-fix version. `test_cancelled_order_is_not_listed_on_the_packing_sheet`
passes both before and after, which confirms the sheet listing was never the broken half. Manually
re-ran the steps above: the crafted POST now flashes "This order was cancelled, so its lines cannot
be packed." and `packed_milli` stays unchanged.

**Impact** — Data-integrity blocker: withdrawn orders could be packed and invoiced.

---

## DEF-007 — 空白或零打包数量被静默写入

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-11 (分拣与打包流程) |
| **Found by** | `tests/test_packing.py::test_blank_or_zero_quantity_is_not_recorded_as_packed` |
| **Severity / Priority** | Medium / Medium |
| **Status** | Fixed |

**Symptom** — Submitting an empty or `0` packed quantity still writes a row update (with
`packed_milli = 0`) and flashes "Packed quantity saved." The packer gets a false confirmation and
the line looks "packed" in reports even though nothing was weighed.

**Root cause** — `quantity_to_milli('')` and `quantity_to_milli('0')` both return `0` by design
(DEF-003), and the handler had no guard at all: it wrote whatever the conversion produced and always
flashed success. `packing completion` counts lines where `packed_milli IS NOT NULL`, so storing `0`
turned an unweighed line into a "packed" one.

**Fix** — Reject non-positive input before writing, with a message that says what to do:

```python
milli = quantity_to_milli(packed_qty, row['sale_type'])
if milli <= 0:
    flash(request, 'Enter a packed quantity greater than zero.', 'error')
    return back
```

**Retest** — `test_blank_or_zero_quantity_is_not_recorded_as_packed` passes (it is one of the 5 tests
that fail against the pre-fix file, and it exercises `''`, `'0'` and `'   '`);
`test_fractional_quantity_is_rejected_for_a_unit_product` and
`test_packer_records_a_short_packed_weight_for_a_kg_product` pass; the stored `packed_milli` stays
`NULL` after every blank submit.

**Impact** — Misleading UI feedback and dirty data in the packing/invoice reports.

---

## DEF-008 — 失败路径静默通过：CSRF 失效无提示、未知编号重定向到坏地址

| Field | Value |
|---|---|
| **Story** | MSD426GXUST34-11 (分拣与打包流程) |
| **Found by** | `tests/test_packing.py::test_forged_csrf_token_cannot_change_packed_quantity`、`::test_unknown_line_returns_not_found_instead_of_a_broken_redirect`、`::test_unknown_round_returns_not_found` |
| **Severity / Priority** | Medium / Medium |
| **Status** | Fixed |

**Symptom** — Three failure paths gave the packer no usable signal.

(a) A stale form — an expired session or a forged CSRF token — posted to `/packing/line/<id>`. The
handler skipped its whole `if row and valid_csrf(...)` body and then redirected back to the sheet, so
the page reloaded looking exactly as before with no message at all. A rejected submission was
indistinguishable from a saved one.

(b) A POST for an order line that does not exist redirected to `/packing/round/` — a URL with the
round id chopped off — instead of answering 404.

(c) GET `/packing/round/<unknown-id>` rendered an empty packing sheet with HTTP 200 instead of 404,
so a broken link looked like a valid round that happened to contain nothing.

**Root cause** — The update handler wrapped everything in `if row and valid_csrf(...)` with no `else`
branch, so every failure fell through to the same silent redirect; the redirect target was built as
`row['round_id'] if row else ''`, which produced the truncated URL. The sheet handler passed
`one('SELECT * FROM rounds WHERE id=?', ...)` straight into the template without checking whether it
returned a row.

**Fix** — Look the line up first and answer 404, check the round before rendering, and treat a failed
CSRF check as a recoverable user error that flashes and redirects back to the sheet:

```python
# GET /packing/round/{rid}
rnd = one('SELECT * FROM rounds WHERE id=?', (rid,))
if not rnd:
    raise HTTPException(404, 'Round not found.')

# POST /packing/line/{line_id}
row = one(LINE_SQL, (line_id,))
if not row:
    raise HTTPException(404, 'Order line not found.')
back = RedirectResponse(f"/packing/round/{row['round_id']}", status_code=303)
if not valid_csrf(request.session, submitted):
    flash(request, 'Session expired. Refresh the packing sheet and try again.', 'error')
    return back
```

**Retest** — All three tests pass, and `test_forged_csrf_token_cannot_change_packed_quantity` and
`test_unknown_line_returns_not_found_instead_of_a_broken_redirect` are among the 5 tests that fail
when `app/routers/packing.py` is reverted to the pre-fix version;
`test_successful_pack_is_audited_and_printed_on_the_sheet` confirms the happy path still writes
`audit_log` with `action='pack'` and `detail='packed=2'`.

**Impact** — Poor recoverability for the packer and an unhandled 500 on a malformed request.

