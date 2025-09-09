#!/usr/bin/env python3
"""
Test script for user management functionality
"""

from database.user_models import get_user_database

def test_user_management():
    """Test user management functions"""
    print("Testing User Management Functionality")
    print("=" * 40)
    
    user_db = get_user_database()
    
    # Test get_all_users
    print("\n1. Testing get_all_users():")
    all_users = user_db.get_all_users()
    print(f"  Total users found: {len(all_users)}")
    
    if all_users:
        print("  User list:")
        for i, user in enumerate(all_users[:3]):  # Show first 3
            print(f"    {i+1}. {user['username']} ({user['email']}) - Admin: {user.get('is_admin', False)}")
    
    # Test execute_query method
    print("\n2. Testing execute_query method:")
    try:
        query_result = user_db.execute_query("SELECT COUNT(*) as count FROM users")
        if query_result:
            print(f"  Query result: {query_result[0]}")
        else:
            print("  Query returned no results")
    except Exception as e:
        print(f"  Execute query error: {e}")
    
    # Test admin management methods
    print("\n3. Testing admin management:")
    
    # Find a non-admin user for testing
    test_user = None
    for user in all_users:
        if not user.get('is_admin'):
            test_user = user
            break
    
    if test_user:
        print(f"  Testing with user: {test_user['username']} (ID: {test_user['id']})")
        
        # Test make_user_admin
        print("  Testing make_user_admin...")
        success = user_db.make_user_admin(test_user['id'])
        print(f"    Make admin result: {success}")
        
        # Test remove_admin_privileges  
        print("  Testing remove_admin_privileges...")
        success = user_db.remove_admin_privileges(test_user['id'])
        print(f"    Remove admin result: {success}")
    else:
        print("  No non-admin user found for testing")
    
    # Test comprehensive analytics 
    print("\n4. Testing comprehensive analytics:")
    analytics = user_db.get_comprehensive_analytics()
    print(f"  Total users: {analytics.get('total_users', 0)}")
    print(f"  Active users (month): {analytics.get('active_users_month', 0)}")
    print(f"  Admin count: {analytics.get('admin_count', 0)}")
    print(f"  Users by education: {analytics.get('users_by_education', {})}")
    
    # Test user activity logs
    print("\n5. Testing user activity logs:")
    activity_logs = user_db.get_user_activity_logs()
    print(f"  Activity log entries: {len(activity_logs)}")
    
    if activity_logs:
        print("  Sample activities:")
        for i, log in enumerate(activity_logs[:2]):
            print(f"    {i+1}. {log.get('username')} - Status: {log.get('activity_status')}")
    
    print("\n✅ User management testing completed!")

if __name__ == "__main__":
    test_user_management()
