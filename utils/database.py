import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('financial_statements.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        """
        Create necessary database tables if they don't exist
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            upload_date TIMESTAMP,
            data_json TEXT NOT NULL
        )
        ''')
        
        self.conn.commit()
    
    def store_statement_data(self, df, filename):
        """
        Store parsed statement data in the database
        """
        cursor = self.conn.cursor()
        
        # Convert DataFrame to JSON for storage
        data_json = df.to_json()
        
        # Store the data
        cursor.execute('''
        INSERT INTO statements (filename, upload_date, data_json)
        VALUES (?, ?, ?)
        ''', (filename, datetime.now(), data_json))
        
        self.conn.commit()
    
    def get_statement_data(self, filename):
        """
        Retrieve statement data from the database
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT data_json FROM statements
        WHERE filename = ?
        ORDER BY upload_date DESC
        LIMIT 1
        ''', (filename,))
        
        result = cursor.fetchone()
        
        if result:
            return pd.read_json(result[0])
        return None
    
    def __del__(self):
        self.conn.close()
