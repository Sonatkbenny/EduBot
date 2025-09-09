#!/usr/bin/env python3
"""
Setup script to create or promote a user to admin status
"""

import sys
from database.user_models import get_user_database
from utils.auth import get_auth_manager

def setup_admin():
    """Setup admin user"""
    user_db = get_user_database()
    auth_manager = get_auth_manager()
    
    print("Admin Setup for EduBot")
    print("=" * 40)
    
    # Option 1: Create new admin user
    print("\n1. Create New Admin User")
    print("2. Promote Existing User to Admin")
    print("3. List All Users")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == "1":
        create_new_admin(user_db, auth_manager)
    elif choice == "2":
        promote_existing_user(user_db)
    elif choice == "3":
        list_all_users(user_db)
    else:
        print("Invalid choice")

def create_new_admin(user_db, auth_manager):
    """Create a new admin user"""
    print("\nCreating New Admin User")
    print("-" * 30)
    
    username = input("Enter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    full_name = input("Enter full name: ").strip()
    password = input("Enter admin password: ").strip()
    
    if not all([username, email, full_name, password]):
        print("ERROR: All fields are required")
        return
    
    # Create user
    password_hash = auth_manager.hash_password(password)
    success, message, user_id = user_db.create_user(
        username, email, full_name, password_hash, "Graduate"
    )
    
    if success:
        # Make user admin
        if user_db.make_user_admin(user_id):
            print(f"SUCCESS: Admin user '{username}' created successfully!")
            print(f"Email: {email}")
            print(f"User ID: {user_id}")
        else:
            print(f"WARNING: User created but failed to set admin privileges")
    else:
        print(f"ERROR: Failed to create user: {message}")

def promote_existing_user(user_db):
    """Promote an existing user to admin"""
    print("\nPromote Existing User to Admin")
    print("-" * 35)
    
    # List users first
    users = user_db.get_all_users()
    if not users:
        print("ERROR: No users found")
        return
    
    print("\nExisting Users:")
    for user in users:
        status = "ADMIN" if user.get('is_admin') else "USER"
        print(f"  ID: {user['id']} | {user['username']} ({user['email']}) - {status}")
    
    try:
        user_id = int(input("\nEnter User ID to promote: ").strip())
        
        # Find user
        target_user = next((u for u in users if u['id'] == user_id), None)
        if not target_user:
            print("ERROR: User not found")
            return
        
        if target_user.get('is_admin'):
            print(f"WARNING: User '{target_user['username']}' is already an admin")
            return
        
        # Promote to admin
        if user_db.make_user_admin(user_id):
            print(f"SUCCESS: User '{target_user['username']}' promoted to admin!")
        else:
            print("ERROR: Failed to promote user")
            
    except ValueError:
        print("ERROR: Invalid User ID")

def list_all_users(user_db):
    """List all users"""
    print("\nAll Users")
    print("-" * 20)
    
    users = user_db.get_all_users()
    if not users:
        print("ERROR: No users found")
        return
    
    for user in users:
        status = "ADMIN" if user.get('is_admin') else "USER"
        active = "ACTIVE" if user.get('is_active') else "INACTIVE"
        print(f"ID: {user['id']}")
        print(f"  Username: {user['username']}")
        print(f"  Email: {user['email']}")
        print(f"  Full Name: {user['full_name']}")
        print(f"  Status: {status} | {active}")
        print(f"  Created: {user['created_at']}")
        print("-" * 40)

if __name__ == "__main__":
    try:
        setup_admin()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
