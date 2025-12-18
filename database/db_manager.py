import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_NAME = "database/complaints.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE,
            customer_name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            address TEXT,
            complaint_text TEXT,
            category TEXT,
            priority TEXT,
            department TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Admin table for simple authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # Default admin
    cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

def add_complaint(tracking_id, name, email, phone, city, address, text, category, priority, department):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO complaints (tracking_id, customer_name, email, phone, city, address, complaint_text, category, priority, department)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tracking_id, name, email, phone, city, address, text, category, priority, department))
    conn.commit()
    conn.close()

def get_all_complaints():
    conn = sqlite3.connect(DATABASE_NAME)
    df = pd.read_sql_query("SELECT * FROM complaints ORDER BY created_at DESC", conn)
    conn.close()
    return df

def update_complaint_status(tracking_id, status):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE tracking_id = ?", (status, tracking_id))
    conn.commit()
    conn.close()

def delete_complaint(tracking_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE tracking_id = ?", (tracking_id,))
    conn.commit()
    conn.close()

def authenticate_admin(username, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
