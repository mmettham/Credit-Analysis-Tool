import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import docx

st.set_page_config(page_title="Credit Request Analyzer", layout="wide")

st.title("Credit Request Analyzer")

# -----------------------------
# USER INPUTS
# -----------------------------
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
    "Upload Supporting Documents (Excel, PDF, Word)",
    type=["xlsx", "pdf", "docx"],
    accept_multiple_files=True
)

# -----------------------------
# FILE READERS
# -----------------------------
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

# -----------------------------
# SIMPLE ANALYSIS LOGIC
# -----------------------------
def generate_summary(all_text):
    text_lower = all_text.lower()
    risks = []

    if "decline" in text_lower or "decrease" in text_lower:
        risks.append("Potential declining performance detected")

    if "debt" in text_lower and "increase" in text_lower:
        risks.append("Rising leverage indicators")

    if "loss" in text_lower:
        risks.append("Losses mentioned in financials")

    if "concentration" in text_lower:
        risks.append("Customer concentration risk noted")

    if len(risks) == 0:
        risks.append("No obvious risks detected (manual review required)")

    summary = f"""
CREDIT REQUEST SUMMARY

Customer Type: {customer_type}
Request Type: {request_type}
Scope: {scope}

--------------------------------

KEY OBSERVATIONS:
- Documents successfully processed
- Initial data extraction completed

RISK INDICATORS:
- {"\n- ".join(risks)}

--------------------------------

PRELIMINARY RECOMMENDATION:
Further financial and credit review recommended prior to final approval.
"""

    return summary

# -----------------------------
# MAIN APP LOGIC
# -----------------------------
if uploaded_files:

    all_text = ""

    st.subheader("File Review & Extracted Content")

    for file in uploaded_files:

        st.markdown(f"### {file.name}")

        if file.name.endswith(".pdf"):
            text = read_pdf(file)
            st.text_area("PDF Extract", text[:1000], height=200)
            all_text += text

        elif file.name.endswith(".docx"):
            text = read_docx(file)
            st.text_area("Word Extract", text[:1000], height=200)
            all_text += text

        elif file.name.endswith(".xlsx"):
            df = read_excel(file)
            st.write("Excel Preview:")
            st.dataframe(df.head())
            all_text += df.to_string()

    st.subheader("Credit Risk Summary")

    if st.button("Generate Analysis"):
        summary = generate_summary(all_text)
        st.text_area("Analysis Output", summary, height=300)

else:
    st.info("Upload files to begin analysis.")
``
