# Sprint Review and Retrospective

Date: (fill in)
Facilitator: XiaohanMa (rotating PM for testing, review and release)
Participants: Zhihe Zhang (zhihe-zhang1), Haolin Li (Moran0405), XiaohanMa
Reviewer / stakeholder present: tutor or team-appointed reviewer (fill in)

## Review

### Demonstrated in this sprint

| Story | Demonstrated behaviour | Acceptance outcome |
|---|---|---|
| GHC-A3-07 Login and access security | Log in / log out, hashed passwords, CSRF rejection, member blocked from coordinator pages with a proper 403 page | Accepted after DEF-001 fixed |
| GHC-A3-08 Member browsing and dashboard | Current-round products with round price and sale type; own order history only; closed rounds not orderable | Accepted |
| GHC-A3-09 Orders and unit/kg pricing | Order created, edited and cancelled before the round closes; totals computed from the frozen round price; closed-round edits refused | Accepted after DEF-002 fixed |
| GHC-A3-10 Order UI and unit tests | Order form and order detail screens; regression suite for order, pricing and security rules | Accepted |
| GHC-A3-11 Packing | Packing sheet lists order lines, packed quantities recorded per member | Accepted |
| GHC-A3-04 / GHC-A3-05 Reporting | Round totals, packing completion, audit trail, printable report and CSV download | Accepted |

### Test evidence presented

- `pytest -q` -> 48 passed (baseline 14 tests plus 34 added during the sprint).
- GitHub Actions workflow green on every merged pull request.
- Defect log `docs/DEFECT_LOG.md`: DEF-001 and DEF-002 (High) fixed and retested; DEF-003 (Low)
  fixed. Each defect has a regression test.

### Deferred work

- Online payments, supplier portal integration, SMS pickup notification, accounting export and a
  mobile app remain in the product backlog (out of scope for this assessment).
- Manual packing variance beyond the recorded quantities is handled outside the system.

### Formal acceptance status

The product was accepted against the agreed acceptance criteria with known limitations recorded in
`docs/HANDOVER.md`. The signed outcome is in the formal acceptance form
(`Formal_Acceptance_Form`). No critical defect remains open; the exit criteria in
`docs/TEST_PLAN.md` are met (no known defect can lose an order, mis-price a line or prevent
startup).

## Retrospective

### What helped delivery

- Fixing the pricing convention (cents, milli-units, frozen round snapshot) during planning removed
  ambiguity and let member, packing and reporting code agree on the same numbers.
- One clear file owner per module meant four feature branches merged into `main` without a single
  conflict.
- Every pull request was reviewed by a different team member before merging, which caught the 403
  handler defect before it reached the release.

### What slowed the team

- Automated coverage on authorisation paths was thin at the start (the security test file held one
  test), so two High defects stayed hidden until the member-scope tests were expanded.
- Shared files were not announced consistently before branching, which created review pressure on
  `app/main.py`.

### Quality issues found

- DEF-001: authorisation failures escaped as HTTP 500 instead of a 403 page (High).
- DEF-002: members could never cancel an order because the order status was read instead of the
  round status (High).
- DEF-003: a blank quantity raised `decimal.InvalidOperation` instead of returning zero (Low).

### One concrete improvement for the next sprint

Write the negative-path test together with the feature, not after it. Each story should commit at
least one test for the rejection case (unauthorised, closed round, invalid quantity) in the same
pull request as the feature, so defects are found by the author rather than during review.
