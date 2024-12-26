import streamlit as st
from utils import HelperFunction


class Frontend(HelperFunction):

    def __init__(self):
        # Set the page title and layout
        st.set_page_config(page_title="ResearchIQ", layout="wide")
        st.title("PDF Assistant")

        super().__init__()
        # Initialize session state for chat history and document_uid
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if 'document_uid' not in st.session_state:
            st.session_state.document_uid = None

        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = 'Q&A'  # Default tab

        if 'processed' not in st.session_state:
            st.session_state.processed = False  # Track if the file is processed

        self.uploaded_file = None

    def qna(self):
        if st.button('Q&A', key='qna'):
            # Clear chat history when switching to Q&A
            st.session_state.selected_tab = 'Q&A'
            st.session_state.chat_history = []  # Clear chat history

    def summary(self):
        if st.button('Summary', key='summary'):
            # Clear chat history when switching to Summary
            st.session_state.selected_tab = 'Summary'
            st.session_state.chat_history = []  # Clear chat history

    def driver(self, uploaded_file):
        if st.session_state.processed:
            # Once the PDF is processed, load the Q&A and Summary tabs
            qna, summarizer = st.tabs(["Q&A", "Summarizer"])
            with qna:
                pdf_viewer, QnA = st.columns([1, 1])
                with pdf_viewer:
                    self.pdf_viewer(uploaded_file)
                with QnA:
                    self.qna()

            with summarizer:
                pdf_viewer, summary = st.columns([1, 1])
                with pdf_viewer:
                    self.pdf_viewer(uploaded_file)
                with summary:
                    self.summary()

            # Display chat history
            self.display_chat_history(st.session_state.chat_history)

            # Q&A Section: Takes a question input
            if st.session_state.selected_tab == 'Q&A':
                self.qa_helper()

            # Summary Section: Calls the API without a question input
            elif st.session_state.selected_tab == 'Summary':
                self.summary_helper()

    def main(self):
        # Inject the CSS into the Streamlit app
        st.markdown(self.central_content_css(), unsafe_allow_html=True)

        # Title of the app
        st.title("Document Upload")

        # Centered file uploader with larger size
        self.uploaded_file = st.file_uploader(
            "Upload your file here!", type=["pdf", "docx", "txt"])

        # Display uploaded file information
        if self.uploaded_file is not None:
            # st.write("File uploaded successfully!")
            if self.process_file(self.uploaded_file):
                st.session_state.processed = True  # Mark PDF as processed
                st.rerun()  # Trigger rerun to load the new page after file is processed
            else:
                st.error("Unable to Process the file")
        else:
            st.write("No file uploaded yet.")

        # If the file is processed, show the Q&A or Summarizer tab page
        if st.session_state.processed:
            self.driver(self.uploaded_file)


Frontend().main()
