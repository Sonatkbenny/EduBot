#!/usr/bin/env python3
"""
Authentication pages for EduBot
Registration, Login, and Password Reset functionality
"""

from datetime import datetime
import streamlit as st
from typing import Dict, Any, Optional
from utils.auth import get_auth_manager
from database.user_models import get_user_database
from frontend.components import create_header, create_success_message, create_error_message, create_warning_message

def registration_page():
    """User registration page"""
    create_header("🔐 Register for EduBot", "Create your account to access AI-powered learning features")
    
    auth_manager = get_auth_manager()
    user_db = get_user_database()
    
    # Registration form
    st.markdown("### 📝 Create Your Account")
    
    with st.form("registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *", 
                placeholder="Enter your full name",
                help="Your full name as you'd like it displayed"
            )
            username = st.text_input(
                "Username *", 
                placeholder="Choose a unique username",
                help="3-50 characters, letters, numbers, underscore, and hyphen only"
            )
            email = st.text_input(
                "Email Address *", 
                placeholder="Enter your email address",
                help="We'll use this for account recovery"
            )
        
        with col2:
            password = st.text_input(
                "Password *", 
                type="password",
                placeholder="Create a strong password",
                help="At least 8 characters with uppercase, lowercase, number, and special character"
            )
            confirm_password = st.text_input(
                "Confirm Password *", 
                type="password",
                placeholder="Re-enter your password"
            )
            education_level = st.selectbox(
                "Education Level *",
                ["", "High School", "Secondary", "College", "Graduate", "Other"],
                help="Select your current education level"
            )
        
        # Password strength indicator
        if password:
            is_strong, errors = auth_manager.validate_password_strength(password)
            if is_strong:
                st.success("✅ Strong password!")
            else:
                st.error("❌ Password requirements not met:")
                for error in errors:
                    st.write(f"  • {error}")
        
        submitted = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Validate all fields
            errors = []
            
            # Required field validation
            if not full_name or not full_name.strip():
                errors.append("Full name is required")
            if not username or not username.strip():
                errors.append("Username is required")
            if not email or not email.strip():
                errors.append("Email is required")
            if not password:
                errors.append("Password is required")
            if not confirm_password:
                errors.append("Please confirm your password")
            if not education_level:
                errors.append("Please select your education level")
            
            # Password confirmation
            if password and confirm_password and password != confirm_password:
                errors.append("Passwords do not match")
            
            # Field format validation
            if full_name:
                is_valid, msg = auth_manager.validate_full_name(full_name.strip())
                if not is_valid:
                    errors.append(f"Full name: {msg}")
            
            if username:
                is_valid, msg = auth_manager.validate_username(username.strip())
                if not is_valid:
                    errors.append(f"Username: {msg}")
            
            if email:
                is_valid, msg = auth_manager.validate_email(email.strip())
                if not is_valid:
                    errors.append(f"Email: {msg}")
            
            if password:
                is_valid, pwd_errors = auth_manager.validate_password_strength(password)
                if not is_valid:
                    errors.extend(pwd_errors)
            
            # Show validation errors
            if errors:
                create_error_message("Please fix the following issues:")
                for error in errors:
                    st.write(f"  • {error}")
                return
            
            # Try to create user
            password_hash = auth_manager.hash_password(password)
            success, message, user_id = user_db.create_user(
                username.strip(),
                email.strip().lower(),
                full_name.strip(),
                password_hash,
                education_level
            )
            
            if success:
                create_success_message(f"🎉 Account created successfully! Welcome to EduBot, {full_name}!")
                st.info("📝 You can now log in with your new account.")
                
                # Set flag to show login redirect outside form
                st.session_state["registration_success"] = True
            else:
                create_error_message(f"Registration failed: {message}")
    
    # Check if registration was successful and show login redirect
    if st.session_state.get("registration_success"):
        st.markdown("---")
        if st.button("🔑 Continue to Login", type="primary", use_container_width=True):
            st.session_state["registration_success"] = False
            st.query_params["auth_page"] = "login"
            st.rerun()
    
    # Login link
    st.markdown("---")
    st.markdown("### 🔑 Already have an account?")
    if st.button("Sign In Here", use_container_width=True, type="secondary"):
        st.query_params["auth_page"] = "login"
        st.rerun()

