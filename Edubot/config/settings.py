import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def initialize_app():
    """Initialize application settings and configurations"""
    
    # Set session state variables if not already set
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_user = None
        st.session_state.uploaded_files = []
        st.session_state.summaries = []
        st.session_state.quizzes = []
        st.session_state.performance_data = []
        st.session_state.recommendations = []

def get_openai_api_key():
    """Get OpenAI API key from Streamlit secrets or environment variables.

    Priority:
    1) st.secrets["openai"]["api_key"]
    2) st.secrets["OPENAI_API_KEY"]
    3) env var OPENAI_API_KEY
    """
    try:
        # Prefer nested secrets: { "openai": { "api_key": "..." } }
        if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
            return st.secrets["openai"]["api_key"]
        # Support flat secret key
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        # st.secrets not available outside Streamlit runtime
        pass

    return os.getenv('OPENAI_API_KEY')

def is_openai_mock_enabled() -> bool:
    """Return True if mock mode is enabled for OpenAI calls."""
    return os.getenv('OPENAI_MOCK', '0') in ('1', 'true', 'True')

def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL', 'postgresql://localhost:5432/edubot')

def get_model_cache_dir():
    """Get model cache directory"""
    return os.getenv('MODEL_CACHE_DIR', './models_cache')

# Model configurations
T5_MODEL_CONFIG = {
    'model_name': 't5-base',
    'max_length': 512,
    'min_length': 50,
    'do_sample': False,
    'num_beams': 4
}

GPT_CONFIG = {
    'model': 'gpt-3.5-turbo',
    'max_tokens': 500,
    'temperature': 0.7
}

TFIDF_CONFIG = {
    'max_features': 1000,
    'ngram_range': (1, 2),
    'min_df': 2
}

PERFORMANCE_MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'threshold': 0.6
}

