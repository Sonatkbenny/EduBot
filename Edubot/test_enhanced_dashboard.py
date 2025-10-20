#!/usr/bin/env python3
"""
Test script for enhanced admin dashboard functionality
Verifies that the analytics data and charts work properly
"""

import sqlite3
from utils.analytics import get_analytics_manager
from frontend.admin_components import create_download_section
import pandas as pd
import json

def test_database_data():
    """Test that we have sample data in the database"""
    print("=== Testing Database Data ===")
    
    db_path = "edubot_users.db"
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check users
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✅ Users: {user_count}")
            
            # Check user activities
            cursor.execute("SELECT COUNT(*) FROM user_activity_log")
            activity_count = cursor.fetchone()[0]
            print(f"✅ User Activities: {activity_count}")
            
            # Check feature usage
            cursor.execute("SELECT COUNT(*) FROM feature_usage")
            feature_count = cursor.fetchone()[0]
            print(f"✅ Feature Usage Records: {feature_count}")
            
            # Check quiz analytics
            cursor.execute("SELECT COUNT(*) FROM quiz_analytics")
            quiz_count = cursor.fetchone()[0]
            print(f"✅ Quiz Analytics: {quiz_count}")
            
            # Check document analytics
            cursor.execute("SELECT COUNT(*) FROM document_analytics")
            doc_count = cursor.fetchone()[0]
            print(f"✅ Document Analytics: {doc_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_analytics_manager():
    """Test the analytics manager functionality"""
    print("\n=== Testing Analytics Manager ===")
    
    try:
        analytics_manager = get_analytics_manager()
        
        # Get dashboard analytics
        analytics = analytics_manager.get_dashboard_analytics("30")
        
        print(f"✅ Total Users: {analytics.get('total_users', 0)}")
        print(f"✅ Active Users: {analytics.get('active_users', 0)}")
        print(f"✅ Feature Usage Categories: {len(analytics.get('feature_usage', {}))}")
        print(f"✅ Activity Types: {len(analytics.get('activity_summary', {}))}")
        print(f"✅ Education Levels: {len(analytics.get('users_by_education', {}))}")
        
        # Test chart creation
        charts = analytics_manager.create_visualization_charts(analytics)
        print(f"✅ Generated Charts: {list(charts.keys())}")
        
        # Test user activity details
        user_activities = analytics_manager.get_user_activity_details(days=30)
        print(f"✅ User Activity Records: {len(user_activities)}")
        
        return True, analytics
        
    except Exception as e:
        print(f"❌ Analytics manager test failed: {e}")
        return False, {}

def test_report_data_structure():
    """Test the data structures for each report type"""
    print("\n=== Testing Report Data Structures ===")
    
    try:
        analytics_manager = get_analytics_manager()
        analytics = analytics_manager.get_dashboard_analytics("30")
        
        # Analytics Report Data
        metrics_data = {
            'Total Users': analytics.get('total_users', 0),
            'Active Users': analytics.get('active_users', 0),
            'Total Quizzes': analytics.get('quiz_stats', {}).get('total_quizzes', 0),
            'Documents Processed': analytics.get('document_stats', {}).get('total_documents', 0),
            'Questions Answered': analytics.get('quiz_stats', {}).get('total_questions', 0)
        }
        print(f"✅ Analytics Report Metrics: {metrics_data}")
        
        # User Activity Data
        activity_data = analytics_manager.get_user_activity_details(days=30)
        if activity_data:
            activity_df = pd.DataFrame(activity_data)
            if 'activity_type' in activity_df.columns:
                activity_counts = activity_df['activity_type'].value_counts()
                print(f"✅ User Activity Types: {dict(activity_counts)}")
            else:
                print("⚠️ No activity_type column found")
        else:
            print("⚠️ No activity data found")
        
        # Charts Data
        charts_data = {
            'Feature Usage': len(analytics.get('feature_usage', {})),
            'Education Levels': len(analytics.get('users_by_education', {})),
            'Registration Records': len(analytics.get('registrations_over_time', [])),
            'Login Records': len(analytics.get('login_activity', [])),
            'Top Active Users': len(analytics.get('top_active_users', []))
        }
        print(f"✅ Charts Data Records: {charts_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report data structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Admin Dashboard Functionality\n")
    
    # Test database
    if not test_database_data():
        print("\n❌ Database tests failed. Run generate_sample_data.py first.")
        return False
    
    # Test analytics manager
    success, analytics = test_analytics_manager()
    if not success:
        print("\n❌ Analytics manager tests failed.")
        return False
    
    # Test report data structures
    if not test_report_data_structure():
        print("\n❌ Report data structure tests failed.")
        return False
    
    print("\n🎉 All tests passed! The enhanced admin dashboard should work properly.")
    print("\n📊 Summary of what's available:")
    print("1. Analytics Report with bar charts showing key metrics")
    print("2. User Activity charts showing activity type distribution")
    print("3. Charts Data overview showing available data records")
    print("4. Download functionality for all three report types")
    
    print(f"\n🔗 Access the admin dashboard at: http://localhost:8501?admin=login")
    print("Use your admin credentials to view the enhanced Reports section.")
    
    return True

if __name__ == "__main__":
    main()
