# Git workflow

1. Keep `main` protected and runnable.
2. Create one branch per story: `feature/GHC-12-member-order-edit` or `fix/GHC-31-order-total-rounding`.
3. Make small meaningful commits, e.g. `GHC-12 validate closed-round order edits`.
4. Push the branch and open a Pull Request.
5. A different team member reviews the PR.
6. Fix review comments before merging.
7. Jira moves to Done only when tests pass and the PR is merged.
8. Tag stable milestones: `v0.1.0`, `v0.2.0`.

Suggested commit types: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`.
