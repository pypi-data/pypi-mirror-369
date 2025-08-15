# Changelog

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**  
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

**Important:** Update version for "civic-transparency-spec==x.y.z" in `pyproject.toml` also.

## [Unreleased]

### Added

- (placeholder) Notes for the next release.

---

## [0.1.8] - 2025-08-14

### Changed

- **Docs & Metadata:** Refined documentation, cleaned internal references, and improved contributor guidance.


> No schema or API changes in this release.

---

## [0.1.7] - 2025-08-11

### Changed

- **Actions & Key Project Files:** Align with best practices.

> No schema or API changes in this release.

---

## [0.0.7] - 2025-08-11

### Changed

- **CI:** No formatting in CI due to auto-gen code.
- **Release:** Add test and validate explicitly.

> No schema or API changes in this release.

---

## [0.0.6] - 2025-08-11

### Fixed

- **Actions:** Updated actions process for correct versioning.

> No schema or API changes in this release.

---

## [0.0.5] - 2025-08-11

### Fixed

- **Generator:** Refactored generator code.
- **Release:** Fixed release action.

> No schema or API changes in this release.

---

## [0.0.4] - 2025-08-11

### Fixed

- **CI:** Fixed auto-generation **version** import error in CI action.

> No schema or API changes in this release.

---

## [0.0.3] - 2025-08-11

### Fixed

- **CI:** Fixed **version** import error in CI action.

> No schema or API changes in this release.

---

## [0.0.2] - 2025-08-11

### Fixed

- **CI:** Fixed error in CI action.

> No schema or API changes in this release.

---

## [0.0.1] - 2025-08-11

### Added

- Initial public release of **Civic Transparency Types** (Pydantic v2) generated from `civic-transparency-spec==0.1.1`:
  - Models: `Meta`, `Run`, `Scenario`, `Series`, `ProvenanceTag`.
- **Docs site** scaffolding (MkDocs Material, i18n) with API reference pages via `mkdocstrings`.
- **Codegen script:** `scripts/generate_types.py` (uses `datamodel-code-generator`) to regenerate models from the spec schemas.
- **Testing:** Import/public API surface checks, version presence, and coverage target (pytest + pytest-cov).
- **Packaging:** `py.typed` marker included for type checkers; generated modules shipped in the wheel.
- **CI:** GitHub Actions for lint, type regeneration guard, tests, docs build, and package build.

---

## Notes on versioning and releases

- We use **SemVer**:
  - **MAJOR** – breaking model changes relative to the spec
  - **MINOR** – backward-compatible additions
  - **PATCH** – clarifications, docs, tooling
- Versions are driven by git tags via `setuptools_scm`. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.

[Unreleased]: https://github.com/civic-interconnect/civic-transparency-spec/compare/v0.1.7...HEAD
[0.1.7]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.7...v0.1.7
[0.0.7]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/civic-interconnect/civic-transparency-types/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/civic-interconnect/civic-transparency-types/releases/tag/v0.0.1
