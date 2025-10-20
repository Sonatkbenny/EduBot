#!/usr/bin/env python3
"""
Analytics utilities for EduBot
Handles user activity tracking and analytics data collection
"""

import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AnalyticsManager:
    """Manages analytics data collection and reporting"""
    
    def __init__(self, db_path: str = "edubot_users.db"):
        self.db_path = db_path
        self.init_analytics_tables()
    
    def init_analytics_tables(self):
        """Initialize analytics tracking tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # User activity log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        activity_type TEXT NOT NULL,
                        activity_description TEXT,
                        page_visited TEXT,
                        session_duration INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Feature usage tracking
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feature_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        feature_name TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 1,
                        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_time_spent INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Quiz analytics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        quiz_id TEXT,
                        topic TEXT,
                        questions_count INTEGER,
                        correct_answers INTEGER,
                        total_score REAL,
                        completion_time INTEGER,
                        difficulty_level TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Document processing analytics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS document_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        document_name TEXT,
                        document_size INTEGER,
                        processing_time INTEGER,
                        summary_length INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Performance analytics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        subject TEXT,
                        topic TEXT,
                        score REAL,
                        total_possible REAL,
                        time_taken INTEGER,
                        improvement_rate REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            print(f"Analytics table initialization error: {e}")
    
    def log_user_activity(self, user_id: int, activity_type: str, 
                         description: str = "", page: str = "", 
                         session_duration: int = 0, metadata: Dict = None):
        """Log user activity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_activity_log 
                    (user_id, activity_type, activity_description, page_visited, 
                     session_duration, created_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, activity_type, description, page, 
                     session_duration, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                     json.dumps(metadata) if metadata else None))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def log_feature_usage(self, user_id: int, feature_name: str, 
                         time_spent: int = 0):
        """Log feature usage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if usage record exists
                cursor.execute('''
                    SELECT id, usage_count, total_time_spent 
                    FROM feature_usage 
                    WHERE user_id = ? AND feature_name = ?
                ''', (user_id, feature_name))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute('''
                        UPDATE feature_usage 
                        SET usage_count = usage_count + 1,
                            last_used = CURRENT_TIMESTAMP,
                            total_time_spent = total_time_spent + ?
                        WHERE id = ?
                    ''', (time_spent, existing[0]))
                else:
                    # Create new record
                    cursor.execute('''
                        INSERT INTO feature_usage 
                        (user_id, feature_name, usage_count, total_time_spent)
                        VALUES (?, ?, 1, ?)
                    ''', (user_id, feature_name, time_spent))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging feature usage: {e}")
            return False
    
    def log_quiz_analytics(self, user_id: int, quiz_data: Dict[str, Any]):
        """Log quiz analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO quiz_analytics 
                    (user_id, quiz_id, topic, questions_count, correct_answers, 
                     total_score, completion_time, difficulty_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    quiz_data.get('quiz_id', ''),
                    quiz_data.get('topic', ''),
                    quiz_data.get('questions_count', 0),
                    quiz_data.get('correct_answers', 0),
                    quiz_data.get('total_score', 0),
                    quiz_data.get('completion_time', 0),
                    quiz_data.get('difficulty_level', 'medium')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging quiz analytics: {e}")
            return False
    
    def log_document_analytics(self, user_id: int, document_data: Dict[str, Any]):
        """Log document processing analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO document_analytics 
                    (user_id, document_name, document_size, processing_time, summary_length)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    document_data.get('document_name', ''),
                    document_data.get('document_size', 0),
                    document_data.get('processing_time', 0),
                    document_data.get('summary_length', 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging document analytics: {e}")
            return False
    
    def log_performance_analytics(self, user_id: int, performance_data: Dict[str, Any]):
        """Log performance analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_analytics 
                    (user_id, subject, topic, score, total_possible, 
                     time_taken, improvement_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    performance_data.get('subject', ''),
                    performance_data.get('topic', ''),
                    performance_data.get('score', 0),
                    performance_data.get('total_possible', 0),
                    performance_data.get('time_taken', 0),
                    performance_data.get('improvement_rate', 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging performance analytics: {e}")
            return False
    
    def get_dashboard_analytics(self, days: str = "30") -> Dict[str, Any]:
        """Get comprehensive dashboard analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                analytics = {}
                
                # User Overview
                cursor.execute('SELECT COUNT(*) as total FROM users WHERE is_active = TRUE')
                analytics['total_users'] = cursor.fetchone()['total']
                
                # Active users (users who logged in within specified days)
                cursor.execute(f'''
                    SELECT COUNT(*) as active 
                    FROM users 
                    WHERE is_active = TRUE AND 
                    (last_login IS NULL OR date(last_login) >= date('now', '-{days} days'))
                ''')
                analytics['active_users'] = cursor.fetchone()['active']
                
                # Users by education level
                cursor.execute('''
                    SELECT education_level, COUNT(*) as count 
                    FROM users 
                    WHERE is_active = TRUE 
                    GROUP BY education_level
                ''')
                analytics['users_by_education'] = dict(cursor.fetchall())
                
                # Activity summary (only up to current date)
                cursor.execute(f'''
                    SELECT activity_type, COUNT(*) as count
                    FROM user_activity_log 
                    WHERE created_at >= date('now', '-{days} days')
                    AND date(created_at) <= date('now')
                    GROUP BY activity_type
                ''')
                analytics['activity_summary'] = dict(cursor.fetchall())
                
                # Feature usage (only up to current date)
                cursor.execute(f'''
                    SELECT feature_name, SUM(usage_count) as total_usage
                    FROM feature_usage 
                    WHERE last_used >= date('now', '-{days} days')
                    AND date(last_used) <= date('now')
                    GROUP BY feature_name
                    ORDER BY total_usage DESC
                ''')
                analytics['feature_usage'] = dict(cursor.fetchall())
                
                # Quiz analytics (only up to current date)
                cursor.execute(f'''
                    SELECT 
                        COUNT(*) as total_quizzes,
                        AVG(total_score) as avg_score,
                        SUM(questions_count) as total_questions
                    FROM quiz_analytics 
                    WHERE created_at >= date('now', '-{days} days')
                    AND date(created_at) <= date('now')
                ''')
                quiz_stats = cursor.fetchone()
                analytics['quiz_stats'] = {
                    'total_quizzes': quiz_stats['total_quizzes'] or 0,
                    'avg_score': round(quiz_stats['avg_score'] or 0, 2),
                    'total_questions': quiz_stats['total_questions'] or 0
                }
                
                # Document processing stats (only up to current date)
                cursor.execute(f'''
                    SELECT 
                        COUNT(*) as total_documents,
                        AVG(processing_time) as avg_processing_time,
                        SUM(document_size) as total_size_processed
                    FROM document_analytics 
                    WHERE created_at >= date('now', '-{days} days')
                    AND date(created_at) <= date('now')
                ''')
                doc_stats = cursor.fetchone()
                analytics['document_stats'] = {
                    'total_documents': doc_stats['total_documents'] or 0,
                    'avg_processing_time': round(doc_stats['avg_processing_time'] or 0, 2),
                    'total_size_processed': doc_stats['total_size_processed'] or 0
                }
                
                # User registrations over time (only up to current date)
                cursor.execute(f'''
                    SELECT date(created_at) as reg_date, COUNT(*) as count
                    FROM users 
                    WHERE created_at >= date('now', '-{days} days')
                    AND date(created_at) <= date('now')
                    GROUP BY date(created_at)
                    ORDER BY reg_date
                ''')
                analytics['registrations_over_time'] = [dict(row) for row in cursor.fetchall()]
                
                # Login activity (only up to current date)
                cursor.execute(f'''
                    SELECT date(last_login) as login_date, COUNT(*) as count
                    FROM users 
                    WHERE last_login >= date('now', '-{days} days')
                    AND date(last_login) <= date('now')
                    GROUP BY date(last_login)
                    ORDER BY login_date
                ''')
                analytics['login_activity'] = [dict(row) for row in cursor.fetchall()]
                
                # Top active users (only up to current date)
                cursor.execute(f'''
                    SELECT u.username, COUNT(ual.id) as activity_count
                    FROM users u
                    LEFT JOIN user_activity_log ual ON u.id = ual.user_id
                    WHERE ual.created_at >= date('now', '-{days} days')
                    AND date(ual.created_at) <= date('now')
                    GROUP BY u.id, u.username
                    ORDER BY activity_count DESC
                    LIMIT 10
                ''')
                analytics['top_active_users'] = [dict(row) for row in cursor.fetchall()]
                
                return analytics
                
        except Exception as e:
            print(f"Error getting dashboard analytics: {e}")
            return {}
    
    def get_user_activity_details(self, user_id: int = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get detailed user activity logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if user_id:
                    cursor.execute('''
                        SELECT ual.*, u.username, u.email
                        FROM user_activity_log ual
                        JOIN users u ON ual.user_id = u.id
                        WHERE ual.user_id = ? 
                        AND ual.created_at >= date('now', '-{} days')
                        AND date(ual.created_at) <= date('now')
                        ORDER BY ual.created_at DESC
                    '''.format(days), (user_id,))
                else:
                    cursor.execute('''
                        SELECT ual.*, u.username, u.email
                        FROM user_activity_log ual
                        JOIN users u ON ual.user_id = u.id
                        WHERE ual.created_at >= date('now', '-{} days')
                        AND date(ual.created_at) <= date('now')
                        ORDER BY ual.created_at DESC
                    '''.format(days))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting user activity details: {e}")
            return []
    
    def create_visualization_charts(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization charts for analytics data"""
        charts = {}
        
        try:
            # User registrations over time
            if analytics.get('registrations_over_time'):
                reg_data = analytics['registrations_over_time']
                df_reg = pd.DataFrame(reg_data)
                df_reg['reg_date'] = pd.to_datetime(df_reg['reg_date'])
                
                fig_reg = px.line(df_reg, x='reg_date', y='count', 
                                 title='User Registrations Over Time',
                                 labels={'reg_date': 'Date', 'count': 'New Users'})
                charts['User Registrations'] = fig_reg
            
            # Login activity
            if analytics.get('login_activity'):
                login_data = analytics['login_activity']
                df_login = pd.DataFrame(login_data)
                df_login['login_date'] = pd.to_datetime(df_login['login_date'])
                
                fig_login = px.bar(df_login, x='login_date', y='count',
                                  title='Daily Login Activity',
                                  labels={'login_date': 'Date', 'count': 'Logins'})
                charts['Login Activity'] = fig_login
            
            # Users by education level
            if analytics.get('users_by_education'):
                edu_data = analytics['users_by_education']
                fig_edu = px.pie(values=list(edu_data.values()), 
                                names=list(edu_data.keys()),
                                title='Users by Education Level')
                charts['Education Distribution'] = fig_edu
            
            # Feature usage
            if analytics.get('feature_usage'):
                feature_data = analytics['feature_usage']
                fig_features = px.bar(x=list(feature_data.keys()), 
                                     y=list(feature_data.values()),
                                     title='Feature Usage Statistics',
                                     labels={'x': 'Feature', 'y': 'Usage Count'})
                charts['Feature Usage'] = fig_features
            
            # Activity summary
            if analytics.get('activity_summary'):
                activity_data = analytics['activity_summary']
                fig_activity = px.bar(x=list(activity_data.keys()), 
                                     y=list(activity_data.values()),
                                     title='Activity Types Distribution',
                                     labels={'x': 'Activity Type', 'y': 'Count'})
                charts['Activity Types'] = fig_activity
            
        except Exception as e:
            print(f"Error creating charts: {e}")
        
        return charts
    
    def get_user_engagement_metrics(self, user_id: int = None) -> Dict[str, Any]:
        """Get user engagement metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                metrics = {}
                
                if user_id:
                    # Individual user metrics
                    cursor.execute('''
                        SELECT 
                            COUNT(DISTINCT DATE(created_at)) as active_days,
                            COUNT(*) as total_activities,
                            AVG(session_duration) as avg_session_duration
                        FROM user_activity_log 
                        WHERE user_id = ? AND created_at >= date('now', '-30 days')
                    ''', (user_id,))
                    
                    user_metrics = cursor.fetchone()
                    metrics['active_days'] = user_metrics['active_days'] or 0
                    metrics['total_activities'] = user_metrics['total_activities'] or 0
                    metrics['avg_session_duration'] = round(user_metrics['avg_session_duration'] or 0, 2)
                    
                    # Feature usage for user
                    cursor.execute('''
                        SELECT feature_name, usage_count, total_time_spent
                        FROM feature_usage 
                        WHERE user_id = ? AND last_used >= date('now', '-30 days')
                        ORDER BY usage_count DESC
                    ''', (user_id,))
                    metrics['feature_usage'] = [dict(row) for row in cursor.fetchall()]
                    
                else:
                    # Overall metrics
                    cursor.execute('''
                        SELECT 
                            COUNT(DISTINCT user_id) as active_users,
                            COUNT(*) as total_activities,
                            AVG(session_duration) as avg_session_duration
                        FROM user_activity_log 
                        WHERE created_at >= date('now', '-30 days')
                    ''')
                    
                    overall_metrics = cursor.fetchone()
                    metrics['active_users'] = overall_metrics['active_users'] or 0
                    metrics['total_activities'] = overall_metrics['total_activities'] or 0
                    metrics['avg_session_duration'] = round(overall_metrics['avg_session_duration'] or 0, 2)
                
                return metrics
                
        except Exception as e:
            print(f"Error getting engagement metrics: {e}")
            return {}

# Global analytics manager instance
_analytics_manager = None

def get_analytics_manager() -> AnalyticsManager:
    """Get global analytics manager instance"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager