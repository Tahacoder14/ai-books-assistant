# assistant/gemini_tools.py

import google.generativeai as genai
from . import tools

# --- NEW: Function Declaration for the Book Search Tool ---
search_books_func = genai.types.FunctionDeclaration(
    name="search_books",
    description="Searches the library catalog for books by title or author to find details and availability.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {"type": "STRING", "description": "The title or author of the book to search for"},
        },
        "required": ["query"],
    },
)

# --- Existing Function Declarations ---
add_book_func = genai.types.FunctionDeclaration(
    name="add_book",
    description="Adds a new book to the library catalog. Only for admin use.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING", "description": "The title of the book"},
            "author": {"type": "STRING", "description": "The author of the book"},
            "genre": {"type": "STRING", "description": "The genre of the book"},
            "copies": {"type": "INTEGER", "description": "The number of copies to add"},
        },
        "required": ["title", "author", "genre", "copies"],
    },
)

get_my_details_func = genai.types.FunctionDeclaration(
    name="get_my_details",
    description="Retrieves the library member details for the currently logged-in user.",
    parameters={"type": "OBJECT", "properties": {}},
)

reserve_book_func = genai.types.FunctionDeclaration(
    name="reserve_book",
    description="Reserves a specific book for the currently logged-in user after they have been shown the details.",
    parameters={
        "type": "OBJECT",
        "properties": {
             "title": {"type": "STRING", "description": "The exact title of the book to reserve"},
        },
        "required": ["title"],
    },
)

# You would also add a declaration for 'add_member' if you want the AI to use it, but for now we'll keep it manual for the admin.

# --- Updated Tool Lists ---
all_gemini_tools = [
    search_books_func,  # Add the new tool here
    add_book_func,
    get_my_details_func,
    reserve_book_func
]

available_tools = {
    "search_books": tools.search_books, # And here
    "add_book": tools.add_book,
    "get_my_details": tools.get_my_details,
    "reserve_book": tools.reserve_book,
    "add_member": tools.add_member,
}