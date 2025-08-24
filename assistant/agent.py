# full path: /intelligence-library-assistance/assistant/agent.py

import os
from openai import OpenAI
from typing import List, Callable
from inspect import signature

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ASSISTANT_NAME = "Intelligence Library Assistant"
ASSISTANT_INSTRUCTIONS = """
You are 'Leo', the Intelligence Library Assistant. Your personality is friendly, helpful, and proactive.
Your goal is to make the user's library experience delightful and easy.

Core Rules:
1.  **Be Proactive**: Anticipate the user's next need. If you find a book, ask if they want to check availability or get more details. After showing member details, ask if they'd like a recommendation.
2.  **Detailed Info Workflow**: When a user asks for details, a summary, or info about a book (e.g., "Tell me about 'Dune'"):
    a. First, ALWAYS use the `search_book` tool to check our local library.
    b. If the book is found in our library, state that, and then immediately use the `get_book_details` tool to provide a rich summary.
    c. If the book is NOT found in our library, directly use the `get_book_details` tool to see if you can find information about it externally.
3.  **Mood to Genre Mapping**: When a user mentions a mood (e.g., "adventurous"), map it to a book genre (Adventure, Mystery, etc.) and use the `suggest_books_by_mood` tool.
4.  **Member Details**: If the user asks "show my details", use the `get_my_details` tool.
5.  **Use Context**: The user's member ID is provided. Use it implicitly for tools like `reserve_book` and `get_my_details`. Do not ask for it again.
6.  **Stay On Topic**: If asked a non-library question, politely decline with personality, e.g., "While I love a good chat, my expertise is really in books! How about we find your next great read?"
"""

def create_assistant(tools_list: List[Callable]):
    """Creates the OpenAI Assistant with a dynamic toolset."""
    # This function dynamically builds the tool definitions from the Python functions.
    # ... (This function's code remains the same as before)
    tools_api = []
    for func in tools_list:
        sig = signature(func)
        params = sig.parameters
        properties = {}
        for name, param in params.items():
            prop_type = "string"
            if param.annotation == int: prop_type = "integer"
            properties[name] = {"type": prop_type, "description": f"The {name} for the operation."}

        tools_api.append({
            "type": "function",
            "function": {
                "name": func.__name__, "description": func.__doc__,
                "parameters": {
                    "type": "object", "properties": properties,
                    "required": [name for name, param in params.items() if param.default == param.empty]
                }
            }
        })

    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME, instructions=ASSISTANT_INSTRUCTIONS,
        model="gpt-4o", # Using the latest, fastest, and most capable model
        tools=tools_api
    )
    return assistant