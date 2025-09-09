#!/usr/bin/env python3
"""
Script to check and fix admin user password
"""
import bcrypt
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("e:/Third/Edubot/data/edubot.db")

def get_admin_user():
    """Get admin user from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    
    conn.close()
    return dict(user) if user else None

def update_password(username, new_password):
    """Update user password in database"""
    # Hash the new password
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (hashed, username)
        )
        conn.commit()
        print(f"Password updated for user: {username}")
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    print("Checking admin user...")
    admin = get_admin_user()
    
    if not admin:
        print("Admin user not found!")
        return
    
    print(f"Admin user found: {admin['username']}")
    print(f"Current password hash: {admin['password_hash']}")
    
    # Try to verify the current password
    password = "admin123"
    is_valid = bcrypt.checkpw(
        password.encode('utf-8'),
        admin['password_hash'].encode('utf-8')
    )
    
    if is_valid:
        print("[SUCCESS] Current password is valid!")
    else:
        print("[ERROR] Current password is invalid!")
        
        # Update to a known good password
        print("\nUpdating password to 'admin123'...")
        if update_password(admin['username'], password):
            print("[SUCCESS] Password updated successfully!")
            
            # Verify the new password
            admin = get_admin_user()
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                admin['password_hash'].encode('utf-8')
            )
            print(f"Verification of new password: {'[SUCCESS]' if is_valid else '[ERROR]'}")
            print(f"New password hash: {admin['password_hash']}")

if __name__ == "__main__":
    main()