def login_page():
    """User login page"""
    create_header("🔑 Login to EduBot", "Access your personalized AI learning assistant")
    
    auth_manager = get_auth_manager()
    user_db = get_user_database()
    
    # Login form
    st.markdown("### 🔓 Sign In")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username or Email", 
            placeholder="Enter your username or email"
        )
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Enter your password"
        )
        
        login_submitted = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
        
        if login_submitted:
            # Validate inputs
            if not username or not password:
                create_error_message("Please enter both username/email and password")
                st.rerun()
            
            # Try to find user by username or email
            user = None
            if "@" in username:
                user = user_db.get_user_by_email(username.strip().lower())
            else:
                user = user_db.get_user_by_username(username.strip())
            
            if not user:
                create_error_message("❌ Invalid username/email or password")
                st.rerun()
            
            # Debug: Print user data and password info
            print(f"User found: {user}")
            print(f"Stored hash: {user['password_hash']}")
            print(f"Input password: {password}")
            
            # Verify password
            password_correct = auth_manager.verify_password(password, user['password_hash'])
            print(f"Password verification result: {password_correct}")
            
            # Log login attempt
            st.session_state['login_attempt'] = {
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'success': password_correct,
                'is_admin': bool(user.get('is_admin', False)),
                'user_id': user.get('id')
            }
            
            if not password_correct:
                print("Password verification failed")
                create_error_message("❌ Invalid username/email or password")
                st.rerun()
            else:
                print("Password verified successfully")
            
            # Set user data with all required fields
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user.get('full_name', 'Administrator'),
                'education_level': user.get('education_level', 'Graduate'),
                'is_admin': bool(user.get('is_admin', False))
            }
            
            # Update last login first
            user_db.update_last_login(user['id'])
            
            # Track login activity
            try:
                from utils.activity_tracker import get_activity_tracker
                activity_tracker = get_activity_tracker()
                activity_tracker.log_login_activity(user['id'], "standard")
            except Exception as e:
                print(f"Error tracking login activity: {e}")
            
            # Check if user is admin
            is_admin = user_data['is_admin']
            print(f"User is admin: {is_admin}")
            print(f"User data: {user_data}")
            
            # Set session state
            if is_admin:
                print("Setting admin session...")
                # Create proper user session using auth_manager
                auth_manager.create_user_session(user_data)
                
                # Set admin-specific session data
                st.session_state['admin_authenticated'] = True
                st.session_state['admin_user'] = user_data
                
                # Force redirect to admin dashboard
                print("Redirecting to admin dashboard...")
                st.query_params.clear()
                st.query_params["admin"] = "dashboard"
                st.rerun()
            else:
                print("Setting regular user session...")
                # Create proper user session using auth_manager
                auth_manager.create_user_session(user_data)
                
                # Clear auth page query param to go to main app
                if "auth_page" in st.query_params:
                    del st.query_params["auth_page"]
                
                # Set flag for redirect
                st.session_state['just_logged_in'] = True
                print("Redirecting to main app...")
                st.rerun()
    
    # Add navigation links outside the form
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Forgot Password?", use_container_width=True, type="secondary"):
            st.query_params["auth_page"] = "reset"
            st.rerun()
    with col2:
        if st.button("📝 Create Account", use_container_width=True, type="secondary"):
            st.query_params["auth_page"] = "register"
            st.rerun()
    
    # Registration link - Enhanced visibility
    st.markdown("---")
    st.markdown("### 📝 New to EduBot?")
    st.markdown("*Join thousands of students already using AI to enhance their learning!*")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📝 Create Account", type="primary", use_container_width=True):
            st.query_params["auth_page"] = "register"
            st.rerun()
    with col2:
        if st.button("📋 Sign Up Here", use_container_width=True):
            st.query_params["auth_page"] = "register"
            st.rerun()
    
    # Additional call-to-action
    st.info("✨ **Create your free account** to access personalized AI tutoring, quiz generation, and progress tracking!")

