import sqlite3

DATABASE_FILE = 'library.db'

def inspect_members():
    """Connects to the database and prints all members."""
    print("--- Inspecting Members in library.db ---")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        
        if not members:
            print("The 'members' table is empty!")
            print("Please run 'python setup_database.py' to add the default members.")
        else:
            print(f"Found {len(members)} member(s):")
            for member in members:
                # Convert the sqlite3.Row object to a dictionary for clean printing
                member_dict = dict(member)
                print(f"  - ID: {member_dict.get('member_id')}, Name: '{member_dict.get('name')}'")
        
        conn.close()
    
    except sqlite3.OperationalError as e:
        print(f"\nERROR: Could not read the 'members' table. It might not exist yet.")
        print(f"Details: {e}")
        print("ACTION: Please run 'python setup_database.py' to create and populate the database.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_members()