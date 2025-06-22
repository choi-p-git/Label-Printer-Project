import os
import json
from datetime import datetime
from tkinter import messagebox

LOG_PATH = "error.log"

# --- Log Rotation ---
def rotate_log_by_month():
    if os.path.exists(LOG_PATH):
        current_month = datetime.now().strftime("%Y-%m")
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if first_line:
                try:
                    log_entry = json.loads(first_line)
                    entry_month = log_entry.get("timestamp", "").split("T")[0][:7]
                    if entry_month and entry_month != current_month:
                        archive_name = f"error_{entry_month}.log"
                        os.rename(LOG_PATH, archive_name)
                except Exception:
                    pass

rotate_log_by_month()
# Ensure error log file exists at startup
if not os.path.exists(LOG_PATH):
    open(LOG_PATH, 'a').close()


def show_error_gui(message: str, title: str = "Error"):
    """Display an error message in a pop-up GUI window."""
    try:
        messagebox.showerror(title, message)
    except Exception:
        pass  # fallback if GUI not available (CLI mode)

def log_error(message: str, context: str = "General", **kwargs):
    """Append a structured JSON log entry to the error log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": "error",
        "context": context,
        "message": message,
    }
    log_entry.update(kwargs)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass

def handle_file_not_found(filepath: str):
    msg = f"Label file not found: {filepath}"
    log_error("Label file not found", context="Lookup", path=filepath)
    show_error_gui(msg)

def handle_printer_not_found(printer_name: str):
    msg = f"Printer not found: {printer_name}"
    log_error("Printer not found", context="Printer", printer=printer_name)
    show_error_gui(msg)

def handle_generic_exception(e: Exception, context: str = ""):
    msg = f"An error occurred.\nContext: {context}\n\nDetails: {str(e)}"
    log_error(str(e), context=context)
    show_error_gui(msg)
