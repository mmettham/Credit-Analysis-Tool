
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import docx
import re

st.title("Credit Request Analyzer")

# Sidebar Inputs
st.sidebar.header("Request Details")

customer_type = st.sidebar.selectbox(
    "Customer Type",
    ["New Customer", "Existing Customer"]
)

request_type = st.sidebar.selectbox(
    "Request Type",
    ["New Credit Application", "Credit Increase", "Extended Terms"]
)

scope = st.sidebar.selectbox(
    "Scope",
    ["Overall Relationship", "Project Specific"]
)

uploaded_files = st.file_uploader(
    "Upload Supporting Documents",
    type=["pdf", "docx", "xlsx"],
    accept_multiple_files=True
)

# ---------------------
# FILE READERS
# ---------------------
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_excel(file):
    df = pd.read_excel(file)
    return df

# ---------------------
# PDF FINANCIAL EXTRACTION
# ---------------------
def extract_financials(text):

    text = text.lower()

    def find_number(keyword):
        pattern = rf"{keyword}[^0-9\-]*([\-\(]?\d[\d,\.]*)"
        match = re.search(pattern, text)
        if match:
            num = match.group(1)
            num = num.replace(",", "").replace("(", "-").replace(")", "")
            try:
                return float(num)
            except:
                return None
        return None

    return {
        "revenue": find_number("revenue"),
        "net_income": find_number("net income"),
        "ebitda": find_number("ebitda"),
        "total_assets": find_number("total assets"),
        "total_liabilities": find_number("total liabilities"),
        "current_assets": find_number("current assets"),
        "current_liabilities": find_number("current liabilities")
    }

# ---------------------
# SUMMARY FUNCTION
# ---------------------
def generate_summary(all_text):

    text = all_text.lower()
    risks = []

    if "decline" in text or "decrease" in text:
        risks.append("Declining performance indicators")

    if "debt" in text:
        risks.append("Potential leverage concerns")

    if "loss" in text:
        risks.append("Losses mentioned")

    if "concentration" in text:
        risks.append("Customer concentration risk")

    if len(risks) == 0:
        risks.append("No major risks detected (manual review required)")

    summary = "CREDIT REQUEST SUMMARY\n\n"
    summary += f"Customer Type: {customer_type}\n"
    summary += f"Request Type: {request_type}\n"
    summary += f"Scope: {scope}\n\n"

    summary += "KEY RISKS:\n"
    for r in risks:
        summary += "- " + r + "\n"

    summary += "\nRECOMMENDATION:\n"
    summary += "Further credit review recommended before approval."

    return summary


# ---------------------
# MAIN LOGIC
# ---------------------
if uploaded_files:

    all_text = ""

    st.subheader("Document Review")

    for file in uploaded_files:

        st.write(f"Processing: {file.name}")

        # ---------------- PDF ----------------
        if file.name.endswith(".pdf"):

            text = read_pdf(file)
            st.text_area(f"PDF Content - {file.name}", text[:800])

            financials = extract_financials(text)

            st.subheader(f"Extracted Financials - {file.name}")

            for key, value in financials.items():
                if value:
                    st.write(f"{key.replace('_', ' ').title()}: {value}")

            # ---- Ratios ----
            try:
                ca = financials["current_assets"]
                cl = financials["current_liabilities"]
                ta = financials["total_assets"]
                tl = financials["total_liabilities"]
                ni = financials["net_income"]
                rev = financials["revenue"]

                if ca and cl:
                    st.write(f"Current Ratio: {ca / cl:.2f}")

                if ta and tl:
                    st.write(f"Debt Ratio: {tl / ta:.2f}")

                if rev and ni:
                    st.write(f"Net Margin: {(ni / rev):.2%}")

                if ta and rev and ni:
                    z_score = (ni / ta) + (rev / ta)
                    st.write(f"Z-Score (Simplified): {z_score:.2f}")

            except:
                st.warning("Could not calculate ratios.")

            all_text += text

        # ---------------- WORD ----------------
        elif file.name.endswith(".docx"):

            text = read_docx(file)
            st.text_area(f"Word Content - {file.name}", text[:800])
            all_text += text

        # ---------------- EXCEL ----------------
        elif file.name.endswith(".xlsx"):

            df = read_excel(file)
            st.dataframe(df.head())
            all_text += df.to_string()

    # -------- FINAL OUTPUT --------
    if st.button("Generate Analysis"):
        result = generate_summary(all_text)
        st.text_area("Credit Summary", result, height=300)

else:
    st.info("Upload files to begin analysis.")
