# 📦 Changelog – Barcode Label Printing Program

All notable changes to this project will be documented in this file.

## [0.1.5] – 2025-05-28
### Added
- Initial Inno Setup installer with user-local installation path (`%LOCALAPPDATA%\LabelPrinter`)
- Bundled SumatraPDF 3.5.2 portable version into installer
- Created default writable `Label Library` folder at install time
- Optional post-installation prompt to install Brother TD-4000 printer driver
- Created auto-detect mechanism for Python version and PyInstaller path in rebuild script
- Created `config.ini` with dynamic label path pointing to local user documents folder
- Added robust error handling and log rotation in `error_handler.py`
- GUI error popups on file/printer failure using `tkinter.messagebox`

### Changed
- Refactored config path to ensure editable `config.ini` post-install
- Relocated label library from program folder to writable location to prevent permission errors
- Refactored `config.py` to dynamically parse `%LOCALAPPDATA%` using `os.environ.get()`
- Replaced default installation path to user-local app folder instead of `C:\Program Files\`

### Fixed
- Installer hanging issue by removing `Run` directive for SumatraPDF
- Path parsing error when using `{localappdata}` instead of resolving at runtime
- Config loading fallback between bundled and installed environments

---

## [v0.1.2] – GUI Refinement & Logging Enhancement
**Released:** 2025-05-28

### Added
- NDJSON structured logging format with timestamp and context metadata
- Monthly log rotation based on first log entry's timestamp
- GUI barcode and quantity entry fields auto-selected and focused
- Always-on-top behavior with window refresh loop
- GUI displays cleaned product name on successful print
- Graceful GUI error messaging integrated with error handler module

### Changed
- Fully removed dependency on Adobe Acrobat Reader
- Temp files now cleaned safely with retry-safe logic

---

## [v0.1.1] – Configuration Refactor
**Released:** 2025-05

### Added
- `.ini` config file for label path, SumatraPDF path, and printer name
- `config.py` for modularized config access
- `error_handler.py` module for GUI + CLI-safe error handling
- Human-readable and machine-parseable error logging (pre-NDJSON)

### Changed
- Refactored `core` and `main_gui` to remove hardcoded paths
- Modularized code structure across four separate `.py` files

---

## [v0.1.0] – Prototype Release
**Released:** 2025-04

### Added
- Barcode input via CLI and GUI
- Static label lookup from filename (`barcode Name.pdf`)
- PDF copying to match desired print quantity using PyPDF2
- GUI for scan entry and quantity prompt
- Printing via Adobe Acrobat or SumatraPDF
- Core functionality runs on Windows with hardcoded paths
