# Modernization roadmap

This roadmap restores Queuesome through small, reviewable vertical slices. A
phase is complete only when its acceptance criteria are automated where
practical.

## Phase 0: establish the delivery foundation

- Select and document one supported Python/Django compatibility matrix.
- Replace the historical dependency dump with direct runtime and development
  dependencies plus a reproducible lock/constraint mechanism.
- Split development, test, and production settings; validate required secrets
  at startup and provide `.env.example` with non-secret placeholders.
- Make a clean local database bootstrap possible without editing source.
- Add formatting, linting, Django checks, migration checks, and tests to CI.
- Add a release process, changelog, pull-request template, and ownership rules.

Acceptance: a fresh checkout can install, migrate, run, and execute CI using
documented commands; the same runtime is used locally, in CI, and on Heroku.

## Phase 1: secure one complete party round

- Namespace every app's URLs.
- Centralize active-party membership and host authorization.
- Convert mutations to validated POST requests with CSRF protection.
- Correct OAuth callback handling, bind OAuth state to the session, and protect
  stored refresh tokens.
- Add uniqueness and integrity constraints for party membership, join codes,
  categories, picks, and votes.
- Test host creation, guest joining, category selection, song selection,
  playback, voting, results, and cleanup.

Acceptance: two browser sessions can complete a round, and authorization,
replay, CSRF, and concurrency tests pass.

## Phase 2: durable game execution

- Express game progress as explicit, validated state transitions.
- Replace web-process threads and busy loops with a bounded worker queue.
- Make jobs idempotent and protect transitions with transactions/locks.
- Define retry, rate-limit, device-loss, worker-restart, and cancellation
  behavior for Spotify operations.
- Add structured logs, error reporting, health checks, and operational metrics.

Acceptance: restarting any web or worker process does not lose or duplicate a
party transition, and failures are visible and recoverable.

## Phase 3: product and operational readiness

- Audit the mobile experience, accessibility, browser support, error states,
  and performance.
- Remove archived/duplicated assets and committed generated files.
- Establish backups, restore drills, retention, incident response, and secret
  rotation.
- Publish privacy, terms, support, and data-deletion information and verify
  current Spotify platform requirements.
- Run staged load, security, and release/rollback exercises.

Acceptance: documented launch checklist passes in staging and production can be
promoted and rolled back without rebuilding.

## Initial work sequence

The first implementation pull requests should remain deliberately narrow:

1. Runtime, dependency, and settings baseline.
2. CI and a minimal application smoke test.
3. URL namespaces and authorization helpers.
4. Party creation/joining tests and fixes.
5. One-round state-machine tests and fixes.
6. Durable background worker architecture.
