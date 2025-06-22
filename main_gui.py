import tkinter as tk
from tkinter import messagebox
import os
import threading
from barcode_label_cli import find_label_file, print_label
from config import DEFAULT_COPIES
from error_handler import handle_generic_exception, log_error

class LabelPrinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barcode Label Printer")
        self.root.geometry("400x300")

        # Initialize screens
        self.home_frame = tk.Frame(root)
        self.qty_frame = tk.Frame(root)
        self.status_frame = tk.Frame(root)

        # Home screen (barcode input)
        self.barcode_label = tk.Label(self.home_frame, text="Scan or enter barcode:")
        self.barcode_label.pack(pady=(20, 0))
        self.barcode_entry = tk.Entry(self.home_frame, width=40)
        self.barcode_entry.pack()
        self.home_frame.pack(fill='both', expand=True)
        self.barcode_entry.focus_set()
        self.barcode_entry.bind("<Return>", self.goto_qty_screen)

        # Quantity screen
        self.qty_label = tk.Label(self.qty_frame, text="Number of labels to print:")
        self.qty_label.pack(pady=(50, 0))
        self.qty_entry = tk.Entry(self.qty_frame, width=10)
        self.qty_entry.pack()
        self.qty_entry.bind("<Return>", self.print_labels)

        # Status screen
        self.status_label = tk.Label(self.status_frame, text="", font=("Arial", 12), anchor='center', justify='center')
        self.status_label.pack(expand=True)

        # Variables
        self.current_barcode = None

        # Start always-on-top loop
        self.enforce_always_on_top()

    def goto_home_screen(self):
        self.qty_frame.pack_forget()
        self.status_frame.pack_forget()
        self.home_frame.pack(fill='both', expand=True)
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.focus_set()

    def goto_qty_screen(self, event=None):
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            messagebox.showwarning("Input Error", "Please enter a barcode.")
            log_error("Empty barcode input submitted", context="GUI Input")
            return
        self.current_barcode = barcode
        self.home_frame.pack_forget()
        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, str(DEFAULT_COPIES))
        self.qty_entry.select_range(0, tk.END)
        self.qty_frame.pack(fill='both', expand=True)
        self.qty_entry.focus_set()

    def print_labels(self, event=None):
        threading.Thread(target=self._print_labels_task).start()

    def _print_labels_task(self):
        try:
            qty = self.qty_entry.get().strip()
            if not qty.isdigit():
                self.root.after(0, lambda: messagebox.showwarning("Input Error", "Please enter a valid number of copies."))
                log_error("Non-numeric copy quantity", context="GUI Input", input=qty)
                return

            label_path = find_label_file(self.current_barcode)
            self.root.after(0, self.qty_frame.pack_forget)
            self.root.after(0, self.status_frame.pack)

            if label_path:
                product_name = os.path.splitext(os.path.basename(label_path))[0]
                print_label(label_path, int(qty), product_name)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"✅ Printed {qty} copies of {product_name}"
                ))
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text="❌ Label not found in library."
                ))
                log_error("Label not found after scan", context="GUI Flow", barcode=self.current_barcode)

            self.root.after(3000, self.goto_home_screen)
        except Exception as e:
            handle_generic_exception(e, context="Unexpected error during label print operation")

    def enforce_always_on_top(self):
        try:
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(100, lambda: self.root.attributes("-topmost", False))
            if self.root.focus_displayof() is not None:
                self.root.focus_force()
                self.barcode_entry.focus_set()
        except Exception as e:
            log_error(str(e), context="GUI Focus Enforcement")
        self.root.after(2000, self.enforce_always_on_top)

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelPrinterApp(root)
    root.mainloop()
