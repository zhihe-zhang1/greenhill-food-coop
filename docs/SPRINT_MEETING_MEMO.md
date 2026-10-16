# Sprint Meeting Memo

> Keep one entry per meeting (daily stand-up, planning or review). Dates, attendees and facilitator
> must match the Jira comments and the actual meeting. Entries below reflect work that was carried
> out on the project; adjust the date, facilitator and attendee lines to the real meeting.

---

## Memo 1 - Sprint planning

Date: (fill in, e.g. Week 5 tutorial)
Facilitator / rotating PM: Zhihe Zhang (zhihe-zhang1)
Attendees: Zhihe Zhang, Haolin Li, XiaohanMa

### Progress since last meeting
- Repository skeleton, SQLite schema and seed data agreed; module ownership confirmed.
- Product backlog drafted in Jira with user stories, acceptance criteria and story points.

### Blockers and risks
- No agreed pricing convention yet -> risk that members and reports compute totals differently.
- Shared files (`app/main.py`, `app/db.py`) could be edited from several branches.

### Decisions
- Money is stored in cents (`price_cents`); quantities use `requested_milli` / `packed_milli`.
- Round creation copies the current product price into `round_products`; later price changes affect
  future rounds only (frozen price snapshot).
- Cancelled orders are excluded from coordinator totals and reports.
- One branch per story: `feature/<jira-key>-<short-name>`; another member must review the PR.

### Jira changes
- Stories moved: none (planning)
- Scope changes: payments, supplier integration, notifications and mobile work stay in the product
  backlog only
- New defects: none

### Actions
| Action | Owner | Due |
|---|---|---|
| Create Jira stories with acceptance criteria and story points | Zhihe Zhang | End of planning |
| Publish the branch and commit-message convention | Zhihe Zhang | End of planning |
| Implement authentication, role guards and CSRF protection | Haolin Li | Sprint 1 |
| Implement packing sheet and quantity recording | XiaohanMa | Sprint 2 |

---

## Memo 2 - Daily stand-up (development execution)

Date: (fill in)
Facilitator / rotating PM: Haolin Li (Moran0405, member B)
Attendees: Zhihe Zhang, Haolin Li, XiaohanMa

### Progress since last meeting
- Member order flow implemented: order create / edit / cancel plus unit-vs-kg conversion
  (`app/services/order_service.py`, `app/services/pricing.py`).
- Member dashboard and current-round product browsing implemented.
- Packing sheet reads order lines and records packed quantities.

### Blockers and risks
- **Blocker (raised by Haolin Li):** a member opening a coordinator-only URL received HTTP 500
  instead of the 403 page, so unauthorised access was not handled correctly.
  Cause: the 403/404 exception handlers returned a `(Response, 403)` tuple.
  Resolution: handlers rewritten to return a `Response`; the same pattern fixed in the login CSRF
  branch. Logged as DEF-001 in `docs/DEFECT_LOG.md`.
- **Blocker (raised by Haolin Li):** members could never cancel an order - `cancel_order` read the
  **order** status (`submitted`) instead of the **round** status. Logged as DEF-002.
- **Risk:** shared file `app/main.py` is touched by the login branch, so it must be reviewed and
  merged by the coordinator.

### Decisions
- Fix DEF-001 and DEF-002 before the sprint review; both block acceptance criteria and therefore
  block the Definition of Done.
- Hot-fix branches reference the Jira issue key in the commit message so the board shows the link.

### Jira changes
- Stories moved: GHC-A3-07 -> In Review; GHC-A3-08 -> In Progress; GHC-A3-09 -> In Progress
- Scope changes: none
- New defects: DEF-001 (High, escape to 500 on authorisation failure), DEF-002 (High, cancellation
  impossible), DEF-003 (Low, blank quantity raised `decimal.InvalidOperation`)

### Actions
| Action | Owner | Due |
|---|---|---|
| Fix DEF-001 in `app/main.py` and `app/routers/auth.py` | Haolin Li | Same day |
| Fix DEF-002 in `order_service.cancel_order` | Haolin Li | Same day |
| Extend `test_security.py`, `test_pricing.py`, `test_order_rules.py` with regression cases | Haolin Li | Same day |
| Review and approve the login branch PR (shared file) | Zhihe Zhang | Next stand-up |
| Verify packing quantities reconcile with member orders | XiaohanMa | Next stand-up |

---

## Memo 3 - Sprint review and retrospective preparation

Date: (fill in)
Facilitator / rotating PM: XiaohanMa
Attendees: Zhihe Zhang, Haolin Li, XiaohanMa

### Progress since last meeting
- Four member-scope stories completed and merged through reviewed pull requests
  (login security, member browsing, order rules and pricing, order UI and unit tests).
- Automated suite grown from 14 to 48 tests; all passing locally and in GitHub Actions.
- Operational report, CSV export and audit trail completed by the coordinator scope.

### Blockers and risks
- No blocking issue remains open; known limitations recorded in `docs/HANDOVER.md`.

### Decisions
- Tag the release `v1.0.0`, publish release notes and keep the versioned evidence for the report.
- Record DEF-001 to DEF-003 in the final report as test-driven defect discovery.

### Jira changes
- Stories moved: GHC-A3-07 to GHC-A3-10 -> Done (each after approval of its pull request)
- Scope changes: none
- New defects: none open after retesting

### Actions
| Action | Owner | Due |
|---|---|---|
| Tag `v1.0.0` and create the GitHub release | Zhihe Zhang | Closure |
| Complete handover and known-issue notes | XiaohanMa | Closure |
| Prepare the report's testing section and defect analysis | Haolin Li | Closure |
