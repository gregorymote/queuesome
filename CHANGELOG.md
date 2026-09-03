# Changelog

All notable changes to Queuesome are documented here. The project follows
Semantic Versioning once releases resume.

## Unreleased

### Added

- Documented the trunk-based branching, Heroku promotion, and release strategy.
- Added a phased modernization roadmap and acceptance criteria.
- Added a Docker Compose PostgreSQL development service and documented the
  environment-based local setup.
- Added GitHub Actions checks for dependencies, Django configuration, migration
  drift, fresh migrations, static collection, and tests on Python 3.13.
- Added smoke coverage for resolving and rendering the public start page.

### Changed

- Established `stage` as the integration and staging-deployment branch, with
  production releases promoted from tested staging builds.
- Updated the GitHub Actions runtime dependencies to their Node.js 24 versions.
- Restricted party mutations to active session members, required host access
  for game administration, and converted device, like, and search mutations to
  CSRF-protected POST requests.
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
