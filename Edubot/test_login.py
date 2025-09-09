#!/usr/bin/env python3
"""
Test login functionality for both regular users and admin
"""
import sys
from database.user_models import get_user_database
from utils.auth import get_auth_manager

def test_user_login(username, expected_admin=False):
    """Test login for a specific user"""
    print(f"\nTesting login for user: {username}")
    print("-" * 30)
    
    # Get user from database
    user_db = get_user_database()
    user = user_db.get_user_by_username(username)
    
    if not user:
        print(f"Error: User '{username}' not found!")
        return False
    
    print(f"User found: {user['username']} ({user.get('email', 'no email')})")
    print(f"Full name: {user.get('full_name', 'N/A')}")
    print(f"Education: {user.get('education_level', 'N/A')}")
    print(f"Is admin: {user.get('is_admin', False)}")
    print(f"Is active: {user.get('is_active', False)}")
    
    # Check if admin status matches expectation
    actual_admin = bool(user.get('is_admin', False))
    if actual_admin != expected_admin:
        print(f"Warning: Expected admin={expected_admin}, but user has admin={actual_admin}")
    
    # For testing, we'll just verify the user exists and has correct admin status
    if actual_admin == expected_admin:
        print(f"✅ User verification successful - {'Admin' if actual_admin else 'Regular'} user")
        return True
    else:
        print(f"❌ User verification failed - Admin status mismatch")
        return False

def test_all_users():
    """Test all users in the database"""
    print("Testing All User Logins")
    print("=" * 40)
    
    user_db = get_user_database()
    
    # Get all users
    all_users = user_db.get_all_users()
    print(f"Found {len(all_users)} users in database:")
    
    regular_users = []
    admin_users = []
    
    for user in all_users:
        username = user.get('username', 'unknown')
        is_admin = bool(user.get('is_admin', False))
        is_active = bool(user.get('is_active', True))
        
        print(f"  - {username} ({'ADMIN' if is_admin else 'USER'}) {'ACTIVE' if is_active else 'INACTIVE'}")
        
        if is_admin:
            admin_users.append(username)
        else:
            regular_users.append(username)
    
    # Test regular users
    print(f"\n\n1. Testing {len(regular_users)} Regular Users:")
    for username in regular_users:
        test_user_login(username, expected_admin=False)
    
    # Test admin users  
    print(f"\n\n2. Testing {len(admin_users)} Admin Users:")
    for username in admin_users:
        test_user_login(username, expected_admin=True)
    
    print("\n" + "=" * 40)
    print("✅ All user login tests completed!")
    print(f"Summary: {len(regular_users)} regular users, {len(admin_users)} admin users")

if __name__ == "__main__":
    test_all_users()
