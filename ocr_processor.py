import pytesseract
from pdf2image import convert_from_path
import re
import json

# Proper paths (IMPORTANT)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\ASUS TUF\Downloads\Release-25.11.0-0\poppler-25.11.0\Library\bin"


# -------------------------------------------------------------
# STEP 1 — Convert PDF → text using OCR
# -------------------------------------------------------------
def pdf_to_text(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    full_text = ""

    for page in pages:
        text = pytesseract.image_to_string(page)
        full_text += text + "\n"

    return full_text


# -------------------------------------------------------------
# STEP 2 — Smart Parsing of messy documents
# -------------------------------------------------------------
def parse_company_name(text):
    patterns = [
        r"Registered Entity Name[:\-]?\s*(.*)",
        r"Company Name[:\-]?\s*(.*)",
        r"Entity[:\-]?\s*(.*)",
        r"Name[:\-]?\s*(.*)"
    ]
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            return m.group(1).strip()
    return "Unknown Company"


def parse_registration_number(text):
    m = re.search(r"(ID|Reg|Registration|Number)[:\-]?\s*([A-Za-z0-9\-]+)", text, re.I)
    if m:
        return m.group(2).strip()
    return "Unknown"


def parse_jurisdiction(text):
    m = re.search(r"(Country|Jurisdiction)[:\-]?\s*(.*)", text, re.I)
    if m:
        return m.group(2).strip()
    return None


def parse_shareholders(text):
    shareholders = []

    # Examples matched:
    # - BlueTomorrow Holdings Ltd (Bermuda) — approx. seventy-two per cent (72%)
    # - Horizon Ventures BV (Netherlands) – 16%
    # Owner: Dr. Eleanor Grant — 100%
    patterns = [
        r"-\s*(.*?)\s*\((.*?)\).*?([0-9]+)[ ]*%",
        r"Owner[:\-]?\s*(.*?)\s*[—-]\s*([0-9]+)%",
        r"(.*?)[ ]*—[ ]*([0-9]+)%"
    ]

    for p in patterns:
        matches = re.findall(p, text)
        for match in matches:
            if len(match) == 3:
                name, country, pct = match
            else:
                name, pct = match
                country = None

            shareholders.append({
                "name": name.strip(),
                "type": "company" if not re.search(r"Mr|Ms|Dr", name, re.I) else "individual",
                "ownership_percentage": float(pct),
                "country": country,
                "registration_number": None,
                "nationality": None,
                "dob": None,
                "sub_entity": None
            })

    return shareholders


# -------------------------------------------------------------
# STEP 3 — Build FINAL JSON in your backend format
# -------------------------------------------------------------
def ocr_to_company_json(pdf_path: str):
    text = pdf_to_text(pdf_path)

    company_json = {
        "company_name": parse_company_name(text),
        "registration_number": parse_registration_number(text),
        "jurisdiction": parse_jurisdiction(text),
        "industry": None,
        "business_address": None,
        "shareholders": parse_shareholders(text)
    }

    return company_json


# -------------------------------------------------------------
if __name__ == "__main__":
    file = r"C:\Users\ASUS TUF\Downloads\hard_A_harborline.pdf"
    result = ocr_to_company_json(file)
    print(json.dumps(result, indent=4))
