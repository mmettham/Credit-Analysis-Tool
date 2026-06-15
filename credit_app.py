
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import docx

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

# File Readers
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

# Analysis Function
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
    summary += "Customer Type: " + customer_type + "\n"
    summary += "Request Type: " + request_type + "\n"
    summary += "Scope: " + scope + "\n\n"

    summary += "KEY RISKS:\n"
    for r in risks:
        summary += "- " + r + "\n"

    summary += "\nRECOMMENDATION:\n"
    summary += "Further credit review recommended before approval."

    return summary


# Main Logic
if uploaded_files:

    all_text = ""

    st.subheader("Document Review")

    for file in uploaded_files:

        st.write("Processing:", file.name)

        if file.name.endswith(".pdf"):
            text = read_pdf(file)
            st.text_area(f"PDF Content - {file.name}", text[:800])
            all_text += text

        elif file.name.endswith(".docx"):
            text = read_docx(file)
            st.text_area(f"Word Content - {file.name}", text[:800])
            all_text += text

        elif file.name.endswith(".xlsx"):
            df = read_excel(file)
            st.dataframe(df.head())
            all_text += df.to_string()

    if st.button("Generate Analysis"):
        result = generate_summary(all_text)
        st.text_area("Credit Summary", result, height=300)

else:
    st.info("Upload files to begin analysis.")
