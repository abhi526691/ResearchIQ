import os
import fitz
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Define the API endpoints
EXTRACTOR_API_URL = os.environ.get("EXTRACTOR_API_URL")
QNA_API_URL = os.environ.get("QNA_API_URL")
SUMMARIZER_API_URL = os.environ.get("SUMMARIZER_API_URL")


class HelperFunction:

    def __init__(self):
        pass

    def central_content_css(self):
        return """
            <style>
                .main {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .block-container {
                    width: 100%;
                    max-width: 1000px;
                    padding: 20px;
                    text-align: center;
                }
                .stFileUploader {
                    width: 100%;
                    border: 2px dashed #0073e6;
                    padding: 50px;
                    background-color: #f5f5f5;
                    border-radius: 10px;
                }
                .stFileUploader label {
                    font-size: 20px;
                }
            </style>
            """

    def display_pdf(self, file):
        file.seek(0)  # Reset the file pointer to the beginning
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        num_pages = pdf_document.page_count
        st.write(f"Total pages: {num_pages}")

        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = pix.tobytes("png")
            st.image(img, caption=f"Page {page_num + 1}")

    def download_pdf(self, uploaded_file, key_suffix):
        st.sidebar.download_button(
            "Download PDF",
            data=uploaded_file.read(),
            file_name=uploaded_file.name,
            mime="application/pdf",
            key=f"download_button_{key_suffix}"
        )

    def process_file(self, uploaded_file):
        # Upload PDF to extractor API
        with st.spinner("Processing the PDF..."):
            uploaded_file.seek(0)  # Reset file pointer to the beginning
            files = {
                "uploaded_file": (uploaded_file.name, uploaded_file, "application/pdf")
            }
            response = requests.post(EXTRACTOR_API_URL, files=files)

        if response.status_code == 200:
            st.session_state.document_uid = response.json().get("document_uid")
            st.success("PDF processed successfully.")
            return True
        else:
            st.error("Failed to process the PDF.")
            return False

    def pdf_viewer(self, uploaded_file):
        self.display_pdf(uploaded_file)
        # self.download_pdf(uploaded_file, key_suffix="viewer")

    def qa_helper(self):
        st.subheader("Ask a Question")
        question = st.text_input("Enter your question:")

        if st.button("Submit Question"):
            if question:
                if st.session_state.document_uid:
                    with st.spinner("Fetching answer..."):
                        qna_response = requests.post(
                            QNA_API_URL, data={"document_uid": st.session_state.document_uid, "question": question})
                    if qna_response.status_code == 200:
                        answer = qna_response.json().get("output")["output"]
                        st.session_state.chat_history.append(
                            ("User: " + question, "Bot: " + answer))
                        st.rerun()  # Refresh the app to display the new message
                    else:
                        st.error("Failed to fetch the answer.")
                else:
                    st.warning("Please upload a PDF file first.")
            else:
                st.warning("Please enter a question.")

    def summary_helper(self):
        st.subheader("Generate Summary")
        if st.session_state.document_uid:
            st.write(f"Document ID: {st.session_state.document_uid}")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(SUMMARIZER_API_URL, data={
                        "document_uid": st.session_state.document_uid})
                if summary_response.status_code == 200:
                    summary = summary_response.json().get("output")["output"]
                    st.session_state.chat_history.append(
                        ("User: Generate Summary", "Bot: " + summary))
                    st.rerun()  # Refresh the app to display the new message
                else:
                    st.error("Failed to generate summary.")
        else:
            st.warning("Please upload a PDF file to generate the summary.")

    def display_chat_history(self, chat_history):
        st.subheader("Chat History")
        for user_msg, bot_msg in chat_history:
            st.markdown(f"""
            <div style='text-align: left; margin: 10px;'>
                <p style='background-color: #f0f0f0; padding: 10px; border-radius: 10px;'>
                <strong>{user_msg}</strong></p>
            </div>
            <div style='text-align: left; margin: 10px;'>
                <p style='background-color: #e0f7fa; padding: 10px; border-radius: 10px;'>
                <strong>{bot_msg}</strong></p>
            </div>
            """, unsafe_allow_html=True)
