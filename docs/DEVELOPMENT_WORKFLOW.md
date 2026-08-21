# BuildCost Pro Development Workflow

## Engineering Loop

1. Read the Master Document and relevant architecture contract.
2. Define the smallest production-ready implementation slice.
3. Implement frontend, backend, data and integration layers as required.
4. Add unit, integration and end-to-end tests.
5. Run validation and security checks.
6. Review the diff for unintended changes.
7. Commit with a clear message.
8. Use pull requests for material feature work.
9. Merge only after validation passes.
10. Keep documentation synchronized with implementation.

## Branching

- `main` is the protected production baseline.
- Feature work should use focused feature branches.
- Pull requests should be small enough to review and test.

## Quality Gates

- Type/lint validation
- Unit tests
- Integration tests
- API contract validation
- Database migration validation
- End-to-end critical-flow tests
- Security checks
- Build validation

## Change Control

Any change that modifies approved business rules, public API contracts, database invariants, authorization rules or production infrastructure must be explicitly documented.
