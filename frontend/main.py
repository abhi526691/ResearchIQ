import streamlit as st
import requests
import fitz  # PyMuPDF
from io import BytesIO

# Define the API endpoints
EXTRACTOR_API_URL = "http://127.0.0.1:8000/document_processing/file/"
QNA_API_URL = "http://127.0.0.1:8000/document_processing/qna/"
SUMMARIZER_API_URL = "http://127.0.0.1:8000/document_processing/summary/"

# Streamlit UI
st.set_page_config(page_title="PDF Assistant", layout="wide")
st.title("PDF Assistant")

# Function to display PDF using PyMuPDF


def display_pdf(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    num_pages = pdf_document.page_count
    st.write(f"Total pages: {num_pages}")
    for page_num in range(num_pages):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = pix.tobytes("png")
        st.image(img, caption=f"Page {page_num + 1}")


# Initialize session state for chat history and document_uid
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'document_uid' not in st.session_state:
    st.session_state.document_uid = None

if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = 'Q&A'  # Default tab

# Sidebar for PDF upload
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    # Display the uploaded PDF
    st.subheader("Uploaded PDF:")
    pdf_viewer, chat_input = st.columns(
        [1.5, 2.5])  # Adjusted column proportions

    # Show the PDF on the left
    with pdf_viewer:
        display_pdf(uploaded_file)
        st.sidebar.download_button(
            "Download PDF",
            data=uploaded_file.read(),
            file_name=uploaded_file.name,
            mime="application/pdf"
        )

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
    else:
        st.error("Failed to process the PDF.")

    # Chat section with navigation options (Q&A and Summary)
    with chat_input:
        # Create the navigation buttons for Q&A and Summary
        tab_button1, tab_button2 = st.columns([1, 1])

        with tab_button1:
            if st.button('Q&A', key='qna'):
                # Clear chat history when switching to Q&A
                st.session_state.selected_tab = 'Q&A'
                st.session_state.chat_history = []  # Clear chat history

        with tab_button2:
            if st.button('Summary', key='summary'):
                # Clear chat history when switching to Summary
                st.session_state.selected_tab = 'Summary'
                st.session_state.chat_history = []  # Clear chat history

        # Display chat history
        st.subheader("Chat History")
        for user_msg, bot_msg in st.session_state.chat_history:
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

        # Q&A Section: Takes a question input
        if st.session_state.selected_tab == 'Q&A':
            st.subheader("Ask a Question")
            question = st.text_input("Enter your question:")

            if st.button("Submit Question"):
                if question:
                    if st.session_state.document_uid:
                        with st.spinner("Fetching answer..."):
                            qna_response = requests.post(
                                QNA_API_URL, data={"document_uid": st.session_state.document_uid, "question": question})
                        if qna_response.status_code == 200:
                            answer = qna_response.json().get("output")[
                                "output"]
                            st.session_state.chat_history.append(
                                ("User: " + question, "Bot: " + answer))
                            st.rerun()  # Refresh the app to display the new message
                        else:
                            st.error("Failed to fetch the answer.")
                    else:
                        st.warning("Please upload a PDF file first.")
                else:
                    st.warning("Please enter a question.")

        # Summary Section: Calls the API without a question input
        elif st.session_state.selected_tab == 'Summary':
            st.subheader("Generate Summary")
            if st.session_state.document_uid:
                st.write(f"Document ID: {st.session_state.document_uid}")
                if st.button("Generate Summary"):
                    with st.spinner("Generating summary..."):
                        summary_response = requests.post(SUMMARIZER_API_URL, data={
                                                         "document_uid": st.session_state.document_uid})
                    if summary_response.status_code == 200:
                        summary = summary_response.json().get("output")[
                            "output"]
                        st.session_state.chat_history.append(
                            ("User: Generate Summary", "Bot: " + summary))
                        st.rerun()  # Refresh the app to display the new message
                    else:
                        st.error("Failed to generate summary.")
            else:
                st.warning("Please upload a PDF file to generate the summary.")

else:
    st.warning("Please upload a PDF file to proceed.")
