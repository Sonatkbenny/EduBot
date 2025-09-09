import os
import sys
import sqlite3
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()

def safe_print(*args, **kwargs):
    """Print function that handles encoding issues"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback to ASCII-only output if encoding fails
        print(*[str(arg).encode('ascii', 'replace').decode('ascii') for arg in args], **kwargs)

class DatabaseConnection:
    """Database connection manager that supports both PostgreSQL and SQLite"""
    
    def __init__(self):
        self.connection = None
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///data/edubot.db')
        self.is_sqlite = self.database_url.startswith('sqlite:')
    
    def connect(self):
        """Establish database connection"""
        try:
            if self.is_sqlite:
                # Extract the path from sqlite:///path/to/db.db
                db_path = self.database_url.split('sqlite:///')[-1]
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                self.connection = sqlite3.connect(db_path)
                self.connection.row_factory = sqlite3.Row  # Enable dictionary-like access
            else:
                # PostgreSQL connection
                import psycopg2
                from psycopg2.extras import RealDictCursor
                self.connection = psycopg2.connect(
                    self.database_url,
                    cursor_factory=RealDictCursor
                )
            return self.connection
        except Exception as e:
            safe_print(f"Database connection error: {e}")
            return None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> Union[List[Dict[str, Any]], bool, int]:
        """Execute a query and return results"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Convert PostgreSQL placeholders to SQLite style if needed
            if self.is_sqlite:
                query = query.replace('%s', '?')
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                if self.is_sqlite:
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
                else:
                    return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.lastrowid or True
                
        except Exception as e:
            safe_print(f"Query execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """Alias for disconnect for compatibility"""
        self.disconnect()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

def create_tables():
    """Create necessary database tables"""
    db = DatabaseConnection()
    
    try:
        # Users table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)
        
        # Documents table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            content TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """)
        
        # Quizzes table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            questions TEXT NOT NULL,  -- JSON string of questions
            score INTEGER,
            max_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """)
        
        # User profiles table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            education_level VARCHAR(50),
            interests TEXT,  -- JSON array of interests
            weak_topics TEXT,  -- JSON array of weak topics
            preferences TEXT,  -- JSON object of user preferences
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """)
        
        # Create migrations table if it doesn't exist
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Performance table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject VARCHAR(100) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            score DECIMAL(5,2),
            total_marks DECIMAL(5,2),
            classification VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """)
        
        # Recommendations table
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic VARCHAR(255) NOT NULL,
            resource_type VARCHAR(50),
            resource_url TEXT,
            title VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        """)
        
        safe_print("✅ Database tables created successfully!")
        
        # Create an admin user if none exists
        result = db.execute_query("SELECT id FROM users WHERE is_admin = 1 LIMIT 1")
        if not result:
            from utils.auth import get_auth_manager
            auth_manager = get_auth_manager()
            password_hash = auth_manager.hash_password("admin123")
            db.execute_query(
                """
                INSERT INTO users (username, email, password_hash, full_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("admin", "admin@edubot.com", password_hash, "Administrator", 1)
            )
            safe_print("✅ Created default admin user (username: admin, password: admin123)")
        
    except Exception as e:
        safe_print(f"❌ Error creating database tables: {e}")
        raise
    finally:
        db.disconnect()

# Initialize database tables
if __name__ == "__main__":
    create_tables()
