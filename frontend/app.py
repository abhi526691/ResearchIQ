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

    def pdf_to_images(self, uploaded_file):
        """Convert PDF pages to images."""
        try:
            uploaded_file.seek(0)
            pdf_document = fitz.open(
                stream=uploaded_file.read(), filetype="pdf")
            pages = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                pages.append(img_data)
            return pages
        except Exception as e:
            # Log error silently or handle it without displaying it to the user
            return []

    def pdf_viewer(self, uploaded_file):
        """Display PDF with pagination."""
        try:
            # Ensure a file is uploaded
            if uploaded_file:
                # Convert PDF to images
                pages = self.pdf_to_images(uploaded_file)
                if not pages:  # If conversion fails or no pages, display info
                    st.info(
                        "There was an issue with the PDF file. Please try another.")
                    return

                total_pages = len(pages)

                # Initialize session state for page tracking
                if "current_page" not in st.session_state:
                    st.session_state.current_page = 0

                # Unique identifier for the component
                unique_id = str(uploaded_file.name) + str(total_pages)

                # Display the current page
                caption = f"Page {st.session_state.current_page + 1} of {total_pages}"
                st.image(pages[st.session_state.current_page], caption=caption)

                # Navigation buttons with unique keys
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("< Previous", key=f"prev_button_{unique_id}_{st.session_state.current_page}", disabled=st.session_state.current_page == 0):
                        st.session_state.current_page -= 1
                with col3:
                    if st.button("Next >", key=f"next_button_{unique_id}_{st.session_state.current_page}", disabled=st.session_state.current_page == total_pages - 1):
                        st.session_state.current_page += 1
            else:
                st.info("Upload a PDF file to view it here.")
        except Exception as e:
            # Handle any unexpected error gracefully without showing it to the user
            pass

    def qa_section_with_fixed_input(self):
        # Display chat history in the Q&A section
        self.display_chat_history(st.session_state.chat_history)

        # Ask the user to enter a question
        question = st.text_input("Enter your question:", key="question_input")

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

    def qa_helper(self):
        st.subheader("Ask a Question")
        # Ask the user to enter a question
        question = st.text_input("Enter your question:", key="question_input")

        # Add some CSS to make the text input fixed at the bottom
        st.markdown("""
            <style>
                .stTextInput {
                    position: fixed;
                    bottom: 20px;
                    left: 10px;
                    right: 10px;
                    width: calc(100% - 5px);
                    z-index: 10;
                }
                .chat-history-container {
                    padding-bottom: 80px;  /* To ensure space for the fixed input box */
                }
            </style>
        """, unsafe_allow_html=True)

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
            # st.write(f"Document ID: {st.session_state.document_uid}")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(SUMMARIZER_API_URL, data={
                        "document_uid": st.session_state.document_uid})
                if summary_response.status_code == 200:
                    summary = summary_response.json().get("output")["output"]
                    st.session_state.chat_history = []

                    self.display_summary_chat(summary)
                    # st.rerun()  # Refresh the app to display the new message
                else:
                    st.error("Failed to generate summary.")
        else:
            st.warning("Please upload a PDF file to generate the summary.")

    def display_summary_chat(self, summary):
        st.markdown(f"""
        <div style='text-align: left; margin: 10px;'>
            <p style='background-color: #f0f0f0; padding: 10px; border-radius: 10px;'>
            <strong>{"Generated Summary"}</strong></p>
        </div>
        <div style='text-align: left; margin: 10px;'>
            <p style='background-color: #e0f7fa; padding: 10px; border-radius: 10px;'>
            <strong>{summary}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    def display_chat_history(self, chat_history):
        st.subheader("Chat History")

        # Display chat messages
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

        st.markdown("</div></div>", unsafe_allow_html=True)


class UI(HelperFunction):

    def __init__(self):
        # Set the page title and layout
        st.set_page_config(page_title="ResearchIQ", layout="wide")
        # st.title("PDF Assistant")

        super().__init__()
        # Initialize session state for chat history, document_uid, page, and processed state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if 'document_uid' not in st.session_state:
            st.session_state.document_uid = None

        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = 'Q&A'  # Default tab

        if 'processed' not in st.session_state:
            st.session_state.processed = False  # Track if the file is processed

        if 'show_uploaded_page' not in st.session_state:
            # Flag to control whether to show the upload page
            st.session_state.show_uploaded_page = True

        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None  # Initialize uploaded file

    def clear_session(self):
        # Clear chat history when switching to Summary
        # st.session_state.selected_tab = 'Summary'
        st.session_state.chat_history = []  # Clear chat history

    def driver(self):
        uploaded_file = st.session_state.uploaded_file  # Get the file from session state
        if st.session_state.processed:
            # Once the PDF is processed, load the Q&A and Summary tabs
            qna, summarizer = st.tabs(["Q&A", "Summarizer"])

            with qna:
                pdf_viewer, QnA = st.columns([1, 1])
                with pdf_viewer:
                    self.pdf_viewer(uploaded_file)
                with QnA:
                    # Apply CSS for QnA section to have fixed input at the bottom
                    self.qa_section_with_fixed_input()

            with summarizer:
                pdf_viewer, summary = st.columns([1, 1])
                with pdf_viewer:
                    self.pdf_viewer(uploaded_file)
                with summary:
                    # Display chat history for summarizer
                    self.summary_helper()

    def main(self):
        # Inject the CSS into the Streamlit app
        # st.markdown(self.central_content_css(), unsafe_allow_html=True)

        # Title of the app
        st.title("Research IQ")

        if st.session_state.show_uploaded_page:
            # Centered file uploader with larger size
            uploaded_file = st.file_uploader(
                "Upload your file here!", type=["pdf", "docx", "txt"])

            # Display uploaded file information
            if uploaded_file is not None:
                st.write("File uploaded successfully!")
                if self.process_file(uploaded_file):
                    # Save the uploaded file to session state
                    st.session_state.uploaded_file = uploaded_file
                    st.session_state.processed = True  # Mark PDF as processed
                    st.session_state.show_uploaded_page = False  # Hide the upload page
                    st.rerun()  # Trigger rerun to load the new page after file is processed
                else:
                    st.error("Unable to Process the file")
            else:
                st.write("No file uploaded yet.")
        else:
            # If the file is processed, show the Q&A or Summarizer tab page
            self.driver()


UI().main()
