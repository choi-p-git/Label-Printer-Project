# 📌 Barcode Label Printing Program – Development Roadmap

---

## v0.1.0 – Prototype Release

**Scope:**  
Local-only label lookup and printing with hardcoded settings.

- Local-only label lookup and printing  
- GUI with barcode entry, quantity selection, and print trigger  
- Uses Adobe Acrobat or SumatraPDF for PDF rendering  
- Hardcoded paths (manual edits only)  
- Windows-only compatibility  

---

## v0.1.1 – Configuration Refactor

**Scope:**  
Refactor for modular configuration and stability.

- Implement `.ini` config file for:
  - Reader path  
  - Label folder  
  - Default printer  
- Graceful error messages for missing files  
- File existence validation before print  
- Code cleanup and modularization  

---

## v0.1.2 – GUI Refinement & Logging Enhancement

**Scope:**  
Improves user experience, structured diagnostics, and internal stability.

- Enforce always-on-top GUI behavior with refresh loop  
- Auto-select barcode and quantity fields for fast workflow  
- Add barcode scan result confirmation in UI  
- Implement NDJSON structured logging (timestamp, context, metadata)  
- Enable monthly error log rotation based on first entry  
- Graceful GUI-integrated error feedback using modular error handler  
- Remove Acrobat dependency; SumatraPDF-exclusive  
- Confirm print success/failure with cleaned product name  
- Safe temp file cleanup with retry-safe `os.unlink`  

---

## v0.1.5 – Installer & Label Directory Selection

**Scope:**  
Deployment preparation and accessibility for non-technical users.

- Windows installer packaging using PyInstaller + Inno Setup  
- Prompts user to select label directory or creates a default on first run  
- Installer writes selection to the `.ini` config file  
- Program always reads paths from the config at runtime  
- Improved accessibility for non-technical users  

---

## v0.2.0 – Linux CLI Compatibility & Kiosk Integration

**Scope:**  
Linux support, CLI operation, kiosk compatibility.

- Develop CLI version with barcode + quantity as command-line args  
- Enable silent print execution without GUI  
- Compatible with Fedora-based kiosks running company-specific web interface  
- Supports shell calls or backend API triggers  
- Basic stdout logging for print success/failure  
- Foundation for future Linux print daemon (planned for v1.0.0)  

---

## v0.2.5 – Remote Label Sync via Menu Builder Integration

**Scope:**  
Server integration with company Menu Builder – Print Shop system.

- Integrate with Menu Builder flagging for “label-ready” recipes  
- Backend generates venue-specific label libraries  
- Labels hosted on company server with venue-level access  
- Local sync via API (manual or scheduled pull)  
- Smart fallback logic:
  - Primary: Use local label file  
  - Secondary: Fetch from server if missing or corrupted  
  - Tertiary: Trigger label generation via Menu Builder  

_Note: Coordinated with Menu Builder platform development._  

---

## v1.0.0 – Full Operational Release

**Scope:**  
Finalize features, expand GUI/UX, production-grade deployment.

- Refactor GUI to include optional embedded label preview  
- Expand folder handling (archived vs active, subfolders)  
- Add optional sync scheduling (startup or interval)  
- Improve update/deployment mechanisms (silent updates, installer refresh)  
- Consolidate error handling, logging, and fallback logic into robust service  
- Tag and version final release as kiosk- and production-ready  
