import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
import base64
from io import BytesIO

# --- Core Module Imports ---
try:
    from assistant.database import check_member_credentials, signup_member
    from assistant.tools import add_book, add_member, reserve_book, search_books
    from assistant.gemini_tools import all_gemini_tools, available_tools
except ImportError as e:
    st.error(f"🚨 Critical Import Error: Failed to import a core module. Ensure project structure is correct. Details: {e}")
    st.stop()

# --- 1. Page Configuration & Professional Styling ---
ADMIN_ID = 0
LOGIN_IMAGE_PATH = "assets/robot.jpg"
LOGO_PATH = "assets/logo.jpg"
st.set_page_config(page_title="AI Book's Assistant", page_icon=LOGO_PATH, layout="centered", initial_sidebar_state="expanded")

def load_css():
    st.markdown("""
    <style>
        @keyframes glow {
            0%, 100% { text-shadow: 0 0 5px #00aaff, 0 0 10px #00aaff; }
            50% { text-shadow: 0 0 20px #00aaff, 0 0 30px #00aaff; }
        }
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        [data-testid="stSidebar"] { background-color: #1a1a2e; }
        [data-testid="stForm"], [data-testid="stExpander"] { background-color: #2a2a4e; border: 1px solid #4a4a70; }
        .stButton>button { border: 2px solid #4a4a70; background-color: #16213e; }
        
        /* --- PERFECTED Sidebar Title, Centered Logo, & Polished Footer --- */
        .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
        .sidebar-title { font-size: 2.2em; font-weight: bold; text-align: center; animation: glow 4s ease-in-out infinite; margin-bottom: 20px; }
        .sidebar-footer { position: fixed; bottom: 15px; width: 304px; text-align: center; font-size: 0.8em; color: #888; }
        
        /* --- HIDE "Press Enter to submit" PERMANENTLY --- */
        [data-testid="stForm"] [data-testid="stHelpText"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Text-to-Speech Function (Corrected) ---
def text_to_speech_autoplay(text: str):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_bytes = mp3_fp.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg"></audio>'
        return audio_html
    except Exception as e:
        print(f"Error in TTS: {e}"); return ""

# --- 3. API Configuration & AI Model Loading ---
load_dotenv(); api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key: st.error("🚨 GOOGLE_API_KEY not found in .env file."); st.stop()
try: genai.configure(api_key=api_key)
except Exception as e: st.error(f"🚨 API Config Error: {e}"); st.stop()

@st.cache_resource
def load_model():
    system_instruction = (
        "You are an AI Book's Assistant. Your creator is a brilliant developer named Taha. When asked 'who made you' or any similar question, you must proudly say: 'I was created by Taha'. "
        "Your most important rule is to **detect the user's language and respond ONLY in that same language.** Your responses should be concise and clear for the text-to-speech engine. "
        "Your protocol is strict: "
        "1. **Persona**: Be friendly, knowledgeable, and enthusiastic. "
        "2. **Clarify First**: If a user's request is vague, ask clarifying questions in their language. "
        "3. **Catalog Research**: For SPECIFIC book/author queries, you MUST use the `search_books` tool. "
        "4. **Creative Recommendation**: For MOOD or GENRE requests, DO NOT use the search tool. Use your own knowledge. "
        "5. **Propose Actions**: After a successful search, you MUST proactively ask the user, in their language, if they want to reserve a book. "
        "6. **Execute Actions**: If they confirm, use the `reserve_book` tool."
    )
    return genai.GenerativeModel('gemini-1.5-flash-latest', tools=all_gemini_tools, system_instruction=system_instruction)

# --- 4. Session State & Theme Initialization ---
st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("member_info", None)
st.session_state.setdefault("chat_session", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("audio_to_play", None)
load_css()

# --- 5. Stylish Sidebar ---
with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(LOGO_PATH,width=300)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">AI Book\'s<br>Assistant</div>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.logged_in and st.session_state.member_info:
        st.success(f"Logged in as **{st.session_state.member_info['name']}**")
        if st.button("Clear Conversation", use_container_width=True): st.session_state.messages = []; st.rerun()
        if st.button("Logout", use_container_width=True): st.session_state.clear(); st.rerun()
        
        if st.session_state.member_info['id'] == ADMIN_ID: # Admin Panel
            st.divider(); st.subheader("Admin Panel", anchor=False)
            with st.expander("➕ Add Book"):
                 with st.form("add_book_form", clear_on_submit=True):
                    title, author = st.text_input("Title"), st.text_input("Author")
                    genre, copies = st.text_input("Genre"), st.number_input("Copies", min_value=1)
                    if st.form_submit_button("Add Book", type="primary"): st.success(add_book(title, author, genre, copies))
    else:
        st.info("Please log in or sign up to begin.")
    st.markdown("<div class='sidebar-footer'>Made with ❤️ by Taha</div>", unsafe_allow_html=True)

# --- 6. Main Application Logic ---

if not st.session_state.logged_in: # LOGIN / SIGNUP SCREEN
    st.image(LOGIN_IMAGE_PATH); st.title("Welcome to the Digital Library!")
    login_tab, signup_tab = st.tabs(["**Login**", "**Sign Up**"])
    # (Login/Signup forms remain unchanged)
    with login_tab:
        with st.form("login_form"):
            name = st.text_input("Name", placeholder="Type Your Full Name"); member_id = st.text_input("Member ID", placeholder="Type Your Member ID")
            if st.form_submit_button("Login", type="primary", use_container_width=True):
                if member_id.isdigit():
                    member_info = check_member_credentials(int(member_id), name)
                    if member_info:
                        st.session_state.logged_in = True; st.session_state.member_info = member_info
                        st.session_state.chat_session = load_model().start_chat(); st.rerun()
                    else: st.error("Login failed. Name or ID is incorrect.")
                else: st.error("Member ID must be a valid number.")
    with signup_tab:
        with st.form("signup_form"):
            name, email = st.text_input("Full Name"), st.text_input("Email Address")
            if st.form_submit_button("Sign Up", type="primary", use_container_width=True):
                if name and email:
                    response = signup_member(name, email)
                    if "Success" in response: st.success(response)
                    else: st.error(response)
                else: st.warning("Please fill in both name and email.")

else: # CHAT INTERFACE
    st.subheader(f"Chat with your Assistant", divider="rainbow")
    
    # --- Plays audio triggered by a button click ---
    if st.session_state.audio_to_play:
        st.markdown(st.session_state.audio_to_play, unsafe_allow_html=True)
        st.session_state.audio_to_play = None

    for i, msg in enumerate(st.session_state.messages): # Display history
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], list):
                for book in msg["content"]:
                    col1, col2 = st.columns([1, 3])
                    if book.get("cover_url"): col1.image(book["cover_url"])
                    with col2: st.markdown(f"**{book['title']}** by {book['author']}<br>*{book['genre']} | {book['copies']} copies left*", unsafe_allow_html=True)
                    if st.button(f"Reserve '{book['title']}'", key=f"reserve_{book['title']}"):
                        st.success(reserve_book(st.session_state.member_info['id'], book['title']))
            
            elif msg["role"] == "assistant": # Assistant messages with speak button
                col1, col2 = st.columns([0.9, 0.1])
                with col1: st.markdown(msg["content"])
                with col2:
                    if st.button("🔊", key=f"speak_{i}", help="Read this message aloud"):
                        st.session_state.audio_to_play = text_to_speech_autoplay(msg["content"])
                        st.rerun()
            else: # User messages
                st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about books, Your moods, Or Your Account..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            chat = st.session_state.chat_session
            try:
                with st.spinner("Thinking..."):
                    response = chat.send_message(st.session_state.messages[-1]['content'])
                    
                    while response.candidates[0].content.parts[0].function_call.name:
                        fc = response.candidates[0].content.parts[0].function_call; tool_func = available_tools.get(fc.name)
                        if tool_func:
                            tool_args = {key: value for key, value in fc.args.items()}
                            if fc.name in ["reserve_book"]: tool_args['member_id'] = st.session_state.member_info['id']
                            output = tool_func(**tool_args)
                            response = chat.send_message(genai.types.Part.from_function_response(name=fc.name, response={"content": output}))
                        else: st.error(f"Error: Model tried to call unknown tool: {fc.name}"); break
                
                final_content = ""
                last_part = response.candidates[0].content.parts[0]
                if hasattr(last_part, 'function_response') and last_part.function_response:
                    response_data = last_part.function_response.response
                    if response_data: final_content = response_data.get('content')
                
                if not final_content and hasattr(last_part, 'text'):
                    final_content = last_part.text
                
                st.session_state.messages.append({"role": "assistant", "content": final_content})
                st.rerun()

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": f"Hello {st.session_state.member_info['name']}! How can I help you today?"})
        st.rerun()