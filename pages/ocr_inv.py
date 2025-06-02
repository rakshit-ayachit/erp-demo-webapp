
import cv2
import pytesseract
import pandas as pd
import re
import streamlit as st
from db import get_invoices_ocr_data

# @st.cache_data
def load_invoice_db():
        # Load CSV file with structured fields
        df = get_invoices_ocr_data()
        return df

# Function to extract data from OCR text using regex
def extract_invoice_data(ocr_text):
    regex_patterns = {
        'vendor': r'^(.*?)\s+invoice\sNo:',
        'invoice_no': r'invoice\sNo\:\s?([^\s]+)',
        'date': r'Date\:\s(\d{2}-\w{3}-\d{4})',
        'gstin_vendor': r'GSTIN\:\s?(\S+)',
        'gstin_client': r'GSTIN\:\s?(\S+)',
        'vendor_id': r'Vendor\sID\s(\S+)',
        'po_amount': r'Purchase\sOrder\sAmount\s\|\s?([¥₹\d,]+(?:\.\d{2})?)',
        'approval_status': r'Approval\sStatus\s\|\s\s?([^\n]+)',
        'vendor_rating': r'Vendor\sRating\s\|\s\s?([\d\.]+)',
        'lead_time': r'Procurement\sLead\sTime\s\|\s(\d+)\sDays',
        'product': r'Products\sand\sServices\sProvided\s([\w\s/-]+)',
        'quantity': r'(\d{3,5})\s(\d+)\s(\d+)',
        'unit_price': r'(\d{1,3}(?:,\d{3})*)\s?',
        'total': r'([\d,]+)\s?License\s\(User\)'
    }

    extracted_data = {}
    for field, pattern in regex_patterns.items():
        match = re.search(pattern, ocr_text)
        extracted_data[field] = match.group(1) if match else None

    return extracted_data

# Function to compare extracted data with database
def compare_with_db(extracted_data, invoice_db):
    vendor = extracted_data['vendor']
    invoice_no = extracted_data['invoice_no']

    match = invoice_db[
        (invoice_db['vendor'] == vendor) & (invoice_db['invoice_no'] == invoice_no)
    ]

    if not match.empty:
        st.success("✅ Invoice matched with the database!")
        return match.iloc[0]
    else:
        st.error("❌ No matching invoice found in the database!")
        return None

# OCR Processing Function
def process_invoice_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    ocr_text = pytesseract.image_to_string(gray, config='--oem 3 --psm 6')
    return ocr_text

# Main Streamlit Page
def ocr_module():
    st.title("🧾 Invoice OCR & Validation")

    uploaded_image = st.file_uploader("Upload Invoice Image", type=["png", "jpg", "jpeg"])

    if uploaded_image is not None:
        with open("uploaded_invoice.png", "wb") as f:
            f.write(uploaded_image.getbuffer())

        ocr_text = process_invoice_image("uploaded_invoice.png")

        st.subheader("🔍 Extracted OCR Text:")
        st.text_area("OCR Text", ocr_text, height=200)

        extracted_data = extract_invoice_data(ocr_text)

        st.subheader("📝 Extracted Data:")
        st.write(extracted_data)

        invoice_db = load_invoice_db()

        match_result = compare_with_db(extracted_data, invoice_db)

        if match_result is not None:
            st.subheader("📊 Matching Invoice Details:")
            st.write(match_result)
