#!/usr/bin/env python3
"""
Verify that all dates in the database are not in the future
"""

import sqlite3
from datetime import datetime

def verify_dates(db_path: str = "edubot_users.db"):
    """Check for any future dates in the database"""
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"🔍 Checking for future dates (after {current_date})")
            print("=" * 60)
            
            # Check each table for future dates
            checks = [
                ("user_activity_log", "created_at"),
                ("users", "created_at"),
                ("users", "last_login"),
                ("feature_usage", "last_used"),
                ("quiz_analytics", "created_at"),
                ("document_analytics", "created_at"),
                ("performance_analytics", "created_at")
            ]
            
            total_future_dates = 0
            
            for table, column in checks:
                try:
                    # Count future dates
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table} 
                        WHERE {column} > datetime('now')
                    """)
                    future_count = cursor.fetchone()[0]
                    
                    # Get total count
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} IS NOT NULL")
                    total_count = cursor.fetchone()[0]
                    
                    status = "✅" if future_count == 0 else "❌"
                    print(f"{status} {table}.{column}: {future_count}/{total_count} future dates")
                    
                    if future_count > 0:
                        total_future_dates += future_count
                        # Show sample future dates
                        cursor.execute(f"""
                            SELECT {column} FROM {table} 
                            WHERE {column} > datetime('now')
                            LIMIT 3
                        """)
                        samples = cursor.fetchall()
                        print(f"   Sample future dates: {samples}")
                        
                except Exception as e:
                    print(f"⚠️  Error checking {table}.{column}: {e}")
            
            print("=" * 60)
            if total_future_dates == 0:
                print("🎉 SUCCESS: No future dates found in database!")
            else:
                print(f"⚠️  FOUND {total_future_dates} future dates that need fixing")
                
            # Check date range of login activity for charts
            print("\n📊 Login Activity Date Range:")
            cursor.execute("""
                SELECT 
                    MIN(date(last_login)) as earliest,
                    MAX(date(last_login)) as latest,
                    COUNT(DISTINCT date(last_login)) as unique_days
                FROM users 
                WHERE last_login IS NOT NULL
                AND last_login <= datetime('now')
            """)
            result = cursor.fetchone()
            if result[0]:
                print(f"   Date range: {result[0]} to {result[1]} ({result[2]} unique days)")
            else:
                print("   No login activity data")
                
            # Check date range of user activity
            print("\n📊 User Activity Date Range:")
            cursor.execute("""
                SELECT 
                    MIN(date(created_at)) as earliest,
                    MAX(date(created_at)) as latest,
                    COUNT(DISTINCT date(created_at)) as unique_days
                FROM user_activity_log 
                WHERE created_at <= datetime('now')
            """)
            result = cursor.fetchone()
            if result[0]:
                print(f"   Date range: {result[0]} to {result[1]} ({result[2]} unique days)")
            else:
                print("   No activity data")
                
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    print("🔍 EduBot Date Verification Tool")
    verify_dates()
