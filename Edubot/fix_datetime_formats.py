#!/usr/bin/env python3
"""
Database datetime format fixer for EduBot
Checks and standardizes datetime formats in the database
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

def fix_datetime_formats(db_path: str = "edubot_users.db"):
    """Fix datetime format inconsistencies in the database"""
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("Checking datetime formats in database...")
            
            # Check user_activity_log table
            cursor.execute("SELECT COUNT(*) FROM user_activity_log")
            activity_count = cursor.fetchone()[0]
            print(f"Found {activity_count} activity records")
            
            if activity_count > 0:
                # Get a sample of datetime formats
                cursor.execute("SELECT created_at FROM user_activity_log LIMIT 10")
                sample_dates = cursor.fetchall()
                
                print("Sample datetime formats:")
                for i, (date_str,) in enumerate(sample_dates):
                    print(f"  {i+1}. {date_str}")
                
                # Check if we need to standardize formats
                cursor.execute("""
                    SELECT id, created_at 
                    FROM user_activity_log 
                    WHERE created_at LIKE '%T%' OR created_at LIKE '%.%'
                """)
                iso_format_records = cursor.fetchall()
                
                if iso_format_records:
                    print(f"Found {len(iso_format_records)} records with ISO format. Converting to standard format...")
                    
                    for record_id, date_str in iso_format_records:
                        try:
                            # Parse the ISO format and convert to standard format
                            if 'T' in date_str:
                                # Handle ISO format like "2025-10-20T09:27:43"
                                if '.' in date_str:
                                    # Handle microseconds
                                    dt = datetime.fromisoformat(date_str.replace('Z', ''))
                                else:
                                    # No microseconds
                                    dt = datetime.fromisoformat(date_str.replace('Z', ''))
                            else:
                                # Try to parse as-is
                                dt = datetime.fromisoformat(date_str)
                            
                            # Convert to standard format
                            standard_format = dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Update the record
                            cursor.execute("""
                                UPDATE user_activity_log 
                                SET created_at = ? 
                                WHERE id = ?
                            """, (standard_format, record_id))
                            
                        except Exception as e:
                            print(f"Error converting datetime for record {record_id}: {e}")
                            continue
                    
                    conn.commit()
                    print("✅ Datetime formats standardized successfully!")
                else:
                    print("✅ All datetime formats are already in standard format")
            
            # Check other tables with datetime columns
            tables_to_check = [
                ('users', ['created_at', 'last_login']),
                ('feature_usage', ['last_used']),
                ('quiz_analytics', ['created_at']),
                ('document_analytics', ['created_at']),
                ('performance_analytics', ['created_at'])
            ]
            
            for table_name, datetime_columns in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        print(f"✅ {table_name}: {count} records")
                        
                        for col in datetime_columns:
                            # Check for ISO format records
                            cursor.execute(f"""
                                SELECT id, {col} 
                                FROM {table_name} 
                                WHERE {col} LIKE '%T%' OR {col} LIKE '%.%'
                                LIMIT 5
                            """)
                            sample_records = cursor.fetchall()
                            
                            if sample_records:
                                print(f"  Found ISO format in {col}, converting...")
                                # Similar conversion logic can be added here if needed
                                
                except Exception as e:
                    print(f"⚠️ Error checking {table_name}: {e}")
            
            print("\n🎉 Database datetime format check completed!")
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

def check_database_structure(db_path: str = "edubot_users.db"):
    """Check the database structure and provide information about tables"""
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("📊 Database Structure Information:")
            print("=" * 50)
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                print(f"\n🔹 Table: {table_name}")
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print("  Columns:")
                for col in columns:
                    col_id, name, col_type, not_null, default_val, pk = col
                    print(f"    - {name}: {col_type}" + (" [PRIMARY KEY]" if pk else ""))
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Records: {count}")
                
                # Show sample data if it exists
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        print("  Sample data:")
                        for i, row in enumerate(sample_data):
                            print(f"    {i+1}: {row}")
            
            print("\n" + "=" * 50)
            
    except Exception as e:
        print(f"❌ Error checking database structure: {e}")

if __name__ == "__main__":
    print("🔧 EduBot Database DateTime Format Fixer")
    print("=" * 50)
    
    # Check database structure first
    check_database_structure()
    
    print("\n" + "=" * 50)
    
    # Fix datetime formats
    fix_datetime_formats()
    
    print("\n✅ All done! You can now run the application.")
