import streamlit as st
import fitz  # PyMuPDF

def pdf_to_images(uploaded_file):
    """Convert PDF pages to images."""
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    pages = []
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img_data = pix.tobytes("png")
        pages.append(img_data)
    return pages

def display_pdf_with_pagination(uploaded_file):
    """Display PDF with pagination."""
    if uploaded_file is not None:
        # Convert PDF to images
        pages = pdf_to_images(uploaded_file)
        total_pages = len(pages)

        # Initialize session state for page tracking
        if "current_page" not in st.session_state:
            st.session_state.current_page = 0

        # Display the current page
        st.image(pages[st.session_state.current_page], caption=f"Page {st.session_state.current_page + 1} of {total_pages}")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("< Previous", disabled=st.session_state.current_page == 0):
                st.session_state.current_page -= 1
        with col3:
            if st.button("Next >", disabled=st.session_state.current_page == total_pages - 1):
                st.session_state.current_page += 1
    else:
        st.warning("Please upload a PDF file.")

# Streamlit App Code
st.title("PDF Viewer with Pagination")
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
display_pdf_with_pagination(uploaded_file)
