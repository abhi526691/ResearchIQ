import streamlit as st
import requests
from PIL import Image

# Define the API endpoints
EXTRACTOR_API_URL = "http://127.0.0.1:8000/document_processing/file/"
QNA_API_URL = "http://127.0.0.1:8000/document_processing/qna/"
SUMMARIZER_API_URL = "http://127.0.0.1:8000/document_processing/summary/"

# Streamlit UI
st.set_page_config(page_title="PDF Assistant", layout="wide")
st.title("PDF Assistant")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    # Display the uploaded PDF
    st.subheader("Uploaded PDF:")
    pdf_viewer, options_view = st.columns([3, 1])

    # Show the PDF on the left
    with pdf_viewer:
        st.write("Displaying the PDF...")
        st.download_button(
            "Download PDF",
            data=uploaded_file.read(),
            file_name=uploaded_file.name,
            mime="application/pdf"
        )

    # Show options for QnA or Summarizer on the right
    with options_view:
        st.subheader("Options")

        # Upload PDF to extractor API
        with st.spinner("Processing the PDF..."):
            response = requests.post(EXTRACTOR_API_URL, files={
                                     "uploaded_file": uploaded_file})
        print("response", response)
        if response.status_code == 200:
            document_uid = response.json().get("document_uid")
            st.success("PDF processed successfully.")
        else:
            st.error("Failed to process the PDF.")

        # Options for QnA or Summarizer
        option = st.radio("Select an action:", ["QnA", "Summarizer"])

        if option == "QnA":
            st.subheader("Ask a Question")
            question = st.text_input("Enter your question:")
            if st.button("Submit Question"):
                if question:
                    with st.spinner("Fetching answer..."):
                        qna_response = requests.post(
                            QNA_API_URL, data={"document_uid": document_uid, "question": question})
                    if qna_response.status_code == 200:
                        answer = qna_response.json().get("output")
                        st.success(f"Answer: {answer}")
                    else:
                        st.error("Failed to fetch the answer.")
                else:
                    st.warning("Please enter a question.")

        elif option == "Summarizer":
            st.subheader("Summary")
            if st.button("Get Summary"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(SUMMARIZER_API_URL, data={
                                                     "document_uid": document_uid})
                if summary_response.status_code == 200:
                    summary = summary_response.json().get("output")
                    st.success(f"Summary: {summary}")
                else:
                    st.error("Failed to generate summary.")
