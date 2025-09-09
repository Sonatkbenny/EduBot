"""
UI components for EduBot
"""
import streamlit as st

def create_header(title: str, description: str = ""):
    """Create a styled page header with title and description"""
    st.markdown(f"""
    <div style='padding: 10px 0 20px 0;'>
        <h1 style='color: #2563eb; margin-bottom: 0;'>{title}</h1>
        <p style='color: #6b7280; margin-top: 0;'>{description}</p>
    </div>
    """, unsafe_allow_html=True)

def create_error_message(message: str):
    """Display an error message"""
    st.error(message, icon="🚨")

def create_success_message(message: str):
    """Display a success message"""
    st.success(message, icon="✅")

def create_warning_message(message: str):
    """Display a warning message"""
    st.warning(message, icon="⚠️")

def create_info_message(message: str):
    """Display an info message"""
    st.info(message, icon="ℹ️")

def create_loading_spinner(text: str = "Processing..."):
    """Create a loading spinner with custom text"""
    return st.spinner(text)

def create_button(label: str, key: str = None, **kwargs):
    """Create a styled button"""
    return st.button(label, key=key, **kwargs)

def create_selectbox(label: str, options: list, key: str = None, **kwargs):
    """Create a styled selectbox"""
    return st.selectbox(label, options, key=key, **kwargs)

def create_text_input(label: str, key: str = None, **kwargs):
    """Create a styled text input"""
    return st.text_input(label, key=key, **kwargs)

def create_text_area(label: str, key: str = None, **kwargs):
    """Create a styled text area"""
    return st.text_area(label, key=key, **kwargs)

def create_expander(label: str, expanded: bool = False, **kwargs):
    """Create a styled expander"""
    return st.expander(label, expanded=expanded, **kwargs)

def create_columns(spec: list, **kwargs):
    """Create responsive columns"""
    return st.columns(spec, **kwargs)

def create_tabs(labels: list, **kwargs):
    """Create styled tabs"""
    return st.tabs(labels, **kwargs)
