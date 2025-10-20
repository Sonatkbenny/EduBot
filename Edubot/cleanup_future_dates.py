#!/usr/bin/env python3
"""
Clean up any future dates in the database
"""

import sqlite3
from datetime import datetime, timedelta
import random

def cleanup_future_dates(db_path: str = "edubot_users.db"):
    """Fix any future dates in the database"""
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            current_datetime = datetime.now()
            
            print(f"🔧 Cleaning up future dates (after {current_datetime})")
            print("=" * 60)
            
            # Tables and columns to fix
            fixes = [
                ("user_activity_log", "created_at"),
                ("users", "last_login"),
                ("feature_usage", "last_used"),
                ("quiz_analytics", "created_at"),
                ("document_analytics", "created_at"),
                ("performance_analytics", "created_at")
            ]
            
            total_fixed = 0
            
            for table, column in fixes:
                try:
                    # Find future dates
                    cursor.execute(f"""
                        SELECT id, {column} FROM {table} 
                        WHERE {column} > datetime('now')
                    """)
                    future_records = cursor.fetchall()
                    
                    if future_records:
                        print(f"🔧 Fixing {len(future_records)} future dates in {table}.{column}")
                        
                        for record_id, future_date in future_records:
                            # Generate a random past date within the last 30 days
                            days_ago = random.randint(1, 30)
                            hours_ago = random.randint(0, 23)
                            minutes_ago = random.randint(0, 59)
                            
                            corrected_date = current_datetime - timedelta(
                                days=days_ago, 
                                hours=hours_ago, 
                                minutes=minutes_ago
                            )
                            
                            # Update with standard format
                            corrected_date_str = corrected_date.strftime('%Y-%m-%d %H:%M:%S')
                            
                            cursor.execute(f"""
                                UPDATE {table} 
                                SET {column} = ? 
                                WHERE id = ?
                            """, (corrected_date_str, record_id))
                            
                            total_fixed += 1
                        
                        print(f"   ✅ Fixed {len(future_records)} records")
                    else:
                        print(f"   ✅ {table}.{column}: No future dates found")
                        
                except Exception as e:
                    print(f"   ❌ Error fixing {table}.{column}: {e}")
            
            if total_fixed > 0:
                conn.commit()
                print("=" * 60)
                print(f"🎉 Successfully fixed {total_fixed} future dates!")
            else:
                print("=" * 60)
                print("✅ No future dates found to fix!")
                
        # Verify the fix
        print("\n🔍 Verifying cleanup...")
        verify_cleanup(db_path)
        
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def verify_cleanup(db_path: str = "edubot_users.db"):
    """Verify that cleanup was successful"""
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check each table for remaining future dates
            checks = [
                ("user_activity_log", "created_at"),
                ("users", "last_login"),
                ("feature_usage", "last_used"),
                ("quiz_analytics", "created_at"),
                ("document_analytics", "created_at"),
                ("performance_analytics", "created_at")
            ]
            
            total_remaining = 0
            
            for table, column in checks:
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table} 
                        WHERE {column} > datetime('now')
                    """)
                    future_count = cursor.fetchone()[0]
                    total_remaining += future_count
                    
                    if future_count == 0:
                        print(f"✅ {table}.{column}: Clean")
                    else:
                        print(f"❌ {table}.{column}: Still has {future_count} future dates")
                        
                except Exception as e:
                    print(f"⚠️  Error checking {table}.{column}: {e}")
            
            if total_remaining == 0:
                print("\n🎉 SUCCESS: All future dates have been cleaned up!")
            else:
                print(f"\n⚠️  {total_remaining} future dates still remain")
                
    except Exception as e:
        print(f"❌ Error verifying cleanup: {e}")

if __name__ == "__main__":
    print("🔧 EduBot Future Date Cleanup Tool")
    cleanup_future_dates()
