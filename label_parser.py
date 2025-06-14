import fitz  # PyMuPDF
import os
import cv2
import numpy as np
from pdf2image import convert_from_path
from pyzbar.pyzbar import decode
from PIL import Image, ImageFilter, ImageOps
import re

# ---- CONFIG ----
PDF_FOLDER = r"C:\Users\plato\Desktop\Daily Labels"  # Set to folder containing your PDFs
ANCHOR_PRICE = "Price:"
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"  # <-- Update to actual Poppler bin path
DEBUG = True
SAVE_IMAGE_DEBUG = True  # Enable saving of rendered image for barcode inspection


def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []
    if len(doc) > 0:
        text = doc[0].get_text()  # Only parse the first page
        full_text.extend(text.splitlines())
    return full_text


def find_item_name_by_price_anchor(lines, anchor_price):
    for i, line in enumerate(lines):
        if anchor_price in line and i - 1 >= 0:
            candidate = lines[i - 1].strip()
            # Check if line before that is also part of the name
            if i - 2 >= 0 and lines[i - 2].strip():
                candidate = lines[i - 2].strip() + " " + candidate
            return candidate.replace("\n", " ").strip()
    return None


def extract_barcode_from_pdf(pdf_path):
    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH,
        first_page=1,
        last_page=1,
        dpi=400  # High resolution for decoding accuracy
    )
    if not images:
        return None
    first_page_image = images[0]

    # Crop bottom 20% of image to isolate barcode
    width, height = first_page_image.size
    barcode_region = first_page_image.crop((0, int(height * 0.80), width, height))

    # Convert to grayscale and enhance contrast
    barcode_region = barcode_region.convert("L")
    barcode_region = ImageOps.autocontrast(barcode_region)

    # Apply sharpening filter to improve barcode clarity
    barcode_region = barcode_region.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=2))

    # Apply binarization (thresholding)
    threshold = 210
    barcode_region = barcode_region.point(lambda x: 255 if x > threshold else 0, mode='1')

    # Try decoding from barcode region
    decoded_objects = decode(barcode_region)

    # Fallback: Try rotation if initial crop fails
    if not decoded_objects:
        angles = [-2, -1, 1, 2]  # try small angle corrections
        for angle in angles:
            rotated = barcode_region.rotate(angle, expand=True)
            decoded_objects = decode(rotated)
            if decoded_objects:
                break

    # Fallback: Try OpenCV enhancements if Pillow fails
    if not decoded_objects:
        cv_image = np.array(barcode_region.convert("L"))
        _, thresh = cv2.threshold(cv_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        final_image = Image.fromarray(dilated)
        decoded_objects = decode(final_image)

    # Fallback: Try adaptive thresholding if dilation fails
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

    # Fallback: Try decoding from full grayscale image if all else fails
    if not decoded_objects:
        fallback_image = first_page_image.convert("L")
        decoded_objects = decode(fallback_image)

        # Save debug images only if decoding failed
        if SAVE_IMAGE_DEBUG:
            debug_image_path = os.path.splitext(pdf_path)[0] + "_rendered.png"
            barcode_debug_path = os.path.splitext(pdf_path)[0] + "_barcode_crop.png"
            first_page_image.save(debug_image_path)
            barcode_region.convert("L").save(barcode_debug_path)  # Save as L mode for better viewing
            print(f"Saved rendered image to: {debug_image_path}")
            print(f"Saved barcode crop image to: {barcode_debug_path}")

    for obj in decoded_objects:
        if obj.type in ["CODE128", "EAN13", "EAN8"]:  # Accept common formats
            return obj.data.decode("utf-8")
    return None


def is_filename_already_formatted(filename):
    base = os.path.splitext(filename)[0]
    return bool(re.match(r"^SAGEMB\d{9} ", base))


def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            if is_filename_already_formatted(filename):
                print(f"⏭ Skipping already formatted file: {filename}")
                continue

            full_path = os.path.join(folder_path, filename)
            print(f"\n>>> Processing: {filename}")
            lines = extract_text_blocks(full_path)
            item_name = find_item_name_by_price_anchor(lines, ANCHOR_PRICE)
            barcode = extract_barcode_from_pdf(full_path)
            print("Detected Item Name:", item_name or "❌ Could not detect item name.")
            print("Detected Barcode:", barcode or "❌ Could not decode barcode.")

            if barcode and item_name:
                clean_name = item_name.replace("/", "-").replace("\\", "-")  # Sanitize filename
                new_filename = f"{barcode} {clean_name}.pdf"
                new_path = os.path.join(folder_path, new_filename)
                try:
                    os.rename(full_path, new_path)
                    print(f"✅ Renamed to: {new_filename}")
                except Exception as e:
                    print(f"❌ Failed to rename: {e}")


if __name__ == "__main__":
    process_folder(PDF_FOLDER)
