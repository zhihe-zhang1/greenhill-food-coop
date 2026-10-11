# Release Plan

1. Pull latest `main` after all approved PRs are merged.
2. Run `pytest -q` from a clean environment.
3. Run the application using README only.
4. Smoke-test member, coordinator, packer, report and CSV workflows.
5. Review `.env.example`, known issues and handover notes.
6. Create an annotated Git tag such as `v1.0.0`.
7. Capture Jira release/version evidence for the final report.
