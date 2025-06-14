import fitz  # PyMuPDF
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image, ImageFilter, ImageOps
import re
from datetime import datetime
import time

# ---- CONFIG ----
PDF_FOLDER = r"C:\Users\plato\Desktop\Label Database"  # Set to folder containing your PDFs
PROCESSING_FOLDER = os.path.join(PDF_FOLDER, "processing folder")
ARCHIVE_FOLDER = os.path.join(PDF_FOLDER, "archive folder")
ANCHOR_PRICE = "Price:"
POPPLER_PATH = r"C:\poppler\poppler-24.08.0\Library\bin"  # <-- Update to actual Poppler bin path
DEBUG = True
SAVE_IMAGE_DEBUG = True  # Enable saving of rendered image for barcode inspection

os.makedirs(PROCESSING_FOLDER, exist_ok=True)
os.makedirs(ARCHIVE_FOLDER, exist_ok=True)

def extract_text_blocks_from_page(page):
    text = page.get_text()
    return text.splitlines()

def find_item_name_by_price_anchor(lines, anchor_price):
    for i, line in enumerate(lines):
        if anchor_price in line and i - 1 >= 0:
            candidate = lines[i - 1].strip()
            if i - 2 >= 0 and lines[i - 2].strip():
                candidate = lines[i - 2].strip() + " " + candidate
            return candidate.replace("\n", " ").strip()
    return None

def extract_barcode_from_page_obj(page):
    pix = page.get_pixmap(dpi=400)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    width, height = img.size
    barcode_region = img.crop((0, int(height * 0.80), width, height))

    barcode_region = barcode_region.convert("L")
    barcode_region = ImageOps.autocontrast(barcode_region)
    barcode_region = barcode_region.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))
    barcode_region = barcode_region.point(lambda x: 255 if x > 210 else 0, mode='1')

    decoded_objects = decode(barcode_region)

    if not decoded_objects:
        angles = [-2, -1, 1, 2]
        for angle in angles:
            rotated = barcode_region.rotate(angle, expand=True)
            decoded_objects = decode(rotated)
            if decoded_objects:
                break

    if not decoded_objects:
        cv_image = np.array(barcode_region.convert("L"))
        _, thresh = cv2.threshold(cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        dilated = cv2.dilate(thresh, np.ones((3, 3), np.uint8), iterations=1)
        final_image = Image.fromarray(dilated)
        decoded_objects = decode(final_image)

    if not decoded_objects:
        adaptive = cv2.adaptiveThreshold(
            cv_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        adaptive_image = Image.fromarray(adaptive)
        decoded_objects = decode(adaptive_image)

    for obj in decoded_objects:
        if obj.type in ["CODE128", "EAN13", "EAN8"]:
            return obj.data.decode("utf-8")
    return None

def is_filename_already_formatted(filename):
    base = os.path.splitext(filename)[0]
    return bool(re.match(r"^SAGEMB\d{9} ", base))

def does_barcode_exist(barcode):
    for existing_file in os.listdir(PDF_FOLDER):
        if existing_file.lower().endswith(".pdf") and existing_file.startswith(barcode):
            return True
    return False

def split_multipage_pdf(original_path):
    doc = fitz.open(original_path)
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    seen_items = set()
    saved_paths = []

    for i in range(len(doc)):
        page = doc[i]
        lines = extract_text_blocks_from_page(page)
        item_name = find_item_name_by_price_anchor(lines, ANCHOR_PRICE)
        barcode = extract_barcode_from_page_obj(page)

        if not item_name or not barcode:
            continue

        if does_barcode_exist(barcode):
            print(f"⏭ Skipping existing barcode: {barcode}")
            continue

        if item_name in seen_items:
            continue

        seen_items.add(item_name)
        tmp_filename = os.path.join(PROCESSING_FOLDER, f"{base_name}_p{i+1}.pdf")
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        new_doc.save(tmp_filename)
        saved_paths.append(tmp_filename)

    doc.close()
    return saved_paths

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            if is_filename_already_formatted(filename):
                print(f"⏭ Skipping already formatted file: {filename}")
                continue

            full_path = os.path.join(folder_path, filename)
            print(f"\n>>> Processing: {filename}")

            try:
                with fitz.open(full_path) as doc:
                    is_multipage = len(doc) > 1
            except Exception as e:
                print(f"❌ Error opening {filename}: {e}")
                continue

            if is_multipage:
                page_pdfs = split_multipage_pdf(full_path)
                for page_pdf in page_pdfs:
                    was_renamed = process_single_label(page_pdf)
                    if not was_renamed:
                        os.remove(page_pdf)
                try:
                    archive_path = os.path.join(ARCHIVE_FOLDER, os.path.basename(full_path))
                    if os.path.exists(archive_path):
                        base, ext = os.path.splitext(archive_path)
                        timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
                        archive_path = f"{base}{timestamp}{ext}"
                    os.replace(full_path, archive_path)
                except Exception as e:
                    print(f"❌ Failed to move to archive: {e}")
            else:
                process_single_label(full_path)

def process_single_label(full_path):
    lines = extract_text_blocks(full_path)
    item_name = find_item_name_by_price_anchor(lines, ANCHOR_PRICE)
    barcode = extract_barcode_from_page(full_path, 0)
    print("Detected Item Name:", item_name or "❌ Could not detect item name.")
    print("Detected Barcode:", barcode or "❌ Could not decode barcode.")

    if barcode and item_name:
        if does_barcode_exist(barcode):
            print(f"⏭ Skipping existing barcode: {barcode}")
            return False
        clean_name = item_name.replace("/", "-").replace("\\", "-")
        new_filename = f"{barcode} {clean_name}.pdf"
        new_path = os.path.join(PDF_FOLDER, new_filename)
        try:
            os.rename(full_path, new_path)
            print(f"✅ Renamed to: {new_filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to rename: {e}")
    return False

def extract_text_blocks(pdf_path, page_num=0):
    doc = fitz.open(pdf_path)
    full_text = []
    if len(doc) > page_num:
        text = doc[page_num].get_text()
        full_text.extend(text.splitlines())
    doc.close()
    return full_text

def extract_barcode_from_page(pdf_path, page_num):
    return extract_barcode_from_page_obj(fitz.open(pdf_path)[page_num])

if __name__ == "__main__":
    while True:
        print(f"\n⏳ Scanning folder at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        process_folder(PDF_FOLDER)
        time.sleep(300)  # Wait 5 minutes before next scan
