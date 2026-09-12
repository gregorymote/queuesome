# Changelog

All notable changes to Queuesome are documented here. The project follows
Semantic Versioning once releases resume.

## Unreleased

- Add database-aware readiness and database-independent liveness endpoints plus
  validated stdout logging configuration.

- Align background-task primary keys with its published migrations and check all
  installed applications for migration drift in CI.

- Bound and validate Spotify artwork downloads, restrict their source hosts, and
  stop deriving temporary file paths from remote URLs.

- Restrict Spot the Fly studio data APIs to superusers and require CSRF-protected
  POST requests for gameplay mutations.

### Added

- Documented the trunk-based branching, Heroku promotion, and release strategy.
- Added a phased modernization roadmap and acceptance criteria.
- Added a Docker Compose PostgreSQL development service and documented the
  environment-based local setup.
- Added GitHub Actions checks for dependencies, Django configuration, migration
  drift, fresh migrations, static collection, and tests on Python 3.13.
- Added smoke coverage for resolving and rendering the public start page.
- Added a Heroku release phase for applying database migrations and a CI check
  for staging-grade Django deployment settings.

### Changed

- Established `stage` as the integration and staging-deployment branch, with
  production releases promoted from tested staging builds.
- Updated the GitHub Actions runtime dependencies to their Node.js 24 versions.
- Restricted party mutations to active session members, required host access
  for game administration, and converted device, like, and search mutations to
  CSRF-protected POST requests.
- Bound Spotify authorization callbacks to one-time session state, validated
  callback parameters, and deferred party creation until token exchange succeeds.
- Enforced unique active party codes and session memberships, safely retried
  code collisions, and hardened missing and inactive join-code handling.
- Serialized party starts and song picks, made repeated submissions idempotent,
  and rejected song results that do not belong to the submitting member.
- Serialized category transitions, restricted library selections to choices
  offered to the current leader, and made replayed selections harmless.
- Completed song selection atomically when all remaining members have picked,
  and claimed playback before starting a worker to prevent duplicate runners.
- Updated Pillow, Requests, and Spotipy to patched releases and added image and
  OAuth integration compatibility coverage.
- Added rotatable authenticated encryption for stored Spotify token payloads
  and one-time state validation to the studio administrator OAuth flow.
- Declared a cost-neutral, scale-zero game worker process and added a validated
  execution switch while retaining the existing web-thread default.
- Reserved an ignored local agent-harness directory and ignored common local
  secret, coverage, test, type-check, and lint artifacts.
- Reduced the production dependency manifest to direct dependencies, replaced
  the archived background-task fork with its maintained upstream package, and
  aligned infrastructure packages with Python 3.13 and Django 5.2.
- Removed an unused direct SciPy import; scikit-learn continues to install the
  compatible SciPy runtime it requires.
- Replaced runtime SVG rendering with Pillow-based recoloring of the existing
  fly mask, removing Queuesome's native Cairo system-library dependency.
- Replaced hard-coded deployment modes, production hosts, URLs, and credentials
  with validated environment-based Django settings.
- Updated static and media configuration for Django 5 and enabled secure cookie,
  HTTPS redirect, proxy SSL, and configurable HSTS settings outside development.
