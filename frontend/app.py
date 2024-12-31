import streamlit as st

# Function to update the session state with new messages


def add_message():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    st.session_state['messages'].append(st.session_state['input_text'])
    st.session_state['input_text'] = ''


# Display the messages in a scrollable container at the top
if 'messages' in st.session_state:
    with st.container():
        st.markdown("### Messages")
        for msg in reversed(st.session_state['messages']):
            st.write(msg)

# Text box for user input
with st.container():
    st.text_input("Type your message here:",
                  key='input_text', on_change=add_message)

# Style to fix the position of the input text box at the bottom of the page
st.markdown(
    """
    <style>
    .stTextInput {
        position: fixed;
        bottom: 0;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
