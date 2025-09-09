import sqlite3
import os
from typing import List, Dict, Any, Optional

class SQLiteConnection:
    """SQLite database connection manager"""
    
    def __init__(self, db_path: str = 'edubot.db'):
        """Initialize SQLite connection"""
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dictionary-like access
            return self.connection
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            
            # Convert PostgreSQL placeholders to SQLite style
            query = query.replace('%s', '?')
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries, return results
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                self.connection.commit()
                return cursor.lastrowid or True
                
        except Exception as e:
            print(f"Query execution error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

def get_database_connection():
    """Get a database connection"""
    return SQLiteConnection('data/edubot.db')

# For backward compatibility
DatabaseConnection = SQLiteConnection
