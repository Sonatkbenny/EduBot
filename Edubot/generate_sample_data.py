#!/usr/bin/env python3
"""
Sample data generator for EduBot
Generates realistic user activity data for testing the admin dashboard
"""

import random
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Sample data for generating realistic activities
ACTIVITY_TYPES = [
    "page_visit", "feature_usage", "quiz_completion", "document_processing",
    "performance_analysis", "recommendation_view", "user_login", "user_logout"
]

PAGES = [
    "Home", "Text Summarization", "Quiz Generation", "Performance Analysis", 
    "Recommendations", "Authentication"
]

FEATURES = [
    "Text Summarization", "Quiz Generation", "PDF Upload", "Performance Dashboard",
    "Resource Recommendations", "Topic Selection", "Quiz Taking", "Results Review"
]

QUIZ_TOPICS = [
    "Mathematics", "Science", "History", "Literature", "Physics", "Chemistry",
    "Biology", "Computer Science", "Geography", "Art", "Music", "Philosophy"
]

SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology", "History", "Literature",
    "Computer Science", "Geography", "Art", "Economics", "Psychology"
]

def generate_sample_users(db_path: str = "edubot_users.db", num_users: int = 50):
    """Generate sample users if they don't exist"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if users already exist
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count >= num_users:
                print(f"Already have {user_count} users in database")
                return
            
            # Generate sample users
            education_levels = ["High School", "Bachelor's", "Master's", "PhD", "Other"]
            
            for i in range(num_users):
                username = f"user_{i+1:03d}"
                email = f"user{i+1}@example.com"
                full_name = f"User {i+1}"
                password_hash = "$2b$12$dummy_hash_for_testing"  # Dummy hash
                education_level = random.choice(education_levels)
                
                # Create registration date between 90 days ago and today
                reg_date = datetime.now() - timedelta(days=random.randint(1, 90))
                
                # Create last login date (some users never logged in, others within valid range)
                if random.random() > 0.2:  # 80% of users have logged in
                    # Ensure last login is between registration and today
                    max_days_since_reg = min(30, (datetime.now() - reg_date).days)
                    if max_days_since_reg > 0:
                        last_login = reg_date + timedelta(days=random.randint(0, max_days_since_reg))
                    else:
                        last_login = reg_date
                else:
                    last_login = None
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO users 
                        (username, email, full_name, password_hash, education_level, created_at, last_login)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (username, email, full_name, password_hash, education_level, 
                         reg_date.isoformat(), last_login.isoformat() if last_login else None))
                except Exception as e:
                    print(f"Error creating user {username}: {e}")
            
            conn.commit()
            print(f"Generated {num_users} sample users")
            
    except Exception as e:
        print(f"Error generating sample users: {e}")

def generate_user_activities(db_path: str = "edubot_users.db", days_back: int = 30):
    """Generate realistic user activity data"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get all users
            cursor.execute("SELECT id, username FROM users WHERE is_active = TRUE")
            users = cursor.fetchall()
            
            if not users:
                print("No users found. Generate users first.")
                return
            
            # Clear existing activity data to avoid duplicates
            cursor.execute("DELETE FROM user_activity_log")
            cursor.execute("DELETE FROM feature_usage")
            cursor.execute("DELETE FROM quiz_analytics")
            cursor.execute("DELETE FROM document_analytics")
            cursor.execute("DELETE FROM performance_analytics")
            
            activities_generated = 0
            
            for user_id, username in users:
                # Generate random number of activities per user
                num_activities = random.randint(5, 50)
                
                for _ in range(num_activities):
                    # Generate activity within the last 'days_back' days (but not in future)
                    days_ago = random.randint(0, days_back)
                    hours_ago = random.randint(0, 23)
                    minutes_ago = random.randint(0, 59)
                    
                    activity_date = datetime.now() - timedelta(
                        days=days_ago,
                        hours=hours_ago,
                        minutes=minutes_ago
                    )
                    
                    # Ensure activity date is not in the future
                    if activity_date > datetime.now():
                        activity_date = datetime.now() - timedelta(hours=random.randint(1, 24))
                    
                    activity_type = random.choice(ACTIVITY_TYPES)
                    page = random.choice(PAGES)
                    session_duration = random.randint(30, 1800)  # 30 seconds to 30 minutes
                    
                    # Generate activity-specific descriptions
                    if activity_type == "page_visit":
                        description = f"Visited {page}"
                    elif activity_type == "feature_usage":
                        feature = random.choice(FEATURES)
                        description = f"Used {feature}"
                    elif activity_type == "quiz_completion":
                        topic = random.choice(QUIZ_TOPICS)
                        score = random.randint(40, 100)
                        description = f"Completed quiz on {topic} with score {score}%"
                    elif activity_type == "document_processing":
                        doc_name = f"document_{random.randint(1, 100)}.pdf"
                        description = f"Processed document: {doc_name}"
                    elif activity_type == "performance_analysis":
                        subject = random.choice(SUBJECTS)
                        description = f"Analyzed performance in {subject}"
                    elif activity_type == "recommendation_view":
                        topic = random.choice(QUIZ_TOPICS)
                        count = random.randint(3, 15)
                        description = f"Viewed {count} recommendations for {topic}"
                    elif activity_type == "user_login":
                        description = "User logged in via standard"
                    else:  # user_logout
                        description = "User logged out"
                    
                    # Insert activity log
                    cursor.execute('''
                        INSERT INTO user_activity_log 
                        (user_id, activity_type, activity_description, page_visited, 
                         session_duration, created_at, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, activity_type, description, page, 
                         session_duration, activity_date.isoformat(), 
                         json.dumps({'generated': True})))
                    
                    activities_generated += 1
            
            # Generate feature usage data
            print("Generating feature usage data...")
            for user_id, username in users:
                for feature in FEATURES:
                    if random.random() > 0.3:  # 70% chance user used this feature
                        usage_count = random.randint(1, 20)
                        total_time = usage_count * random.randint(60, 600)  # 1-10 minutes per use
                        
                        # Ensure last_used is not in the future
                        days_ago = random.randint(0, days_back)
                        last_used = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                        if last_used > datetime.now():
                            last_used = datetime.now() - timedelta(hours=random.randint(1, 24))
                        
                        cursor.execute('''
                            INSERT INTO feature_usage 
                            (user_id, feature_name, usage_count, last_used, total_time_spent)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (user_id, feature, usage_count, last_used.isoformat(), total_time))
            
            # Generate quiz analytics
            print("Generating quiz analytics...")
            for user_id, username in users:
                num_quizzes = random.randint(0, 15)
                for i in range(num_quizzes):
                    topic = random.choice(QUIZ_TOPICS)
                    questions_count = random.randint(5, 20)
                    correct_answers = random.randint(0, questions_count)
                    total_score = (correct_answers / questions_count) * 100
                    completion_time = random.randint(180, 1800)  # 3-30 minutes
                    difficulty_level = random.choice(['easy', 'medium', 'hard'])
                    
                    # Ensure quiz date is not in the future
                    days_ago = random.randint(0, days_back)
                    quiz_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                    if quiz_date > datetime.now():
                        quiz_date = datetime.now() - timedelta(hours=random.randint(1, 24))
                    
                    cursor.execute('''
                        INSERT INTO quiz_analytics 
                        (user_id, quiz_id, topic, questions_count, correct_answers, 
                         total_score, completion_time, difficulty_level, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, f"quiz_{user_id}_{i}", topic, questions_count, 
                         correct_answers, total_score, completion_time, 
                         difficulty_level, quiz_date.isoformat()))
            
            # Generate document analytics
            print("Generating document analytics...")
            for user_id, username in users:
                num_documents = random.randint(0, 10)
                for i in range(num_documents):
                    doc_name = f"document_{random.randint(1, 1000)}.pdf"
                    doc_size = random.randint(1024, 10485760)  # 1KB to 10MB
                    processing_time = random.randint(5, 120)  # 5 seconds to 2 minutes
                    summary_length = random.randint(100, 1000)  # characters
                    
                    # Ensure document date is not in the future
                    days_ago = random.randint(0, days_back)
                    doc_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                    if doc_date > datetime.now():
                        doc_date = datetime.now() - timedelta(hours=random.randint(1, 24))
                    
                    cursor.execute('''
                        INSERT INTO document_analytics 
                        (user_id, document_name, document_size, processing_time, 
                         summary_length, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (user_id, doc_name, doc_size, processing_time, 
                         summary_length, doc_date.isoformat()))
            
            # Generate performance analytics
            print("Generating performance analytics...")
            for user_id, username in users:
                num_performances = random.randint(0, 8)
                for i in range(num_performances):
                    subject = random.choice(SUBJECTS)
                    topic = random.choice(QUIZ_TOPICS)
                    score = random.uniform(0, 100)
                    total_possible = 100
                    time_taken = random.randint(300, 3600)  # 5 minutes to 1 hour
                    improvement_rate = random.uniform(-10, 15)  # -10% to +15%
                    
                    # Ensure performance date is not in the future
                    days_ago = random.randint(0, days_back)
                    perf_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                    if perf_date > datetime.now():
                        perf_date = datetime.now() - timedelta(hours=random.randint(1, 24))
                    
                    cursor.execute('''
                        INSERT INTO performance_analytics 
                        (user_id, subject, topic, score, total_possible, 
                         time_taken, improvement_rate, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, subject, topic, score, total_possible, 
                         time_taken, improvement_rate, perf_date.isoformat()))
            
            conn.commit()
            print(f"Generated {activities_generated} user activities and related analytics data")
            
    except Exception as e:
        print(f"Error generating sample data: {e}")

def main():
    """Main function to generate all sample data"""
    print("Generating sample data for EduBot...")
    
    # Generate sample users
    print("Step 1: Generating sample users...")
    generate_sample_users(num_users=25)
    
    # Generate user activities
    print("Step 2: Generating user activities...")
    generate_user_activities(days_back=30)
    
    print("Sample data generation completed!")
    print("\nYou can now:")
    print("1. Run the application: streamlit run app.py")
    print("2. Login as admin and check the User Activities section")
    print("3. View the analytics dashboard with real data")

if __name__ == "__main__":
    main()
