import streamlit as st
import os
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from config.settings import initialize_app
from utils.auth import get_auth_manager
from frontend.auth_pages import auth_navigation, logout_confirmation
from frontend.admin_pages import admin_navigation, admin_logout
from database.user_models import get_user_database

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    # Initialize application settings
    initialize_app()
    
    # Set page configuration
    st.set_page_config(
        page_title="EduBot - AI Learning Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize authentication manager
    auth_manager = get_auth_manager()
    
    # Handle admin routes and authentication
    if "admin" in st.query_params:
        try:
            # Let admin_navigation handle all admin routing
            admin_navigation()
            return
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    
    # Check if admin is authenticated but not on admin page
    if st.session_state.get('admin_authenticated'):
        print("Admin authenticated, redirecting to dashboard")
        st.query_params["admin"] = "dashboard"
        st.rerun()
    
    # Check if user just logged in and needs redirect
    if st.session_state.get('just_logged_in'):
        st.session_state.pop('just_logged_in', None)
        st.rerun()
        
    # Check if we have an admin user in session but not marked as authenticated
    admin_user = st.session_state.get('admin_user')
    if admin_user and not st.session_state.get('admin_authenticated'):
        print("Found admin user in session, setting authenticated flag")
        st.session_state['admin_authenticated'] = True
        st.query_params["admin"] = "dashboard"
        st.rerun()
    
    # Check if user is authenticated
    if not auth_manager.is_authenticated():
        # If we're not on an auth page and don't have a reset token, redirect to login
        if "auth_page" not in st.query_params and "reset_token" not in st.query_params:
            st.query_params["auth_page"] = "login"
            st.rerun()
        
        # Show authentication pages
        auth_navigation()
        return
    
    # If we're on an auth page but already authenticated, clear it
    if "auth_page" in st.query_params:
        del st.query_params["auth_page"]
        st.rerun()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎓 EduBot")
    st.sidebar.markdown("---")
    
    # Show user info and logout option
    logout_confirmation()
    
    # Navigation menu
    page_options = [
        "🏠 Home",
        "📝 Text Summarization", 
        "❓ Quiz Generation",
        "📊 Performance Analysis",
        "📚 Recommendations"
    ]
    
    # Add admin link if user is admin
    if st.session_state.get('current_user', {}).get('is_admin', False):
        page_options.append("👑 Admin Dashboard")
    
    # Check if quick action page was selected
    quick_action_page = st.session_state.get("quick_action_page", None)
    default_index = 0
    
    if quick_action_page and quick_action_page in page_options:
        default_index = page_options.index(quick_action_page)
        # Clear the quick action page after using it
        del st.session_state["quick_action_page"]
    
    page = st.sidebar.selectbox(
        "Choose a feature:",
        page_options,
        index=default_index,
        key="nav_page_select"
    )
    
    # Page routing
    if page == "🏠 Home":
        from frontend.pages import home_page
        home_page()
    elif page == "📝 Text Summarization":
        from frontend.pages import summarization_page
        summarization_page()
    elif page == "❓ Quiz Generation":
        from frontend.pages import quiz_page
        quiz_page()
    elif page == "📊 Performance Analysis":
        from frontend.pages import performance_page
        performance_page()
    elif page == "📚 Recommendations":
        from frontend.pages import recommendations_page
        recommendations_page()
    elif page == "👑 Admin Dashboard":
        st.query_params["admin"] = "dashboard"
        st.rerun()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**EduBot v1.0**")
    st.sidebar.markdown("AI-Powered Learning Assistant")

if __name__ == "__main__":
    main()
