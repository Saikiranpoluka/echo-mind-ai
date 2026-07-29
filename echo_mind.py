import streamlit as st
from openai import OpenAI
import mysql.connector
from ddgs import DDGS
import speech_recognition as sr
from gtts import gTTS
import io
import base64
import pypdf

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
    /* 1. Exact Gemini Background & Typography */
    .stApp {
        background-color: #131314;
        color: #E3E3E3;
        font-family: 'Google Sans', 'Inter', sans-serif;
    }
    header[data-testid="stHeader"] { background: transparent !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 2. Center the Chat Area like Gemini (Max 900px wide) */
    .main .block-container {
        max-width: 900px !important;
        margin: 0 auto;
        padding-top: 2rem;
        padding-bottom: 120px; /* Make room for bottom bar */
    }

    /* 3. Style the Chat Input Box (The Pill Shape) */
    div[data-testid="stChatInput"] {
        padding-bottom: 20px;
    }
    div[data-testid="stChatInput"] > div {
        background-color: #1E1F20;
        border-radius: 28px;
        border: none;
        padding: 5px 10px 5px 60px; /* 60px left padding to make room for our + icon! */
    }
    div[data-testid="stChatInput"] textarea {
        color: #E3E3E3;
        font-size: 16px;
    }

    /* 4. THE MAGIC TRICK: Float the Popover '+' Icon INSIDE the chat input! */
    div[data-testid="stPopover"] {
        position: fixed;
        bottom: 53px; /* Align vertically with the chat input */
        z-index: 10000;
        margin-left: 15px; /* Push inward to sit inside the pill */
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

    /* 5. Gemini Chat Bubbles */
    div[data-testid="stChatMessage"][data-baseweb="card"] {
        background-color: transparent !important;
        border: none !important;
    }
    /* Make user messages look like Gemini (Dark grey bubble, right-aligned text) */
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        background-color: #1E1F20;
        padding: 12px 20px;
        border-radius: 24px;
        display: inline-block;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Database Functions (Unchanged)
def get_db():
    try:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=int(st.secrets["mysql"]["port"]),
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl_ca="ca.pem"
        )
    except Exception:
        return None

def save_chat(role, content):
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS echo_chat_history (id INT AUTO_INCREMENT PRIMARY KEY, role VARCHAR(20), content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("INSERT INTO echo_chat_history (role, content) VALUES (%s, %s)", (role, content))
        conn.commit()
        cursor.close()
        conn.close()

def load_chat_history():
    conn = get_db()
    messages = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT role, content FROM echo_chat_history ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            for row in reversed(rows):
                messages.append({"role": row["role"], "content": row["content"]})
            cursor.close()
            conn.close()
        except Exception:
            pass
    return messages

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
            if not keywords: return ""
            conditions = " OR ".join(["content LIKE %s" for _ in keywords])
            values = tuple([f"%{kw}%" for kw in keywords])
            sql = f"SELECT role, content FROM echo_chat_history WHERE {conditions} ORDER BY id DESC LIMIT 5"
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

# 4. Universal Puter Client
puter_client = OpenAI(
    api_key=st.secrets.get("PUTER_AUTH_TOKEN", "your_token_here"),
    base_url="https://api.puter.com/puterai/openai/v1/"
)

# INTERPRETER LANGUAGES
LANGUAGES = {
    "English": ("en-US", "en"), "Hindi": ("hi-IN", "hi"),
    "Spanish": ("es-ES", "es"), "French": ("fr-FR", "fr"),
    "German": ("de-DE", "de"), "Telugu": ("te-IN", "te"),
    "Tamil": ("ta-IN", "ta"), "Japanese": ("ja-JP", "ja")
}

# 5. Helper Utilities
def live_web_search(query):
    try:
        # Optimize the query for a search engine
        search_query = query + " current live rate today"
        
        # Use DDGS to fetch top 3 results
        results = DDGS().text(search_query, max_results=3)
        if results: 
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception as e:
        print(f"⚠️ DDGS Search Error: {e}") # This will show in your terminal if it fails!
    return ""

def transcribe_audio(audio_bytes, lang_code="en-US"):
    recognizer = sr.Recognizer()
    try:
        audio_file = sr.AudioFile(io.BytesIO(audio_bytes))
        with audio_file as source: audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data, language=lang_code)
    except Exception: return None

def text_to_speech(text, lang_code='en'):
    spoken_text = text[:350] + ("..." if len(text) > 350 else "")
    tts = gTTS(text=spoken_text, lang=lang_code)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def encode_image(file):
    return base64.b64encode(file.read()).decode('utf-8')

def extract_text_from_pdf(file):
    try:
        reader = pypdf.PdfReader(file)
        return "".join([page.extract_text() + "\n" for page in reader.pages if page.extract_text()]).strip()
    except Exception as e: return f"Error: {e}"

# Initialize Session State
if "messages" not in st.session_state: st.session_state.messages = load_chat_history()
if "uploaded_file" not in st.session_state: st.session_state.uploaded_file = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ✨ Echo Mind")
    st.caption("Gemini Clone Architecture")
    st.divider()
    mode = st.radio("Mode:", ["💬 General Chat", "🌐 Live Interpreter", "🎨 Creative Studio"])
    enable_search = st.toggle("🌐 Web Browsing RAG", value=True)
    enable_audio_out = st.toggle("🔊 AI Voice Output", value=False)
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ---------------- MODE: GENERAL CHAT (GEMINI CLONE) ----------------
if mode == "💬 General Chat":
    
    # Display Chat History
    if not st.session_state.messages:
        st.markdown("<h2 style='text-align: center; color: #E3E3E3; margin-top: 100px;'>Hello, I'm Echo Mind.</h2><p style='text-align: center; color: #C4C7C5;'>How can I help you today?</p>", unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ➕ THE POPUVER BUTTON (Styled via CSS to hover over the chat input!)
    with st.popover("➕", use_container_width=False):
        st.markdown("**Attachments**")
        audio_in = st.audio_input("Speak:")
        uploaded_file = st.file_uploader("Upload Image, PDF, or Text:", type=["png", "jpg", "jpeg", "pdf", "txt"])
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file

    # The actual Chat Input
    prompt = st.chat_input("Ask Echo Mind anything...")
    
    # Handle Audio Input Auto-submit
    if audio_in and prompt is None:
        with st.spinner("Transcribing..."):
            audio_bytes = audio_in.read()
            spoken_prompt = transcribe_audio(audio_bytes)
            if spoken_prompt:
                prompt = spoken_prompt

    if st.session_state.uploaded_file and not prompt:
        prompt = f"Please analyze the attached file ({st.session_state.uploaded_file.name})."

    # Core Execution
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_chat("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        web_context = ""
        if enable_search:
            with st.spinner("🌐 Browsing the live web..."):
                web_context = live_web_search(prompt)
                if not web_context:
                    st.caption("⚠️ *Web search failed or found no data. Using AI memory.*")

        memory_context = search_long_term_memory(prompt)

        doc_text = ""
        is_image = False
        active_file = st.session_state.uploaded_file
        
        if active_file:
            st.info(f"📎 Attached: {active_file.name}")
            if active_file.type.startswith("image"): is_image = True
            elif active_file.name.endswith(".pdf"): doc_text = extract_text_from_pdf(active_file)
            else: doc_text = active_file.read().decode("utf-8", errors="ignore")

        sys_prompt = f"""You are an advanced AI named Echo Mind. Be concise, intelligent, and helpful. 
        
        CRITICAL INSTRUCTION: If LIVE WEB DATA is provided below, you MUST use it to answer the user's question. For prices, exchange rates, and news, rely ONLY on the LIVE WEB DATA and state that it is based on current web results.
        
        {f'--- LIVE WEB DATA ---\n{web_context}' if web_context else ''}
        {f'--- DOC CONTENT ---\n{doc_text[:4000]}' if doc_text else ''}
        {memory_context}"""

        # OPTIMIZED ROUTING (100% Gemini 3.5 Flash for max speed & cheap token usage)
        active_model = "google/gemini-3.5-flash"

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                if is_image:
                    active_file.seek(0)
                    base64_img = encode_image(active_file)
                    response = puter_client.chat.completions.create(
                        model=active_model, 
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "user", "content": [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{active_file.type};base64,{base64_img}"}}]}
                        ]
                    )
                else:
                    llm_messages = [{"role": "system", "content": sys_prompt}] + st.session_state.messages[-8:]
                    response = puter_client.chat.completions.create(model=active_model, messages=llm_messages)

                reply = response.choices[0].message.content
                message_placeholder.markdown(reply)

                st.session_state.messages.append({"role": "assistant", "content": reply})
                save_chat("assistant", reply)
                st.session_state.uploaded_file = None # Clear after success

                if enable_audio_out:
                    audio_fp = text_to_speech(reply)
                    st.audio(audio_fp, format="audio/mp3", autoplay=True)

            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.uploaded_file = None

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

    input_text = None
    if audio_val:
        with st.spinner("Listening..."):
            input_text = transcribe_audio(audio_val.read(), lang_code=src_stt)
    elif typed_text.strip(): input_text = typed_text.strip()

    with col_out:
        if input_text:
            st.info(f"**Original:** {input_text}")
            with st.spinner("Translating..."):
                response = puter_client.chat.completions.create(
                    model="google/gemini-3.5-flash",
                    messages=[{"role": "user", "content": f"Translate to {tgt_lang_name}. Output ONLY the translation: {input_text}"}]
                )
                translated_text = response.choices[0].message.content.strip()
                st.success(f"**{tgt_lang_name}:**\n\n### {translated_text}")
                audio_fp = text_to_speech(translated_text, lang_code=tgt_tts)
                st.audio(audio_fp, format="audio/mp3", autoplay=True)

# ---------------- MODE: CREATIVE STUDIO ----------------
elif mode == "🎨 Creative Studio":
    st.markdown("### 🎨 Image Generation")
    img_prompt = st.text_area("Describe the image:")
    if st.button("✨ Generate"):
        if img_prompt:
            with st.spinner("Painting..."):
                try:
                    response = puter_client.images.generate(model="dall-e-3", prompt=img_prompt, n=1, size="1024x1024")
                    st.image(response.data[0].url, caption=img_prompt, use_column_width=True)
                except Exception as e: st.error(f"Failed: {e}")