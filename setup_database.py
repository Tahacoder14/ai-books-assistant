# setup_database.py (Final "Taha" Version)

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'library.db')

def setup_database():
    """Creates the database tables and populates them with initial data."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed existing database for a clean setup.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create members table
    cursor.execute('''
    CREATE TABLE members (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    print("Created 'members' table.")

    # Insert Admin with specific ID 0, and "Taha" as the sample user with ID 1
    cursor.execute("INSERT INTO members (id, name, email) VALUES (0, 'Admin', 'admin@library.com')")
    cursor.execute("INSERT INTO members (id, name, email) VALUES (1, 'Taha', 'taha@example.com')")
    print("Inserted Admin (ID 0) and sample user Taha (ID 1).")
    
    # Create books table
    cursor.execute('''
    CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        author TEXT NOT NULL,
        genre TEXT,
        copies INTEGER NOT NULL DEFAULT 1
    )''')
    print("Created 'books' table.")
    
    # Add sample books for searching
    books_to_add = [
        ('The Three-Body Problem', 'Cixin Liu', 'Science Fiction', 5),
        ('Astrophysics for People in a Hurry', 'Neil deGrasse Tyson', 'Physics', 3),
        ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'History', 4),
        ('Project Hail Mary', 'Andy Weir', 'Science Fiction', 6),
        ('A Brief History of Time', 'Stephen Hawking', 'Physics', 2),
        ('The God Equation', 'Michio Kaku', 'Physics', 3)
    ]
    cursor.executemany("INSERT INTO books (title, author, genre, copies) VALUES (?, ?, ?, ?)", books_to_add)
    print("Populated 'books' table.")
    
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup_database()
    print("\n--- LOGIN CREDENTIALS ---")
    print("Admin Login -> Name: Admin, ID: 0")
    print("User Login  -> Name: Taha,  ID: 1")