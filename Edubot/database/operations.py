from config.database import DatabaseConnection
from database.models import User, Document, Quiz, Performance, Recommendation, UserProfile
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class DatabaseOperations:
    """Database operations for EduBot"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create_user(self, username: str, email: str) -> Optional[User]:
        """Create a new user"""
        try:
            query = """
            INSERT INTO users (username, email) 
            VALUES (%s, %s) 
            RETURNING id, username, email, created_at
            """
            result = self.db.execute_query(query, (username, email))
            
            if result:
                user_data = result[0]
                return User.from_dict(user_data)
            return None
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            result = self.db.execute_query(query, (user_id,))
            
            if result:
                return User.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
            
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            result = self.db.execute_query(query, (username,))
            
            if result:
                return dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
            
    def get_all_users_activity(self) -> List[Dict[str, Any]]:
        """Get activity data for all users"""
        try:
            query = """
            SELECT 
                u.id, u.username, u.email, u.full_name, u.last_login,
                COUNT(DISTINCT q.id) as quiz_count,
                COUNT(DISTINCT d.id) as document_count,
                MAX(COALESCE(q.created_at, d.created_at)) as last_activity
            FROM users u
            LEFT JOIN quizzes q ON q.user_id = u.id
            LEFT JOIN documents d ON d.user_id = u.id
            GROUP BY u.id, u.username, u.email, u.full_name, u.last_login
            ORDER BY last_activity DESC NULLS LAST
            """
            
            results = self.db.execute_query(query)
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            print(f"Error getting user activity: {e}")
            return []
            
    def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            query = "SELECT COUNT(*) as count FROM users"
            result = self.db.execute_query(query)
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"Error getting total users: {e}")
            return 0
    
    def save_document(self, user_id: int, filename: str, content: str, summary: str = None) -> Optional[Document]:
        """Save document and summary"""
        try:
            query = """
            INSERT INTO documents (user_id, filename, content, summary) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id, user_id, filename, content, summary, created_at
            """
            result = self.db.execute_query(query, (user_id, filename, content, summary))
            
            if result:
                return Document.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error saving document: {e}")
            return None
    
    def get_user_documents(self, user_id: int) -> List[Document]:
        """Get all documents for a user"""
        try:
            query = "SELECT * FROM documents WHERE user_id = %s ORDER BY created_at DESC"
            results = self.db.execute_query(query, (user_id,))
            
            return [Document.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def save_quiz(self, user_id: int, topic: str, questions: List[Dict[str, Any]]) -> Optional[Quiz]:
        """Save generated quiz"""
        try:
            query = """
            INSERT INTO quizzes (user_id, topic, questions) 
            VALUES (%s, %s, %s) 
            RETURNING id, user_id, topic, questions, created_at
            """
            questions_json = json.dumps(questions)
            result = self.db.execute_query(query, (user_id, topic, questions_json))
            
            if result:
                return Quiz.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error saving quiz: {e}")
            return None
    
    def get_user_quizzes(self, user_id: int) -> List[Quiz]:
        """Get all quizzes for a user"""
        try:
            query = "SELECT * FROM quizzes WHERE user_id = %s ORDER BY created_at DESC"
            results = self.db.execute_query(query, (user_id,))
            
            return [Quiz.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting quizzes: {e}")
            return []
    
    def save_performance(self, user_id: int, subject: str, topic: str, 
                        score: float, total_marks: float, classification: str = None) -> Optional[Performance]:
        """Save performance data"""
        try:
            query = """
            INSERT INTO performance (user_id, subject, topic, score, total_marks, classification) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING id, user_id, subject, topic, score, total_marks, classification, created_at
            """
            result = self.db.execute_query(query, (user_id, subject, topic, score, total_marks, classification))
            
            if result:
                return Performance.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error saving performance: {e}")
            return None
    
    def get_user_performance(self, user_id: int) -> List[Performance]:
        """Get all performance data for a user"""
        try:
            query = "SELECT * FROM performance WHERE user_id = %s ORDER BY created_at DESC"
            results = self.db.execute_query(query, (user_id,))
            
            return [Performance.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting performance: {e}")
            return []
    
    def get_performance_by_subject(self, user_id: int, subject: str) -> List[Performance]:
        """Get performance data for a specific subject"""
        try:
            query = "SELECT * FROM performance WHERE user_id = %s AND subject = %s ORDER BY created_at DESC"
            results = self.db.execute_query(query, (user_id, subject))
            
            return [Performance.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting performance by subject: {e}")
            return []
    
    def save_recommendation(self, user_id: int, topic: str, resource_type: str, 
                          resource_url: str, title: str) -> Optional[Recommendation]:
        """Save recommendation"""
        try:
            query = """
            INSERT INTO recommendations (user_id, topic, resource_type, resource_url, title) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id, user_id, topic, resource_type, resource_url, title, created_at
            """
            result = self.db.execute_query(query, (user_id, topic, resource_type, resource_url, title))
            
            if result:
                return Recommendation.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error saving recommendation: {e}")
            return None
    
    def get_user_recommendations(self, user_id: int) -> List[Recommendation]:
        """Get all recommendations for a user"""
        try:
            query = "SELECT * FROM recommendations WHERE user_id = %s ORDER BY created_at DESC"
            results = self.db.execute_query(query, (user_id,))
            
            return [Recommendation.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def save_user_profile(self, user_id: int, interests: List[str], 
                         weak_topics: List[str], learning_style: str) -> bool:
        """Save or update user profile"""
        try:
            # Check if profile exists
            check_query = "SELECT id FROM user_profiles WHERE user_id = %s"
            existing = self.db.execute_query(check_query, (user_id,))
            
            interests_json = json.dumps(interests)
            weak_topics_json = json.dumps(weak_topics)
            
            if existing:
                # Update existing profile
                query = """
                UPDATE user_profiles 
                SET interests = %s, weak_topics = %s, learning_style = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """
                self.db.execute_query(query, (interests_json, weak_topics_json, learning_style, user_id))
            else:
                # Create new profile
                query = """
                INSERT INTO user_profiles (user_id, interests, weak_topics, learning_style) 
                VALUES (%s, %s, %s, %s)
                """
                self.db.execute_query(query, (user_id, interests_json, weak_topics_json, learning_style))
            
            return True
            
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            query = "SELECT * FROM user_profiles WHERE user_id = %s"
            result = self.db.execute_query(query, (user_id,))
            
            if result:
                return UserProfile.from_dict(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def get_performance_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get performance statistics for a user"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_tests,
                AVG(score/total_marks * 100) as average_percentage,
                MAX(score/total_marks * 100) as highest_percentage,
                MIN(score/total_marks * 100) as lowest_percentage,
                subject,
                COUNT(*) as subject_count
            FROM performance 
            WHERE user_id = %s 
            GROUP BY subject
            """
            results = self.db.execute_query(query, (user_id,))
            
            stats = {
                'subjects': {},
                'overall': {}
            }
            
            total_tests = 0
            total_percentage = 0
            
            for result in results:
                subject = result['subject']
                stats['subjects'][subject] = {
                    'total_tests': result['subject_count'],
                    'average_percentage': round(result['average_percentage'], 2),
                    'highest_percentage': round(result['highest_percentage'], 2),
                    'lowest_percentage': round(result['lowest_percentage'], 2)
                }
                total_tests += result['subject_count']
                total_percentage += result['average_percentage'] * result['subject_count']
            
            if total_tests > 0:
                stats['overall'] = {
                    'total_tests': total_tests,
                    'average_percentage': round(total_percentage / total_tests, 2)
                }
            
            return stats
            
        except Exception as e:
            print(f"Error getting performance statistics: {e}")
            return {}
    
    def delete_user_data(self, user_id: int) -> bool:
        """Delete all data for a user (for privacy)"""
        try:
            # Delete in order to respect foreign key constraints
            tables = ['recommendations', 'performance', 'quizzes', 'documents', 'user_profiles', 'users']
            
            for table in tables:
                query = f"DELETE FROM {table} WHERE user_id = %s"
                self.db.execute_query(query, (user_id,))
            
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        self.db.disconnect()

# Global database operations instance
def get_db_operations():
    """Get database operations instance"""
    return DatabaseOperations()


def get_user_database():
    """Get database operations instance for user-related operations"""
    return DatabaseOperations()






