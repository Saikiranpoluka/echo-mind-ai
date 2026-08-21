import bcrypt
import streamlit as st
import os
from openai import OpenAI
import mysql.connector
from ddgs import DDGS
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import pypdf
import uuid

# 1. Page Configuration
st.set_page_config(
    page_title="Echo Mind - Gemini Clone",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. GEMINI CLONE CUSTOM CSS
CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
        font-family: 'Google Sans', 'Inter', sans-serif;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .main .block-container {
        max-width: 900px !important;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 120px;
    }

    div[data-testid="stChatInput"] { padding-bottom: 20px; }
    div[data-testid="stChatInput"] > div {
        background-color: #1E1F20;
        border-radius: 28px;
        border: none;
        padding: 5px 10px 5px 60px; 
    }
    div[data-testid="stChatInput"] textarea {
        color: #E3E3E3;
        font-size: 16px;
    }

    div[data-testid="stPopover"] {
        position: fixed;
        bottom: 53px; 
        z-index: 10000;
        margin-left: 15px; 
    }
    div[data-testid="stPopover"] button {
        background: transparent !important;
        border: none !important;
        color: #C4C7C5 !important;
        font-size: 20px !important;
        width: 40px;
        height: 40px;
        border-radius: 50% !important;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: none !important;
    }
    div[data-testid="stPopover"] button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stChatMessage"][data-baseweb="card"] {
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        background-color: #1E1F20;
        padding: 12px 20px;
        border-radius: 24px;
        display: inline-block;
    }
    
    .login-box {
        background-color: #1E1F20;
        padding: 40px;
        border-radius: 16px;
        text-align: center;
        max-width: 400px;
        margin: 100px auto;
        border: 1px solid #333;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. CORE DATABASE CONNECTION
def get_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl_ca="ca.pem"  # Ensure this file is present in your deployment directory
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# 4. CUSTOM DATABASE AUTHENTICATION
def init_auth_db():
    """Creates the user table if it doesn't exist."""
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS echo_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

def create_user(email, password):
    """Hashes the password and saves the new user."""
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            cursor.execute(
                "INSERT INTO echo_users (email, password_hash) VALUES (%s, %s)", 
                (email, hashed_pw.decode('utf-8'))
            )
            conn.commit()
            return True
        except mysql.connector.IntegrityError:
            return False 
        finally:
            cursor.close()
            conn.close()
    return False

def authenticate_user(email, password):
    """Fetches the user and verifies the hashed password."""
    conn = get_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM echo_users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return True
    return False

# Initialize the user table when the app boots
init_auth_db()

# --- CUSTOM LOGIN / SIGNUP UI ---
if 'connected' not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    st.markdown("""
        <div class="login-box">
            <h1 style="color: #A78BFA; margin-bottom: 10px;">✨ Echo Mind</h1>
            <p style="color: #94A3B8; margin-bottom: 30px;">Sign in or create a secure account.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        # LOGIN TAB
        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, type="primary"):
                if login_email and login_password:
                    if authenticate_user(login_email, login_password):
                        st.session_state.connected = True
                        st.session_state['user_info'] = {'email': login_email, 'name': login_email.split('@')[0]}
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                else:
                    st.warning("Please enter both email and password.")
                    
        # SIGN UP TAB
        with tab_signup:
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Create Account", use_container_width=True):
                if not signup_email or not signup_password:
                    st.warning("Please fill out all fields.")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match!")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    if create_user(signup_email, signup_password):
                        st.success("✅ Account created successfully! You can now log in.")
                    else:
                        st.error("⚠️ An account with that email already exists.")
    st.stop()

# If connected, set the USER_EMAIL for the rest of the app to use
USER_EMAIL = st.session_state['user_info']['email']

# 5. SESSION & DB FUNCTIONS (THREADED CHATS)
def save_chat(role, content, session_id):
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS echo_app_chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100),
                user_email VARCHAR(255),
                role VARCHAR(20), 
                content TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO echo_app_chat_history (session_id, user_email, role, content) VALUES (%s, %s, %s, %s)", 
            (session_id, USER_EMAIL, role, content)
        )
        conn.commit()
        cursor.close()
        conn.close()

def load_specific_chat(session_id):
    conn = get_db()
    messages = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT role, content FROM echo_app_chat_history WHERE session_id = %s ORDER BY id ASC", (session_id,))
            messages = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            pass
    return messages

def get_user_chat_sessions():
    conn = get_db()
    sessions = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT session_id, content FROM echo_app_chat_history 
                WHERE id IN (
                    SELECT MIN(id) FROM echo_app_chat_history 
                    WHERE user_email = %s AND role = 'user' 
                    GROUP BY session_id
                ) ORDER BY id DESC LIMIT 15
            """, (USER_EMAIL,))
            sessions = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            pass
    return sessions

def search_long_term_memory(user_query):
    conn = get_db()
    relevant_context = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            clean_query = user_query.lower().replace('?', '').replace('.', '').replace(',', '')
            stop_words = {"what", "this", "that", "with", "have", "from", "just", "like", "how", "are", "you", "the", "and"}
            keywords = [w for w in clean_query.split() if len(w) >= 3 and w not in stop_words]
            if "name" in clean_query and "name" not in keywords: keywords.append("name")
            
            if not keywords: 
                return ""
            
            conditions = " OR ".join(["content LIKE %s" for _ in keywords])
            values = tuple([USER_EMAIL] + [f"%{kw}%" for kw in keywords])
            
            sql = f"SELECT role, content FROM echo_app_chat_history WHERE user_email = %s AND ({conditions}) ORDER BY id DESC LIMIT 5"
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            if rows:
                relevant_context.append("--- MEMORY ---")
                for row in rows: relevant_context.append(f"{row['role'].upper()}: {row['content']}")
            cursor.close()
            conn.close()
        except Exception:
            pass
    return "\n".join(relevant_context)

# 6. Universal Clients
primary_client = OpenAI(api_key=st.secrets.get("PUTER_AUTH_TOKEN", ""), base_url="https://api.puter.com/puterai/openai/v1/")
backup_client = OpenAI(api_key=st.secrets.get("BACKUP_AUTH_TOKEN", ""), base_url="https://agentrouter.org")

LANGUAGES = {
    "English": ("en-US", "en"), "Hindi": ("hi-IN", "hi"),
    "Spanish": ("es-ES", "es"), "French": ("fr-FR", "fr"),
    "German": ("de-DE", "de"), "Telugu": ("te-IN", "te"),
    "Tamil": ("ta-IN", "ta"), "Japanese": ("ja-JP", "ja")
}

# Helper Utilities
def live_web_search(query):
    try:
        # Fixed: Removed the hardcoded " current live rate today" query poisoner.
        results = DDGS().text(query, max_results=3)
        if results: return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception: pass
    return ""

def transcribe_audio(audio_bytes, lang_code="en-US"):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source: 
            return recognizer.recognize_google(recognizer.record(source), language=lang_code)
    except Exception: return None

def text_to_speech(text, lang_code='en'):
    tts = gTTS(text=text[:350] + ("..." if len(text) > 350 else ""), lang=lang_code)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def encode_image(file): return base64.b64encode(file.read()).decode('utf-8')

def extract_text_from_pdf(file):
    try:
        return "".join([page.extract_text() + "\n" for page in pypdf.PdfReader(file).pages if page.extract_text()]).strip()
    except Exception as e: return f"Error: {e}"

# Initialize State (Empty Chat on Login!)
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- SIDEBAR (CLEANER LAYOUT) ---
with st.sidebar:
    st.markdown(f"👤 `{USER_EMAIL}`")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.connected = False
        st.session_state.current_session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    st.markdown("### ⚙️ Settings")
    mode = st.radio("Mode:", ["💬 General Chat", "🌐 Live Interpreter", "🎨 Creative Studio"])
    enable_search = st.toggle("🌐 Web Browsing RAG", value=True)
    enable_audio_out = st.toggle("🔊 AI Voice Output", value=False)
    
    st.divider()
    
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("### 📜 Chat History")
    past_sessions = get_user_chat_sessions()
    
    if past_sessions:
        for session in past_sessions:
            chat_title = session['content'][:25] + "..." if len(session['content']) > 25 else session['content']
            if st.button(f"💬 {chat_title}", key=session['session_id'], use_container_width=True):
                st.session_state.current_session_id = session['session_id']
                st.session_state.messages = load_specific_chat(session['session_id'])
                st.rerun()
    else:
        st.caption("No recent chats found.")

# ---------------- MODE: GENERAL CHAT ----------------
if mode == "💬 General Chat":
    
    if not st.session_state.messages:
        st.markdown(f"<h2 style='text-align: center; color: #E3E3E3; margin-top: 100px;'>Hello, {st.session_state['user_info'].get('name', 'there')}.</h2><p style='text-align: center; color: #C4C7C5;'>How can I help you today?</p>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    with st.popover("➕", use_container_width=False):
        st.markdown("**Attachments**")
        audio_in = st.audio_input("Speak:")
        # Read straight from the widget to avoid caching UI loops
        uploaded_file = st.file_uploader("Upload Image, PDF, or Text:", type=["png", "jpg", "jpeg", "pdf", "txt"])

    prompt = st.chat_input("Ask Echo Mind anything...")
    
    if audio_in and prompt is None:
        with st.spinner("Transcribing..."):
            spoken_prompt = transcribe_audio(audio_in.read())
            if spoken_prompt: prompt = spoken_prompt

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat("user", prompt, st.session_state.current_session_id)
        with st.chat_message("user"): st.markdown(prompt)

        web_context = ""
        if enable_search:
            with st.spinner("🌐 Browsing..."):
                web_context = live_web_search(prompt)

        memory_context = search_long_term_memory(prompt)

        doc_text, is_image = "", False
        
        if uploaded_file:
            st.info(f"📎 Attached: {uploaded_file.name}")
            if uploaded_file.type.startswith("image"): is_image = True
            elif uploaded_file.name.endswith(".pdf"): doc_text = extract_text_from_pdf(uploaded_file)
            else: doc_text = uploaded_file.read().decode("utf-8", errors="ignore")

        sys_prompt = f"""You are an advanced AI named Echo Mind.
        CRITICAL INSTRUCTION: If LIVE WEB DATA is provided below, rely ONLY on it for prices, exchange rates, and news.
        
        {f'--- LIVE WEB DATA ---\n{web_context}' if web_context else ''}
        {f'--- DOC CONTENT ---\n{doc_text[:4000]}' if doc_text else ''}
        {memory_context}"""

        active_model = "google/gemini-3.5-flash"

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                if is_image:
                    uploaded_file.seek(0)
                    base64_img = encode_image(uploaded_file)
                    # Fixed: Send the image WITH the previous chat history, not overriding it.
                    history_payload = st.session_state.messages[-8:-1] if len(st.session_state.messages) > 1 else []
                    image_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{uploaded_file.type};base64,{base64_img}"}}]
                    
                    payload = {"model": active_model, "messages": [{"role": "system", "content": sys_prompt}] + history_payload + [{"role": "user", "content": image_content}]}
                else:
                    payload = {"model": active_model, "messages": [{"role": "system", "content": sys_prompt}] + st.session_state.messages[-8:]}

                try: 
                    response = primary_client.chat.completions.create(**payload)
                except Exception: 
                    response = backup_client.chat.completions.create(**payload)

                # --- Bulletproof Response Parser ---
                if hasattr(response, 'choices'):
                    reply = response.choices[0].message.content
                elif isinstance(response, dict) and 'choices' in response:
                    reply = response['choices'][0]['message']['content']
                elif isinstance(response, str):
                    reply = response # The API returned raw text (likely an error message)
                else:
                    reply = str(response)
                    
                message_placeholder.markdown(reply)

                st.session_state.messages.append({"role": "assistant", "content": reply})
                save_chat("assistant", reply, st.session_state.current_session_id)

                if enable_audio_out: st.audio(text_to_speech(reply), format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Error: {e}")

# ---------------- MODE: LIVE INTERPRETER ----------------
elif mode == "🌐 Live Interpreter":
    st.markdown("### 🌐 Live Interpreter")
    col_lang1, col_lang2 = st.columns(2)
    with col_lang1: src_lang_name = st.selectbox("I Speak:", list(LANGUAGES.keys()), index=0)
    with col_lang2: tgt_lang_name = st.selectbox("Translate To:", list(LANGUAGES.keys()), index=1)
    src_stt, src_tts = LANGUAGES[src_lang_name]
    tgt_stt, tgt_tts = LANGUAGES[tgt_lang_name]
    
    col_in, col_out = st.columns(2)
    with col_in:
        audio_val = st.audio_input(f"Record {src_lang_name}:")
        typed_text = st.text_area("Or type here:")
    
    # Fixed: Fallback logic safely checks both audio and text without crashing if one fails.
    input_text = None
    if audio_val:
        input_text = transcribe_audio(audio_val.read(), lang_code=src_stt)
    if not input_text and typed_text.strip():
        input_text = typed_text.strip()

    with col_out:
        if input_text:
            st.info(f"**Original:** {input_text}")
            with st.spinner("Translating..."):
                payload = {"model": "google/gemini-3.5-flash", "messages": [{"role": "user", "content": f"Translate to {tgt_lang_name}. Output ONLY translation: {input_text}"}]}
                try:
                    try: response = primary_client.chat.completions.create(**payload)
                    except Exception: response = backup_client.chat.completions.create(**payload)
                    
                    # --- Bulletproof Response Parser ---
                    if hasattr(response, 'choices'):
                        translated_text = response.choices[0].message.content.strip()
                    elif isinstance(response, dict) and 'choices' in response:
                        translated_text = response['choices'][0]['message']['content'].strip()
                    elif isinstance(response, str):
                        translated_text = response.strip()
                    else:
                        translated_text = str(response).strip()
                    st.success(f"**{tgt_lang_name}:**\n\n### {translated_text}")
                    st.audio(text_to_speech(translated_text, lang_code=tgt_tts), format="audio/mp3", autoplay=True)
                except Exception as e: st.error(f"Translation Error: {e}")

# ---------------- MODE: CREATIVE STUDIO ----------------
elif mode == "🎨 Creative Studio":
    st.markdown("### 🎨 Image Generation")
    img_prompt = st.text_area("Describe the image:")
    if st.button("✨ Generate") and img_prompt:
        with st.spinner("Painting..."):
            try:
                try: response = primary_client.images.generate(model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024")
                except Exception: response = backup_client.images.generate(model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024")
                st.image(response.data[0].url, caption=img_prompt, use_column_width=True)
            except Exception as e: st.error(f"Failed: {e}")
