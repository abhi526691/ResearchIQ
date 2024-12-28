import streamlit as st
from utils import HelperFunction


class Frontend(HelperFunction):

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

    # def qna(self):
    #     # Clear chat history when switching to Q&A
    #     st.session_state.selected_tab = 'Q&A'
    #     st.session_state.chat_history = []  # Clear chat history

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
                    # Display chat history
                    self.display_chat_history(st.session_state.chat_history)
                    self.qa_helper()

            with summarizer:
                pdf_viewer, summary = st.columns([1, 1])
                with pdf_viewer:
                    self.pdf_viewer(uploaded_file)
                with summary:
                    # Display chat history
                    self.summary_helper()
                # self.qna()


    def main(self):
        # Inject the CSS into the Streamlit app
        st.markdown(self.central_content_css(), unsafe_allow_html=True)

        # Title of the app
        st.title("Document Upload")

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


Frontend().main()
