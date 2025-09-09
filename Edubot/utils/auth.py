#!/usr/bin/env python3
"""
Authentication utilities for EduBot
Handles password hashing, validation, and session management
"""

import bcrypt
import re
import jwt
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from email_validator import validate_email, EmailNotValidError
import secrets
import hashlib

class AuthManager:
    """Authentication manager for user registration, login, and session handling"""
    
    def __init__(self):
        self.secret_key = self._get_secret_key()
        self.session_timeout = 24 * 60 * 60  # 24 hours in seconds
    
    def _get_secret_key(self) -> str:
        """Get or generate secret key for JWT tokens"""
        # Try to get from environment or session state
        secret = st.session_state.get('app_secret_key')
        if not secret:
            # Generate a new secret for this session
            secret = secrets.token_urlsafe(32)
            st.session_state['app_secret_key'] = secret
        return secret
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            print(f"Verifying password for hash: {hashed_password[:10]}...")
            result = bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
            print(f"Password verification result: {result}")
            return result
        except Exception as e:
            print(f"Error in verify_password: {str(e)}")
            print(f"Password: {password}")
            print(f"Hash: {hashed_password}")
            return False
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format"""
        try:
            # Validate and get info
            valid = validate_email(email)
            return True, valid.email
        except EmailNotValidError as e:
            return False, str(e)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, list]:
        """Validate password strength and return errors if any"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """Validate username format"""
        if not username or len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        # Allow alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        return True, ""
    
    def validate_full_name(self, full_name: str) -> Tuple[bool, str]:
        """Validate full name"""
        if not full_name or len(full_name.strip()) < 2:
            return False, "Full name must be at least 2 characters long"
        
        if len(full_name) > 100:
            return False, "Full name must be less than 100 characters"
        
        # Allow letters, spaces, apostrophes, and hyphens
        if not re.match(r'^[a-zA-Z\s\'-]+$', full_name):
            return False, "Full name can only contain letters, spaces, apostrophes, and hyphens"
        
        return True, ""
    
    def create_session_token(self, user_data: Dict[str, Any]) -> str:
        """Create a JWT session token for the user"""
        payload = {
            'user_id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data['full_name'],
            'education_level': user_data['education_level'],
            'is_admin': user_data.get('is_admin', False),
            'exp': datetime.utcnow() + timedelta(seconds=self.session_timeout),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def create_user_session(self, user_data: Dict[str, Any]):
        """Create a user session in Streamlit"""
        # Create session token
        token = self.create_session_token(user_data)
        
        # Store in session state
        st.session_state['authenticated'] = True
        st.session_state['session_token'] = token
        st.session_state['current_user'] = {
            'id': user_data['id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data['full_name'],
            'education_level': user_data['education_level'],
            'is_admin': user_data.get('is_admin', False)
        }
        st.session_state['user'] = st.session_state['current_user']  # For compatibility
        st.session_state['login_time'] = datetime.now()
    
    def logout_user(self):
        """Logout user and clear session"""
        keys_to_remove = [
            'authenticated', 'session_token', 'current_user', 
            'login_time', 'summaries', 'quizzes', 'performance_data', 
            'recommendations'
        ]
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not st.session_state.get('authenticated'):
            return False
        
        # Verify session token
        token = st.session_state.get('session_token')
        if not token:
            return False
        
        user_data = self.verify_session_token(token)
        if not user_data:
            # Token expired or invalid
            self.logout_user()
            return False
        
        return True
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user data from session"""
        if self.is_authenticated():
            return st.session_state.get('current_user')
        return None
    
    def require_authentication(self):
        """Decorator function to require authentication for pages"""
        if not self.is_authenticated():
            st.error("🔒 Please log in to access this feature.")
            st.stop()
        
        return True
    
    def generate_password_reset_token(self, user_email: str) -> str:
        """Generate a password reset token"""
        payload = {
            'email': user_email,
            'purpose': 'password_reset',
            'exp': datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            if payload.get('purpose') == 'password_reset':
                return payload.get('email')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
        
        return None

# Global auth manager instance
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get global authentication manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
