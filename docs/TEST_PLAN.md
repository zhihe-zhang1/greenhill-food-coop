# Test Plan

## Automated
Run `pytest -q`. Tests cover pricing, authentication, order rules, HTTP routes, reporting, API access and packing updates.

## Manual acceptance
For each Jira story demonstrate every acceptance criterion. Test member isolation, closed-round editing restrictions, withdrawn products, per-unit versus per-kilogram totals, packing actual quantities and clean-checkout startup.

## Exit criteria
No known critical defect may lose an order, mis-price a line or prevent startup. Failed acceptance criteria keep the Jira story out of Done.
