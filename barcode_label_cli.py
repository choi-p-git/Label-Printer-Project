import os
import glob
import time
import tempfile
import subprocess
import win32print
from PyPDF2 import PdfReader, PdfWriter
from config import PRINTER_NAME, PRINTER_DRIVER, LABEL_DIRECTORY, SUMATRA_PATH
from error_handler import handle_file_not_found, handle_printer_not_found, handle_generic_exception, log_error

SUPPORTED_EXTENSIONS = [".pdf"]

def find_label_file(barcode: str) -> str:
    """Search for a label file that starts with the given barcode."""
    for ext in SUPPORTED_EXTENSIONS:
        pattern = os.path.join(LABEL_DIRECTORY, f"{barcode} *{ext}")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    log_error("No label file match found", context="Lookup", barcode=barcode)
    return None

def get_printer_port(printer_name: str) -> str:
    """Find the port name (e.g., USB001) for a given printer name."""
    flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    printers = win32print.EnumPrinters(flags)
    for printer in printers:
        _, _, name, _ = printer
        if printer_name.lower() in name.lower():
            try:
                hprinter = win32print.OpenPrinter(name)
                info = win32print.GetPrinter(hprinter, 2)
                win32print.ClosePrinter(hprinter)
                return info["pPortName"]
            except Exception as e:
                handle_generic_exception(e, context="Querying printer port", printer=printer_name)
                return None
    handle_printer_not_found(printer_name)
    return None

def print_label(file_path: str, copies: int = 1, product_name: str = "label"):
    if not os.path.exists(file_path):
        handle_file_not_found(file_path)
        return

    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        if not reader.pages:
            raise ValueError("PDF has no pages.")
        page = reader.pages[0]
        for _ in range(copies):
            writer.add_page(page)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            writer.write(tmp_file)
            tmp_file_path = tmp_file.name

    except Exception as e:
        handle_generic_exception(e, context="Building multi-page temporary PDF", file_path=file_path)
        return

    printer_port = get_printer_port(PRINTER_NAME)
    if not printer_port:
        return

    try:
        print(f"🖨️ Printing {copies} copies of: {product_name} → {PRINTER_NAME} via SumatraPDF")
        command = f'"{SUMATRA_PATH}" -print-to "{PRINTER_NAME}" -silent "{tmp_file_path}"'
        subprocess.run(command, shell=True)
        time.sleep(1)
    except Exception as e:
        handle_generic_exception(e, context="Executing SumatraPDF print command", command=command)
    finally:
        try:
            os.unlink(tmp_file_path)
            print("🧹 Temporary file cleaned up.")
        except Exception as e:
            handle_generic_exception(e, context="Cleaning up temporary file", tmp_path=tmp_file_path)
