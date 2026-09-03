# Branching and releases

Queuesome uses trunk-based development. `stage` is the long-lived integration
branch and represents the code deployed to the staging environment. Production
is represented by promoted Heroku releases and version tags, not a separate
development branch.

## Branches

- Create short-lived branches from an up-to-date `stage`.
- Use `feature/<description>`, `fix/<description>`, or
  `chore/<description>` for normal work. Automation may use its own documented
  prefix, such as `codex/`.
- Open a pull request back to `stage`; do not merge until required CI checks
  pass and the change has been reviewed.
- Prefer squash merging so each pull request is one understandable change on
  `stage`.
- Delete the source branch after merge.
- Do not commit directly to `stage` or maintain a second, divergent production
  line. Production releases are immutable promotions of builds tested from
  `stage`.

Emergency production fixes follow the same process with a `fix/` branch. If
production must be restored immediately, roll back the Heroku release first,
then merge a tested fix or revert to `stage`.

## Environments

The intended flow is:

1. A pull request runs CI and may create an isolated Heroku Review App.
2. Merging into `stage` automatically deploys to the staging app, after CI.
3. Smoke tests run against staging.
4. The tested staging build artifact is promoted through a Heroku Pipeline to
   production. Production is not rebuilt from a different branch.

Database migrations run in Heroku's release phase. Migrations must be backward
compatible with the currently running application so a rolling deploy or code
rollback does not leave the database unusable.

Direct pushes to the Heroku Git remotes are reserved for recovery. They are not
the normal release mechanism.

## Versioning

Use Semantic Versioning tags:

- `0.x.y` while the modernization work is incomplete.
- `1.0.0` for the first supported relaunch.
- Increment the major version for incompatible public behavior, minor for
  backward-compatible features, and patch for backward-compatible fixes.

Tags are created from the production commit after promotion succeeds. Keep a
`CHANGELOG.md` using a human-readable "Added / Changed / Fixed / Security"
structure, with an `Unreleased` section assembled from merged pull requests.

## Migrating the existing repository

`stage` was created from the current `master` production baseline. The old
`main` branch is already contained by `master`. After the modernization
foundation pull request is ready:

1. Make `stage` the GitHub default branch.
2. Protect `stage`: require pull requests, required CI checks, resolved review
   conversations, and disallow force pushes and deletion.
3. Point the staging app's automatic GitHub deployment at `stage` and require CI.
4. Put staging and production in one Heroku Pipeline and promote staging builds
   to production.
5. Verify deploys and links, then archive/delete `main` and other obsolete
   branches. Retire `master` after the legacy production deployment path is no
   longer needed.

Changing the GitHub default branch and Heroku deployment settings must be done
as one coordinated operation; until then, `master` remains the operational
default and existing Heroku deployment settings remain unchanged.
