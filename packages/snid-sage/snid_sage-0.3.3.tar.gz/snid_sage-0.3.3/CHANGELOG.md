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
