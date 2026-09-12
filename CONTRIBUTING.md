# Contributing

Queuesome is being modernized in small, independently reviewable changes. Read
`docs/branching-and-releases.md` and `docs/modernization-roadmap.md` before
starting work.

## Workflow

1. Branch from the latest `stage` using `feature/`, `fix/`, or `chore/`.
2. Keep a pull request focused on one deployable outcome.
3. Add or update tests for every behavior change and regression fix.
4. Update the `Unreleased` section of `CHANGELOG.md` for user-visible,
   operational, or security-relevant changes.
5. Run the repository's formatting, linting, Django, migration, and test checks.
6. Open a pull request and merge only after required checks and review pass.

Never commit credentials, production data, OAuth tokens, or local environment
files. Report suspected credential exposure privately and rotate the affected
credential before attempting repository cleanup.

## Dependency updates

Edit only the direct production requirements in `requirements.in`, then rebuild
the fully pinned deployment lock from a clean Python 3.13 environment:

```shell
lock_workspace="$(mktemp -d)"
python -m venv "$lock_workspace/venv"
"$lock_workspace/venv/bin/pip" install --requirement requirements.in
"$lock_workspace/venv/bin/pip" freeze \
  --exclude pip --exclude setuptools --exclude wheel > requirements.txt
```

Commit `requirements.in` and the resulting `requirements.txt` together. Install
and test from `requirements.txt`, which is the file used by CI and Heroku.
