#!/usr/bin/env python3
"""
Script to check admin user's is_admin flag
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("e:/Third/Edubot/data/edubot.db")

def check_admin_flag():
    """Check if admin user has is_admin flag set to true"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get admin user
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if not admin:
        print("Admin user not found!")
        return
    
    admin_dict = dict(admin)
    print(f"Admin user found: {admin_dict['username']}")
    print(f"is_admin flag: {bool(admin_dict.get('is_admin', False))}")
    print(f"All user data: {admin_dict}")
    
    # Check if we need to update the flag
    if not admin_dict.get('is_admin', False):
        print("\nUpdating is_admin flag to True...")
        try:
            cursor.execute(
                "UPDATE users SET is_admin = 1 WHERE username = 'admin'"
            )
            conn.commit()
            print("Successfully updated is_admin flag!")
        except Exception as e:
            print(f"Error updating is_admin flag: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_admin_flag()
