#!/usr/bin/env python3
"""
Test script for analytics functionality
"""

from utils.analytics import get_analytics_manager
from database.user_models import get_user_database

def test_analytics():
    """Test analytics functionality"""
    print("Testing Analytics Functionality")
    print("=" * 40)
    
    # Test database analytics
    print("\n1. Testing Database Analytics:")
    user_db = get_user_database()
    analytics_data = user_db.get_comprehensive_analytics()
    
    print(f"  Total Users: {analytics_data.get('total_users', 0)}")
    print(f"  Active Users (Month): {analytics_data.get('active_users_month', 0)}")
    print(f"  Active Users (Week): {analytics_data.get('active_users_week', 0)}")
    print(f"  Admin Count: {analytics_data.get('admin_count', 0)}")
    
    # Test analytics manager
    print("\n2. Testing Analytics Manager:")
    analytics_manager = get_analytics_manager()
    dashboard_analytics = analytics_manager.get_dashboard_analytics()
    
    print(f"  User Growth Rate: {dashboard_analytics.get('user_growth_rate', 0)}%")
    print(f"  Login Frequency: {dashboard_analytics.get('login_frequency', 0)}")
    print(f"  Last Updated: {dashboard_analytics.get('last_updated', 'Unknown')}")
    
    # Test charts generation
    print("\n3. Testing Chart Generation:")
    try:
        charts = analytics_manager.create_visualization_charts(dashboard_analytics)
        print(f"  Generated Charts: {list(charts.keys())}")
    except Exception as e:
        print(f"  Chart Generation Error: {e}")
    
    # Test report generation
    print("\n4. Testing Report Generation:")
    try:
        # Test PDF generation
        pdf_data = analytics_manager.generate_analytics_report(dashboard_analytics, "pdf")
        print(f"  PDF Report Size: {len(pdf_data)} bytes")
        
        # Test Excel generation
        excel_data = analytics_manager.generate_analytics_report(dashboard_analytics, "excel")
        print(f"  Excel Report Size: {len(excel_data)} bytes")
        
    except Exception as e:
        print(f"  Report Generation Error: {e}")
    
    print("\n5. User Activity Logs:")
    activity_logs = user_db.get_user_activity_logs(30)
    print(f"  Activity Log Entries: {len(activity_logs)}")
    
    if activity_logs:
        print("  Recent Activity:")
        for i, log in enumerate(activity_logs[:3]):
            print(f"    {i+1}. {log.get('username')} - {log.get('activity_status')}")
    
    print("\n✅ Analytics testing completed!")

if __name__ == "__main__":
    test_analytics()
