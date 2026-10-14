# Sprint Plan

This document records the team's sprint planning for the Greenhill Food Co-op ordering system.
Sprint names, dates and capacity must match the Jira board (`MSD426GXUST34`).

## Team and rotating project manager

| Phase | Rotating project manager | Result of the phase |
|---|---|---|
| Project initiation and sprint planning | Zhihe Zhang (zhihe-zhang1) | Requirements confirmed, Jira backlog created, acceptance criteria and branch conventions agreed |
| Development execution and daily tracking | Haolin Li (Moran0405, member B) | Orders, pricing and member features delivered; blockers, changes and stand-ups recorded in Jira |
| Testing, review and release | Member C | Defect regression, sprint review, release checks and closure evidence |

## Sprint goal (delivered sprint)

**Sprint goal:** Deliver an end-to-end working weekly order - published products -> member order ->
coordinator totals -> printable packing record - and close the release with passing automated tests.

Commit only stories the team can finish under the Definition of Done. Keep payments, supplier
integrations, notifications and mobile work in the product backlog.

## Sprint structure

| Sprint (Jira) | Focus | Sprint outcome |
|---|---|---|
| MSD426GX Sprint 1 | Application skeleton, SQLite schema, seed data, authentication, coordinator product/member/round management | Runnable app, roles enforced, rounds and price snapshots creatable |
| MSD426GX Sprint 2 | Member browsing, order create/edit/cancel, unit-vs-kg pricing, packing sheet and packed quantities | Member order flow demonstrable end to end |
| MSD426GX Sprint 3 | Operational report and CSV export, audit trail, member order UI, defect fixes and release v1.0.0 | Release candidate accepted by the team reviewer |

> Fill in the actual start and end dates of each sprint from Jira.

## Committed backlog for the delivered sprint

| Story | Owner | Points | Jira key | Test approach |
|---|---|---|---|---|
| GHC-A3-07 Login and access security | Haolin Li (B) | 3 | MSD426GXUST34 (see board) | Unit tests for hashing and CSRF; HTTP tests for role-based access |
| GHC-A3-08 Member product browsing and dashboard | Haolin Li (B) | 3 | MSD426GXUST34 (see board) | HTTP tests for member-only access, round status and product listing |
| GHC-A3-09 Member orders and unit/kg pricing rules | Haolin Li (B) | 5 | MSD426GXUST34 (see board) | Unit tests for price snapshot, quantity conversion, edit/cancel rules |
| GHC-A3-10 Member order UI and business unit tests | Haolin Li (B) | 5 | MSD426GXUST34 (see board) | UI-level tests for order form and order detail; full regression run |
| GHC-A3-11 Packing and dispatch of exact quantities | Member C | 5 | MSD426GXUST34 (see board) | Integration tests for packing sheet and packed quantities |
| GHC-A3-12 Automated tests and CI | Member C | 3 | MSD426GXUST34 (see board) | GitHub Actions workflow executing the pytest suite |
| GHC-A3-04 Coordinator totals, audit and restricted API | Zhihe Zhang (A) | 5 | MSD426GXUST34 (see board) | Service tests for totals, audit log and API access control |
| GHC-A3-05 Operational report and CSV export | Zhihe Zhang (A) | 5 | MSD426GXUST34 (see board) | Report, metrics and CSV tests plus manual CSV download check |

**Committed capacity:** 3 developers. Confirm the number of working hours per person in Jira before
the first stand-up; do not commit more points than the team can finish under the Definition of Done.

## Dependencies between committed stories

- The member order flow (B) reads the round price snapshot created by the coordinator round story (A).
  An order must always be priced from `round_products`, never from the product's latest price.
- Packing (C) reads `order_lines` written by the member order flow (B); packed quantities must
  reconcile with the member's requested quantities.
- The operational report (A) aggregates order lines, so cancelled orders must be excluded by the
  order service (B) rather than filtered again in the report.
- `app/main.py`, `app/db.py` and `app/templates/base.html` are shared files controlled by
  zhihe-zhang1; changes to them are announced in stand-up before the branch is pushed.

## Test approach for the sprint

- Automated: `pytest -q`. Every story must leave the suite green; the CI workflow in
  `.github/workflows/tests.yml` runs the suite on every push and pull request.
- Manual acceptance: each story is demonstrated against its acceptance criteria in the sprint review
  (member isolation, closed-round restrictions, unit-vs-kg totals, packing quantities, CSV export).
- Defects found during the sprint are logged in `docs/DEFECT_LOG.md` with severity, root cause and
  the fix commit, and are linked to the story they block.

## Definition of Done

A story may only be moved to Done in Jira when:

1. every acceptance criterion has been demonstrated;
2. the automated suite passes;
3. the pull request has been reviewed and approved by a different team member;
4. affected documentation is updated; and
5. the Jira issue contains the requirement, acceptance criteria, owner, sprint, test evidence and
   the linked pull request.

## Risks for this sprint

| Risk | Impact | Mitigation |
|---|---|---|
| Price snapshot bypassed by the member view | Wrong totals, rejected acceptance criteria | Order service always reads `round_products`; covered by unit tests |
| Shared files (`app/main.py`) edited on several branches | Merge conflicts, broken integration | One owner per file; announce changes in stand-up |
| Weak test coverage on authorisation paths | Defects reach the release | Expand tests per story; defect log drives regression tests |
| Late delivery pressure | Documentation and evidence gaps | Evidence captured while working, not reconstructed afterwards |
