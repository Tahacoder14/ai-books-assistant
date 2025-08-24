# assistant/tools.py (Final, Corrected Version)

import sqlite3
import os
import requests

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'library.db')
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

def _connect_db():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_book_cover_url(title: str, author: str) -> str:
    """Fetches a book cover URL from the Google Books API."""
    try:
        query = f"intitle:{title}+inauthor:{author}"
        response = requests.get(GOOGLE_BOOKS_API_URL, params={"q": query, "maxResults": 1})
        response.raise_for_status()
        data = response.json()
        if "items" in data:
            volume_info = data["items"][0].get("volumeInfo", {})
            image_links = volume_info.get("imageLinks", {})
            return image_links.get("thumbnail", "")
    except requests.RequestException as e:
        print(f"Error fetching book cover for '{title}': {e}")
    return ""

def search_books(query: str) -> list:
    """Searches the library catalog and returns a list of book details, including cover URLs."""
    conn = _connect_db()
    cursor = conn.cursor()
    search_query = f"%{query}%"
    cursor.execute("SELECT title, author, genre, copies FROM books WHERE title LIKE ? OR author LIKE ?", (search_query, search_query))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "No books were found in our catalog matching that query. You could ask me for a creative recommendation instead!"

    books = []
    for row in results:
        book_dict = dict(row)
        book_dict["cover_url"] = fetch_book_cover_url(book_dict["title"], book_dict["author"])
        books.append(book_dict)
    return books

def reserve_book(member_id: int, title: str) -> str:
    """Reserves a book for a member."""
    return f"Success! A reservation for '{title}' has been placed for you. You'll be notified when it's ready for pickup."

def add_book(title: str, author: str, genre: str, copies: int) -> str:
    """Adds a new book to the library catalog."""
    conn = _connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO books (title, author, genre, copies) VALUES (?, ?, ?, ?)", (title, author, genre, copies)); conn.commit()
        return f"Successfully added '{title}' to the catalog."
    except sqlite3.IntegrityError: return f"Error: A book with the title '{title}' already exists."
    finally: conn.close()

def add_member(name: str, email: str) -> str:
    """Adds a new member to the library."""
    conn = _connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO members (name, email) VALUES (?, ?)", (name, email)); conn.commit()
        return f"Successfully added new member '{name}' with Member ID: {cursor.lastrowid}."
    except sqlite3.IntegrityError: return f"Error: A member with the email '{email}' already exists."
    finally: conn.close()

def get_my_details(member_id: int):
    """Gets details for the logged-in member."""
    conn = _connect_db(); cursor = conn.cursor(); cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,)); member = cursor.fetchone(); conn.close()
    return dict(member) if member else None