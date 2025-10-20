#!/usr/bin/env python3
"""
Admin pages for EduBot
Admin authentication and dashboard functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import get_auth_manager
from database.user_models import get_user_database
from frontend.components import create_header, create_error_message, create_success_message

def admin_login_page():
    """Admin login page"""
    create_header("🔒 Admin Login", "Access the EduBot admin dashboard")
    
    auth_manager = get_auth_manager()
    user_db = get_user_database()
    
    # Check if already logged in as admin
    if st.session_state.get('admin_authenticated'):
        st.rerun()
    
    # Login form
    with st.form("admin_login_form", clear_on_submit=True):
        username = st.text_input(
            "Admin Username", 
            placeholder="Enter admin username"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Enter admin password"
        )
        
        login_submitted = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
        
        if login_submitted:
            if not username or not password:
                create_error_message("Please enter both username and password")
                st.rerun()
            
            # Verify admin credentials
            user = user_db.get_user_by_username(username.strip())
            
            if not user or not user.get('is_admin', False):
                create_error_message("❌ Invalid admin credentials")
                st.rerun()
            
            if not auth_manager.verify_password(password, user['password_hash']):
                create_error_message("❌ Invalid admin credentials")
                st.rerun()
            
            # Create admin session
            st.session_state['admin_authenticated'] = True
            st.session_state['admin_user'] = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
            
            # Redirect to admin dashboard
            st.query_params["admin"] = "dashboard"
            st.rerun()
    
    # Back to main app link
    st.markdown("---")
    if st.button("← Back to EduBot", use_container_width=True):
        st.query_params.clear()
        st.rerun()

def admin_logout():
    """Logout admin user"""
    if 'admin_authenticated' in st.session_state:
        del st.session_state['admin_authenticated']
    if 'admin_user' in st.session_state:
        del st.session_state['admin_user']
    st.rerun()

def manage_users():
    """User management section"""
    user_db = get_user_database()
    
    st.markdown("## 👥 User Management")
    
    # Get all users
    users = user_db.get_all_users()
    
    if not users:
        st.info("No users found.")
        return
    
    # Convert to DataFrame for display
    df = pd.DataFrame(users)
    
    # Format dates
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
    if 'last_login' in df.columns:
        df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
    
    # Display user statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", len(users))
    with col2:
        admin_count = len([u for u in users if u.get('is_admin')])
        st.metric("👑 Admins", admin_count)
    with col3:
        active_count = len([u for u in users if u.get('is_active')])
        st.metric("✅ Active", active_count)
    with col4:
        recent_count = len([u for u in users if u.get('last_login')])
        st.metric("🟢 Recent Logins", recent_count)
    
    st.markdown("---")
    
    # Display user table with better formatting
    display_columns = ['id', 'username', 'email', 'full_name', 'education_level', 'is_admin', 'created_at', 'last_login']
    available_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(
        df[available_columns]
        .rename(columns={
            'id': 'ID',
            'username': 'Username',
            'email': 'Email',
            'full_name': 'Full Name',
            'education_level': 'Education',
            'is_admin': 'Is Admin',
            'created_at': 'Created At',
            'last_login': 'Last Login'
        }),
        use_container_width=True,
        height=400
    )
    
    # User actions
    st.markdown("### User Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🔧 Edit User"):
            user_id = st.number_input("User ID", min_value=1, step=1, key="edit_user_id")
            is_admin = st.checkbox("Is Admin", key="edit_is_admin")
            
            if st.button("Update User", key="update_user_btn"):
                try:
                    if is_admin:
                        success = user_db.make_user_admin(user_id)
                    else:
                        success = user_db.remove_admin_privileges(user_id)
                    
                    if success:
                        st.success(f"User {user_id} updated successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to update user {user_id}")
                except Exception as e:
                    st.error(f"Error updating user: {e}")
    
    with col2:
        with st.expander("❌ Delete User", expanded=False):
            user_id = st.number_input("User ID", min_value=1, step=1, key="delete_user_id")
            confirm = st.checkbox("I understand this action cannot be undone", key="confirm_delete")
            
            if st.button("Delete User", disabled=not confirm, type="primary", key="delete_user_btn"):
                if user_id == st.session_state['admin_user']['id']:
                    st.error("Cannot delete your own account while logged in")
                else:
                    try:
                        # Use execute_query method for delete operation
                        result = user_db.execute_query("DELETE FROM users WHERE id = ?", (user_id,))
                        st.success(f"User {user_id} deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting user: {e}")

def admin_dashboard():
    """Enhanced admin dashboard with comprehensive analytics"""
    # Check if admin is authenticated
    if not st.session_state.get('admin_authenticated'):
        st.query_params["admin"] = "login"
        st.rerun()
    
    create_header("📊 Admin Analytics Dashboard", "Comprehensive analytics and user management")
    
    # Navigation in sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['admin_user']['username']}")
        st.markdown("*Administrator*")
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigation",
            ["📊 Analytics Dashboard", "👥 User Management", "📈 Reports", "🔍 User Activities"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True, key="refresh_btn"):
            st.rerun()
            
        st.markdown("---")
        
        if st.button("🔒 Logout", type="secondary", use_container_width=True, key="logout_btn"):
            admin_logout()
            return  # Exit early after logout
    
    # Main content area
    if page == "📊 Analytics Dashboard":
        # Import analytics components
        try:
            from frontend.admin_components import (
                create_analytics_cards, create_engagement_metrics, create_performance_overview,
                create_date_range_filter, create_download_section, create_activity_timeline,
                create_error_summary
            )
            from utils.analytics import get_analytics_manager
            
            # Get analytics data
            analytics_manager = get_analytics_manager()
            
            # Date range filter
            start_date, end_date, date_range = create_date_range_filter()
            
            # Get comprehensive analytics
            analytics = analytics_manager.get_dashboard_analytics(date_range)
            
            # Display main analytics cards
            create_analytics_cards(analytics)
            
            st.markdown("---")
            
            # Engagement metrics
            create_engagement_metrics(analytics)
            
            st.markdown("---")
            
            # Performance overview
            create_performance_overview(analytics)
            
            st.markdown("---")
            
            # Charts and visualizations
            st.markdown("### 📈 Visualizations")
            
            try:
                charts = analytics_manager.create_visualization_charts(analytics)
                
                # Display charts in tabs
                if charts:
                    chart_tabs = st.tabs(list(charts.keys()))
                    for i, (chart_name, chart) in enumerate(charts.items()):
                        with chart_tabs[i]:
                            # Use unique key based on chart name to avoid ID conflicts
                            chart_key = f"plotly_chart_{chart_name.lower().replace(' ', '_')}"
                            st.plotly_chart(chart, use_container_width=True, key=chart_key)
                else:
                    st.info("📈 No chart data available for the selected period.")
                    
            except Exception as e:
                st.warning(f"Charts unavailable: {str(e)}")
            
            st.markdown("---")
            
            # Activity timeline
            create_activity_timeline(analytics)
            
            st.markdown("---")
            
            # System health
            create_error_summary()
            
        except ImportError as e:
            st.error(f"Analytics components not available: {str(e)}")
            # Fallback to basic dashboard
            basic_admin_dashboard()
            
    elif page == "📈 Reports":
        # Reports section
        st.markdown("## 📈 Analytics Reports")
        
        try:
            from frontend.admin_components import create_download_section
            from utils.analytics import get_analytics_manager
            
            analytics_manager = get_analytics_manager()
            analytics = analytics_manager.get_dashboard_analytics("30")
            
            create_download_section(analytics)
            
        except ImportError:
            st.error("Report generation components not available")
    
    elif page == "🔍 User Activities":
        # User activities section
        st.markdown("## 🔍 User Activity Details")
        
        try:
            from frontend.admin_components import create_user_activity_table
            from utils.analytics import get_analytics_manager
            
            analytics_manager = get_analytics_manager()
            
            # Get user activity data
            user_activities = analytics_manager.get_user_activity_details(days=30)
            
            # Display user activity table
            create_user_activity_table(user_activities)
            
        except ImportError:
            st.error("User activity components not available")
    
    elif page == "👥 User Management":
        manage_users()

def basic_admin_dashboard():
    """Basic admin dashboard fallback when analytics components aren't available"""
    # Get user activity data
    user_db = get_user_database()
    users_activity = user_db.get_all_users_activity()
    total_users = user_db.get_total_users()
    
    # Display basic metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Total Users", total_users)
    with col2:
        active_users = len([u for u in users_activity if u.get('last_activity')])
        st.metric("🟢 Active Users", active_users)
    with col3:
        avg_quizzes = sum(u.get('quiz_count', 0) for u in users_activity) / max(total_users, 1)
        st.metric("📝 Avg Quizzes/User", f"{avg_quizzes:.1f}")
    
    # Basic user activity display
    st.markdown("### 👥 User Activity")
    
    if users_activity:
        import pandas as pd
        df = pd.DataFrame(users_activity)
        
        # Format datetime columns
        if 'last_login' in df.columns:
            df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
        
        # Display data table
        st.dataframe(
            df[['username', 'email', 'last_login']]
            .rename(columns={
                'username': 'Username',
                'email': 'Email',
                'last_login': 'Last Login'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No user activity data available.")

def admin_navigation():
    """Handle admin page routing"""
    try:
        # Check if we're on an admin page
        if "admin" not in st.query_params:
            st.query_params["admin"] = "login"
            st.rerun()
            
        page = st.query_params.get("admin", "login").lower()
        
        # Handle login page
        if page == "login":
            if st.session_state.get('admin_authenticated'):
                st.query_params["admin"] = "dashboard"
                st.rerun()
            else:
                admin_login_page()
                return
                
        # Handle dashboard page
        elif page == "dashboard":
            if st.session_state.get('admin_authenticated'):
                admin_dashboard()
                return
            else:
                st.query_params["admin"] = "login"
                st.rerun()
                
        # Handle unknown pages
        else:
            st.error("Invalid admin page requested.")
            st.query_params["admin"] = "login"
            st.rerun()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()
