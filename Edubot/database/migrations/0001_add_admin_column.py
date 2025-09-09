"""
Database migration to add is_admin column to users table
"""

def upgrade(db):
    """Apply the migration"""
    try:
        # Check if the column already exists
        result = db.execute_query("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='is_admin'
        """)
        
        if not result:
            # Add the is_admin column
            db.execute_query("""
            ALTER TABLE users 
            ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE
            """)
            
            # Make the first user an admin
            db.execute_query("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE id = (SELECT MIN(id) FROM users)
            """)
            
            print("✅ Added is_admin column to users table")
        else:
            print("ℹ️ is_admin column already exists")
            
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        raise

def downgrade(db):
    """Revert the migration"""
    try:
        db.execute_query("""
        ALTER TABLE users 
        DROP COLUMN IF EXISTS is_admin
        """)
        print("✅ Removed is_admin column from users table")
    except Exception as e:
        print(f"❌ Error reverting migration: {e}")
        raise
