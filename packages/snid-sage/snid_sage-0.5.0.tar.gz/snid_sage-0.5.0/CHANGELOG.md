# Changelog

All notable changes to SNID SAGE will be documented in this file.

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 

---

## [0.5.0] - 2025-08-15

### 🎉 First Fully Stable Release

This release marks SNID SAGE's transition to a fully stable, production-ready application.

### Added
- REST and observed wavelength axes support (GUI and CLI)

### Fixed
- Resolved all known bugs and edge cases

### Notes
- **This is the first release officially recommended for production use**


## [0.4.1] - 2025-08-14

### Added
- Automatic version checking on startup (GUI and CLI). The check is non-blocking and only notifies when an update is available.

### Fixed
- Cross‑platform keyboard shortcuts: corrected Ctrl (Windows/Linux) vs Cmd (macOS) handling across GUI menus and dialogs.

### Notes
- Version numbering managed by setuptools_scm; publish by tagging `v0.4.1`.

---

## [0.4.0] - 2025-08-14

### Changed
- Prepare documentation for 0.4.0 release
- Mark 0.4.0 as current release across docs

### Fixed
- Minor documentation inconsistencies referencing 0.3.0

### Notes
- Version numbering managed by setuptools_scm; publish by tagging `v0.4.0`

---

## [0.3.0] - 2025-08-07

### Added
- PySide6-based modern GUI interface
- Enhanced interactive plotting capabilities with pyqtgraph
- Better performance for real-time spectrum analysis
- Improved dialog systems and user interface components

### Changed
- **BREAKING**: Migrated GUI framework from tkinter to PySide6/Qt
- **BREAKING**: Replaced matplotlib-based plots with pyqtgraph for better performance
- Updated GUI interface for modern Qt-based experience
- Improved cross-platform compatibility with Qt framework

### Removed
- Legacy tkinter-based GUI components
- ttkbootstrap dependency (replaced by Qt styling)

### Technical
- Added PySide6==6.9.0 as GUI dependency
- Added pyqtgraph>=0.13.0 for high-performance plotting
- Updated build system to handle Qt resources
- Improved packaging for Qt-based distribution

### Migration Notes
- Installation is simplified: `pip install snid-sage` installs the full application
- Configuration files remain compatible
- CLI interface unchanged

---

## [0.2.0] - 2025

### Added
- Beta release with core functionality
- Template-based supernova classification
- CLI and tkinter-based GUI interfaces

---