def password_reset_page():
    """Password reset page"""
    create_header("🔄 Reset Password", "Recover access to your EduBot account")
    
    auth_manager = get_auth_manager()
    user_db = get_user_database()
    
    # Check if we're in reset confirmation mode
    reset_token = st.query_params.get("reset_token", None)
    
    if reset_token:
        # Password reset confirmation
        st.markdown("### 🔒 Set New Password")
        
        # Verify token first
        email = auth_manager.verify_password_reset_token(reset_token)
        if not email:
            create_error_message("❌ Invalid or expired reset token. Please request a new password reset.")
            if st.button("🔄 Request New Reset", use_container_width=True):
                del st.query_params["reset_token"]
                st.rerun()
            return
        
        with st.form("password_reset_form"):
            st.info(f"🔑 Setting new password for: {email}")
            
            new_password = st.text_input(
                "New Password *", 
                type="password",
                placeholder="Enter your new password"
            )
            confirm_new_password = st.text_input(
                "Confirm New Password *", 
                type="password",
                placeholder="Re-enter your new password"
            )
            
            # Password strength indicator
            if new_password:
                is_strong, errors = auth_manager.validate_password_strength(new_password)
                if is_strong:
                    st.success("✅ Strong password!")
                else:
                    st.error("❌ Password requirements not met:")
                    for error in errors:
                        st.write(f"  • {error}")
            
            reset_submitted = st.form_submit_button("🔐 Reset Password", type="primary", use_container_width=True)
            
            if reset_submitted:
                # Validate inputs
                if not new_password or not confirm_new_password:
                    create_error_message("Please fill in both password fields")
                    return
                
                if new_password != confirm_new_password:
                    create_error_message("Passwords do not match")
                    return
                
                # Validate password strength
                is_strong, pwd_errors = auth_manager.validate_password_strength(new_password)
                if not is_strong:
                    create_error_message("Password does not meet requirements:")
                    for error in pwd_errors:
                        st.write(f"  • {error}")
                    return
                
                # Update password
                password_hash = auth_manager.hash_password(new_password)
                if user_db.update_password(email, password_hash):
                    create_success_message("🎉 Password reset successfully!")
                    st.info("🔑 You can now log in with your new password.")
                    
                    # Remove reset token and redirect to login
                    del st.query_params["reset_token"]
                    st.query_params["auth_page"] = "login"
                    st.rerun()
                else:
                    create_error_message("❌ Failed to reset password. Please try again.")
    
    else:
        # Password reset request
        st.markdown("### 📧 Request Password Reset")
        
        with st.form("password_reset_request_form"):
            st.markdown("Enter your email address or username to reset your password:")
            
            identifier = st.text_input(
                "Email or Username", 
                placeholder="Enter your email address or username"
            )
            
            reset_requested = st.form_submit_button("🔄 Send Reset Link", type="primary", use_container_width=True)
            
            if reset_requested:
                if not identifier or not identifier.strip():
                    create_error_message("Please enter your email or username")
                    return
                
                # Find user by email or username
                user = None
                if "@" in identifier:
                    user = user_db.get_user_by_email(identifier.strip().lower())
                else:
                    user = user_db.get_user_by_username(identifier.strip())
                
                if not user:
                    # Don't reveal if user exists or not for security
                    create_success_message("🔄 If an account with that email/username exists, password reset instructions have been sent.")
                    return
                
                # Generate reset token
                reset_token = auth_manager.generate_password_reset_token(user['email'])
                
                # Store token in database for verification
                from datetime import datetime, timedelta
                expires_at = datetime.now() + timedelta(hours=1)
                user_db.store_password_reset_token(user['email'], reset_token, expires_at)
                
                # Set state to show reset link after form submission
                st.session_state['show_reset_link'] = True
                st.session_state['reset_token'] = reset_token
                st.rerun()
    
    # Show reset link after form submission (outside the form)
    if st.session_state.get('show_reset_link'):
        st.markdown("---")
        create_success_message("🔄 Password reset link generated!")
        st.info("📧 In a real application, this would be sent to your email. For demo purposes, click the link below:")
        
        reset_token = st.session_state.get('reset_token')
        if st.button("🔗 Click here to reset password", use_container_width=True, type="primary"):
            st.query_params["reset_token"] = reset_token
            del st.session_state['show_reset_link']
            del st.session_state['reset_token']
            st.rerun()
    
    # Navigation links
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Back to Login", use_container_width=True):
            st.query_params["auth_page"] = "login"
            st.rerun()
    with col2:
        if st.button("📝 Create Account", use_container_width=True):
            st.query_params["auth_page"] = "register"
            st.rerun()

def auth_navigation():
    """Handle authentication page routing"""
    auth_page = st.query_params.get("auth_page", "login")
    
    # Show only the requested page
    if auth_page == "login":
        login_page()
    elif auth_page == "register":
        registration_page()
    elif auth_page == "reset":
        password_reset_page()
    else:
        # Default to login if invalid page specified
        st.query_params["auth_page"] = "login"
        st.rerun()

def logout_confirmation():
    """Show logout confirmation"""
    auth_manager = get_auth_manager()
    current_user = auth_manager.get_current_user()
    
    if current_user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{current_user['full_name']}**")
        st.sidebar.markdown(f"📧 {current_user['email']}")
        st.sidebar.markdown(f"🎓 {current_user['education_level']}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            # Track logout activity before logging out
            try:
                from utils.activity_tracker import get_activity_tracker
                activity_tracker = get_activity_tracker()
                activity_tracker.log_logout_activity(current_user['id'])
            except Exception as e:
                print(f"Error tracking logout activity: {e}")
            
            auth_manager.logout_user()
            create_success_message("👋 You have been logged out successfully!")
            st.rerun()
