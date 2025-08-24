# assistant/database.py (Final Bug-Fix Version)
# (No changes from the previous version, but included for completeness)
import sqlite3, os
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'library.db')
def _connect_db():
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row; return conn
def check_member_credentials(member_id: int, name: str):
    conn = _connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ? AND lower(name) = ?", (member_id, name.lower().strip()))
    member = cursor.fetchone()
    conn.close()
    return dict(member) if member else None
def signup_member(name: str, email: str) -> str:
    conn = _connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return f"Success! You are now a member. Your new Member ID is {cursor.lastrowid}. Please use it to log in."
    except sqlite3.IntegrityError: return "Error: A member with this email already exists."
    finally: conn.close()
def find_member_by_id(member_id: int):
    conn = _connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
    member = cursor.fetchone()
    conn.close()
    return dict(member) if member else None