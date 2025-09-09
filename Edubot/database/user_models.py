#!/usr/bin/env python3
"""
User database models for EduBot
Handles user data storage, retrieval, and validation
"""

import sqlite3
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

class UserDatabase:
    """SQLite-based user database for local development"""
    
    def __init__(self, db_path: str = "edubot_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        education_level TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_admin BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Check if is_admin column exists and add if not (for existing databases)
                cursor.execute("PRAGMA table_info(users)")
                columns = [column[1] for column in cursor.fetchall()]
                if 'is_admin' not in columns:
                    cursor.execute('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE')
                
                # Create password reset tokens table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        token TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        used BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create user sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_token TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                
        except Exception as e:
            print(f"Database initialization error: {e}")
    
    def create_user(self, username: str, email: str, full_name: str, 
                   password_hash: str, education_level: str) -> Tuple[bool, str, Optional[int]]:
        """Create a new user in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for existing username
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return False, "Username already exists", None
                
                # Check for existing email
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    return False, "Email already exists", None
                
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (username, email, full_name, password_hash, education_level)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, full_name, password_hash, education_level))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                return True, "User created successfully", user_id
                
        except Exception as e:
            return False, f"Database error: {str(e)}", None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, password_hash, 
                           education_level, created_at, last_login, is_active, is_admin
                    FROM users WHERE username = ? AND is_active = TRUE
                ''', (username,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'password_hash': row[4],
                        'education_level': row[5],
                        'created_at': row[6],
                        'last_login': row[7],
                        'is_active': row[8],
                        'is_admin': bool(row[9])
                    }
                
        except Exception as e:
            print(f"Database error: {e}")
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, password_hash, 
                           education_level, created_at, last_login, is_active, is_admin
                    FROM users WHERE email = ? AND is_active = TRUE
                ''', (email,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'password_hash': row[4],
                        'education_level': row[5],
                        'created_at': row[6],
                        'last_login': row[7],
                        'is_active': row[8],
                        'is_admin': bool(row[9])
                    }
                
        except Exception as e:
            print(f"Database error: {e}")
        
        return None
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def update_password(self, email: str, new_password_hash: str) -> bool:
        """Update user's password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET password_hash = ? 
                    WHERE email = ? AND is_active = TRUE
                ''', (new_password_hash, email))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    return True
                
        except Exception as e:
            print(f"Database error: {e}")
        
        return False
    
    def store_password_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Store password reset token"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Invalidate existing tokens for this email
                cursor.execute('''
                    UPDATE password_reset_tokens 
                    SET used = TRUE 
                    WHERE email = ? AND used = FALSE
                ''', (email,))
                
                # Insert new token
                cursor.execute('''
                    INSERT INTO password_reset_tokens (email, token, expires_at)
                    VALUES (?, ?, ?)
                ''', (email, token, expires_at))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email if valid"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT email FROM password_reset_tokens 
                    WHERE token = ? AND used = FALSE AND expires_at > CURRENT_TIMESTAMP
                ''', (token,))
                
                row = cursor.fetchone()
                if row:
                    # Mark token as used
                    cursor.execute('''
                        UPDATE password_reset_tokens 
                        SET used = TRUE 
                        WHERE token = ?
                    ''', (token,))
                    conn.commit()
                    
                    return row[0]
                
        except Exception as e:
            print(f"Database error: {e}")
        
        return None
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total users
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
                total_users = cursor.fetchone()[0]
                
                # Users by education level
                cursor.execute('''
                    SELECT education_level, COUNT(*) 
                    FROM users WHERE is_active = TRUE 
                    GROUP BY education_level
                ''')
                education_stats = dict(cursor.fetchall())
                
                return {
                    'total_users': total_users,
                    'education_stats': education_stats,
                    'last_updated': datetime.now()
                }
                
        except Exception as e:
            print(f"Database error: {e}")
            return {'total_users': 0, 'education_stats': {}, 'last_updated': datetime.now()}
    
    def make_user_admin(self, user_id: int) -> bool:
        """Make a user an admin"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_admin = TRUE WHERE id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Database error making user admin: {e}")
            return False
    
    def remove_admin_privileges(self, user_id: int) -> bool:
        """Remove admin privileges from a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET is_admin = FALSE WHERE id = ?', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Database error removing admin privileges: {e}")
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users for admin management"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, username, email, full_name, education_level, 
                           created_at, last_login, is_active, is_admin
                    FROM users ORDER BY created_at DESC
                ''')
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'education_level': row[4],
                        'created_at': row[5],
                        'last_login': row[6],
                        'is_active': bool(row[7]),
                        'is_admin': bool(row[8])
                    })
                
                return users
                
        except Exception as e:
            print(f"Database error getting all users: {e}")
            return []
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a raw SQL query (for admin functions)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return [dict(row) for row in cursor.fetchall()]
                else:
                    conn.commit()
                    return []
                    
        except Exception as e:
            print(f"Database error executing query: {e}")
            return []
    
    def get_all_users_activity(self) -> List[Dict[str, Any]]:
        """Get user activity data for admin dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, email, last_login, created_at,
                           0 as quiz_count, 0 as document_count, last_login as last_activity
                    FROM users 
                    WHERE is_active = TRUE
                    ORDER BY last_login DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Database error getting user activity: {e}")
            return []
    
    def get_total_users(self) -> int:
        """Get total number of active users"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = TRUE')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Database error getting total users: {e}")
            return 0
    
    def get_comprehensive_analytics(self, start_date=None, end_date=None):
        """Get comprehensive analytics data for admin dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                analytics = {}
                
                # User Overview
                cursor.execute('SELECT COUNT(*) as total FROM users WHERE is_active = TRUE')
                analytics['total_users'] = cursor.fetchone()['total']
                
                # Active users (users who logged in within last 30 days)
                cursor.execute('''
                    SELECT COUNT(*) as active 
                    FROM users 
                    WHERE is_active = TRUE AND 
                    (last_login IS NULL OR date(last_login) >= date('now', '-30 days'))
                ''')
                analytics['active_users_month'] = cursor.fetchone()['active']
                
                # Active users this week
                cursor.execute('''
                    SELECT COUNT(*) as active 
                    FROM users 
                    WHERE is_active = TRUE AND 
                    (last_login IS NULL OR date(last_login) >= date('now', '-7 days'))
                ''')
                analytics['active_users_week'] = cursor.fetchone()['active']
                
                # Users by education level
                cursor.execute('''
                    SELECT education_level, COUNT(*) as count 
                    FROM users 
                    WHERE is_active = TRUE 
                    GROUP BY education_level
                ''')
                analytics['users_by_education'] = dict(cursor.fetchall())
                
                # User registrations over time (last 30 days)
                cursor.execute('''
                    SELECT date(created_at) as reg_date, COUNT(*) as count
                    FROM users 
                    WHERE created_at >= date('now', '-30 days')
                    GROUP BY date(created_at)
                    ORDER BY reg_date
                ''')
                analytics['registrations_over_time'] = [dict(row) for row in cursor.fetchall()]
                
                # Login activity (last 30 days)
                cursor.execute('''
                    SELECT date(last_login) as login_date, COUNT(*) as count
                    FROM users 
                    WHERE last_login >= date('now', '-30 days')
                    GROUP BY date(last_login)
                    ORDER BY login_date
                ''')
                analytics['login_activity'] = [dict(row) for row in cursor.fetchall()]
                
                # Admin count
                cursor.execute('SELECT COUNT(*) as admin_count FROM users WHERE is_admin = TRUE')
                analytics['admin_count'] = cursor.fetchone()['admin_count']
                
                return analytics
                
        except Exception as e:
            print(f"Database error getting analytics: {e}")
            return {}
    
    def get_user_activity_logs(self, days=30):
        """Get user activity logs for the specified number of days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get user activity summary
                cursor.execute('''
                    SELECT 
                        username, 
                        email, 
                        last_login,
                        created_at,
                        is_admin,
                        CASE 
                            WHEN last_login >= date('now', '-7 days') THEN 'This Week'
                            WHEN last_login >= date('now', '-30 days') THEN 'This Month'
                            WHEN last_login IS NOT NULL THEN 'Older'
                            ELSE 'Never'
                        END as activity_status
                    FROM users 
                    WHERE is_active = TRUE
                    ORDER BY last_login DESC
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Database error getting activity logs: {e}")
            return []
    
    def get_engagement_metrics(self):
        """Get user engagement metrics"""
        # Since we don't have quiz/document tables yet, return mock data
        # This should be implemented when those tables are created
        return {
            'total_quizzes': 0,
            'total_documents': 0,
            'total_recommendations': 0,
            'avg_quizzes_per_user': 0,
            'avg_documents_per_user': 0,
            'quiz_completion_rate': 0
        }
    
    def get_performance_analytics(self):
        """Get performance analytics across all users"""
        # Mock data for now - should be implemented with actual performance data
        return {
            'avg_quiz_score': 0,
            'strong_topics': [],
            'weak_topics': [],
            'performance_trends': []
        }

# Global database instance
_user_db = None

def get_user_database() -> UserDatabase:
    """Get global user database instance"""
    global _user_db
    if _user_db is None:
        _user_db = UserDatabase()
    return _user_db
