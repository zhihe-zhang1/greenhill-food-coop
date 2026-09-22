# Git Workflow

## Branch model

```text
main
 └── feature/zhihe-zhang
```

`main` is kept as the stable branch. Assessment 2 development is performed on `feature/zhihe-zhang`.

For Assessment 3, story-specific branches should include the Jira issue key, for example:

```text
feature/MSD426GXUST34-5-place-order
feature/MSD426GXUST34-8-packing-sheet
```

## Daily workflow

```bash
git switch feature/zhihe-zhang
git pull origin feature/zhihe-zhang

# make a focused change

pytest -q
git status
git add <files>
git commit -m "type: short description"
git push origin feature/zhihe-zhang
```

## Commit convention

This repository uses simple conventional-style prefixes:

- `feat:` new user-facing capability
- `fix:` correction to an existing capability
- `test:` automated test changes
- `ci:` continuous-integration changes
- `chore:` configuration or maintenance work
- `docs:` documentation changes

A commit should represent one meaningful change and should avoid unrelated files.

## Pull request workflow

When the development branch is ready:

1. Open a pull request from `feature/zhihe-zhang` to `main`.
2. Confirm GitHub Actions passes.
3. Review changed files.
4. Obtain review where required.
5. Address review comments.
6. Merge only after checks and review are complete.
7. Re-run or verify tests on the stable branch.
8. Create a release/tag when the version is ready.

## Assessment 3 story workflow

The Greenhill case Definition of Done requires story-named branches and review. The recommended flow is:

```text
Jira Story
→ story branch
→ implementation
→ acceptance criteria checked
→ automated tests
→ push
→ pull request
→ review
→ merge
→ Jira/Confluence update
```

The Jira issue key should appear in the branch name and can also be included in related commit or pull-request text.
