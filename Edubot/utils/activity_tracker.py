#!/usr/bin/env python3
"""
Activity tracking helper for EduBot
Provides easy integration for logging user activities across the application
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any
from utils.analytics import get_analytics_manager
import time

class ActivityTracker:
    """Helper class for tracking user activities throughout the application"""
    
    def __init__(self):
        self.analytics_manager = get_analytics_manager()
        self.session_start_time = None
    
    def init_session_tracking(self):
        """Initialize session tracking for a user"""
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = time.time()
    
    def log_page_visit(self, page_name: str, description: str = ""):
        """Log when a user visits a page"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="page_visit",
                description=description or f"Visited {page_name}",
                page=page_name,
                metadata={'timestamp': datetime.now().isoformat()}
            )
    
    def log_feature_usage(self, feature_name: str, time_spent: int = 0, metadata: Dict = None):
        """Log when a user uses a specific feature"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            # Log in analytics
            self.analytics_manager.log_feature_usage(
                user_id=user['id'],
                feature_name=feature_name,
                time_spent=time_spent
            )
            
            # Also log as activity
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="feature_usage",
                description=f"Used {feature_name}",
                page=feature_name,
                session_duration=time_spent,
                metadata=metadata or {}
            )
    
    def log_quiz_activity(self, quiz_data: Dict[str, Any]):
        """Log quiz completion activity"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            # Log in quiz analytics
            self.analytics_manager.log_quiz_analytics(user['id'], quiz_data)
            
            # Also log as general activity
            score = quiz_data.get('total_score', 0)
            topic = quiz_data.get('topic', 'Unknown')
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="quiz_completion",
                description=f"Completed quiz on {topic} with score {score}%",
                page="Quiz Generation",
                session_duration=quiz_data.get('completion_time', 0),
                metadata=quiz_data
            )
    
    def log_document_processing(self, document_data: Dict[str, Any]):
        """Log document processing activity"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            # Log in document analytics
            self.analytics_manager.log_document_analytics(user['id'], document_data)
            
            # Also log as general activity
            doc_name = document_data.get('document_name', 'Unknown')
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="document_processing",
                description=f"Processed document: {doc_name}",
                page="Text Summarization",
                session_duration=document_data.get('processing_time', 0),
                metadata=document_data
            )
    
    def log_performance_analysis(self, performance_data: Dict[str, Any]):
        """Log performance analysis activity"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            # Log in performance analytics
            self.analytics_manager.log_performance_analytics(user['id'], performance_data)
            
            # Also log as general activity
            subject = performance_data.get('subject', 'Unknown')
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="performance_analysis",
                description=f"Analyzed performance in {subject}",
                page="Performance Analysis",
                metadata=performance_data
            )
    
    def log_recommendation_view(self, recommendation_data: Dict[str, Any]):
        """Log when user views recommendations"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            topic = recommendation_data.get('topic', 'General')
            count = recommendation_data.get('count', 0)
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="recommendation_view",
                description=f"Viewed {count} recommendations for {topic}",
                page="Recommendations",
                metadata=recommendation_data
            )
    
    def log_login_activity(self, user_id: int, login_method: str = "standard"):
        """Log user login activity"""
        self.analytics_manager.log_user_activity(
            user_id=user_id,
            activity_type="user_login",
            description=f"User logged in via {login_method}",
            page="Authentication",
            metadata={'login_method': login_method, 'login_time': datetime.now().isoformat()}
        )
    
    def log_logout_activity(self, user_id: int):
        """Log user logout activity"""
        session_duration = 0
        if 'session_start_time' in st.session_state:
            session_duration = int(time.time() - st.session_state.session_start_time)
        
        self.analytics_manager.log_user_activity(
            user_id=user_id,
            activity_type="user_logout",
            description="User logged out",
            page="Authentication",
            session_duration=session_duration,
            metadata={'logout_time': datetime.now().isoformat()}
        )
    
    def log_error_encounter(self, error_type: str, error_message: str, page: str):
        """Log when user encounters an error"""
        user = st.session_state.get('current_user')
        if user and user.get('id'):
            self.analytics_manager.log_user_activity(
                user_id=user['id'],
                activity_type="error_encounter",
                description=f"Encountered {error_type}: {error_message}",
                page=page,
                metadata={'error_type': error_type, 'error_message': error_message}
            )
    
    def get_session_duration(self) -> int:
        """Get current session duration in seconds"""
        if 'session_start_time' in st.session_state:
            return int(time.time() - st.session_state.session_start_time)
        return 0

# Global activity tracker instance
_activity_tracker = None

def get_activity_tracker() -> ActivityTracker:
    """Get global activity tracker instance"""
    global _activity_tracker
    if _activity_tracker is None:
        _activity_tracker = ActivityTracker()
    return _activity_tracker

def track_page_visit(page_name: str, description: str = ""):
    """Convenience function to track page visits"""
    tracker = get_activity_tracker()
    tracker.init_session_tracking()
    tracker.log_page_visit(page_name, description)

def track_feature_usage(feature_name: str, time_spent: int = 0, metadata: Dict = None):
    """Convenience function to track feature usage"""
    tracker = get_activity_tracker()
    tracker.log_feature_usage(feature_name, time_spent, metadata)
