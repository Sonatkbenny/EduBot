#!/usr/bin/env python3
"""
Direct admin creation script
"""

from database.user_models import get_user_database
from utils.auth import get_auth_manager

def create_admin():
    """Create admin user directly"""
    user_db = get_user_database()
    auth_manager = get_auth_manager()
    
    print("Creating admin user...")
    
    # Admin credentials
    username = "admin"
    email = "admin@edubot.com"
    full_name = "Administrator"
    password = "admin123"
    
    # Create user
    password_hash = auth_manager.hash_password(password)
    success, message, user_id = user_db.create_user(
        username, email, full_name, password_hash, "Graduate"
    )
    
    if success:
        # Make user admin
        if user_db.make_user_admin(user_id):
            print(f"SUCCESS: Admin user created!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Email: {email}")
            print(f"User ID: {user_id}")
        else:
            print("WARNING: User created but failed to set admin privileges")
    else:
        print(f"ERROR: Failed to create user: {message}")
        
    # List all users
    print("\nCurrent users:")
    users = user_db.get_all_users()
    for user in users:
        status = "ADMIN" if user.get('is_admin') else "USER"
        print(f"  ID: {user['id']} | {user['username']} ({user['email']}) - {status}")

if __name__ == "__main__":
    create_admin()
