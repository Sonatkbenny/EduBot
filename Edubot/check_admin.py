#!/usr/bin/env python3
"""
Check admin user and database structure
"""
import sqlite3
from config.database import DatabaseConnection

def check_admin_user():
    """Check if admin user exists and has correct permissions"""
    db = DatabaseConnection()
    db.connect()
    
    try:
        # Check users table structure
        cursor = db.connection.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUsers table structure:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
        
        # Check admin user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print("\nAdmin user found:")
            # Convert row to dict for easier access
            admin_dict = dict(admin)
            print(f"ID: {admin_dict['id']}")
            print(f"Username: {admin_dict['username']}")
            print(f"Email: {admin_dict['email']}")
            print(f"Is Admin: {admin_dict.get('is_admin', 'Column not found')}")
            print(f"Password Hash: {admin_dict['password_hash'][:20]}..." if 'password_hash' in admin_dict else 'No password hash')
        else:
            print("\nAdmin user not found!")
            
            # Check all users
            print("\nAll users:")
            cursor.execute("SELECT id, username, email FROM users")
            for user in cursor.fetchall():
                print(f"- {user['username']} ({user['email']})")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.disconnect()

if __name__ == "__main__":
    check_admin_user()
