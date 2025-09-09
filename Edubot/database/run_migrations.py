#!/usr/bin/env python3
"""
Run database migrations
"""
import os
import sys
import importlib
import glob
from config.database import DatabaseConnection

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Custom print function to handle encoding
safe_print = print

def get_migrations():
    """Get all migration files in order"""
    migration_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    migration_files = sorted(glob.glob(os.path.join(migration_dir, '*.py')))
    
    # Filter out __init__.py and other non-migration files
    migration_files = [f for f in migration_files if os.path.basename(f) != '__init__.py']
    
    return migration_files

def run_migrations():
    """Run all pending migrations"""
    db = DatabaseConnection()
    
    try:
        # Create migrations table if it doesn't exist
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Get applied migrations
        result = db.execute_query("SELECT name FROM migrations") or []
        applied_migrations = {row['name'] for row in result}
        
        # Get all migration files
        migration_files = get_migrations()
        
        safe_print(f"Found {len(migration_files)} migration(s)")
        
        for migration_file in migration_files:
            migration_name = os.path.basename(migration_file)
            
            if migration_name in applied_migrations:
                safe_print(f"✓ {migration_name} (already applied)")
                continue
                
            safe_print(f"→ Applying {migration_name}...")
            
            try:
                # Import the migration module
                module_name = f"database.migrations.{os.path.splitext(migration_name)[0]}"
                migration = importlib.import_module(module_name)
                
                # Run the migration
                migration.upgrade(db)
                
                # Record the migration
                db.execute_query(
                    "INSERT INTO migrations (name) VALUES (%s)",
                    (migration_name,)
                )
                
                safe_print(f"✓ {migration_name} (applied)")
                
            except Exception as e:
                safe_print(f"✗ {migration_name} (failed)")
                safe_print(f"   Error: {str(e)}")
                raise
            
        safe_print("\n✅ All migrations applied successfully!")
        
    except Exception as e:
        safe_print("\n❌ Error applying migrations:")
        safe_print(f"   {str(e)}")
        sys.exit(1)
    finally:
        if hasattr(db, 'disconnect'):
            db.disconnect()

if __name__ == "__main__":
    run_migrations()
