# Changelog

All notable changes to Queuesome are documented here. The project follows
Semantic Versioning once releases resume.

## Unreleased

### Added

- Documented the trunk-based branching, Heroku promotion, and release strategy.
- Added a phased modernization roadmap and acceptance criteria.

### Changed

- Reserved an ignored local agent-harness directory and ignored common local
  secret, coverage, test, type-check, and lint artifacts.
- Reduced the production dependency manifest to direct dependencies, replaced
  the archived background-task fork with its maintained upstream package, and
  aligned infrastructure packages with Python 3.13 and Django 5.2.
- Removed an unused direct SciPy import; scikit-learn continues to install the
  compatible SciPy runtime it requires.
- Replaced runtime SVG rendering with Pillow-based recoloring of the existing
  fly mask, removing Queuesome's native Cairo system-library dependency.
