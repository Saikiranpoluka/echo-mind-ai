# 🤖 Echo Mind: Multi-Modal AI Operating System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b.svg)](https://streamlit.io/)
[![OpenAI SDK](https://img.shields.io/badge/OpenAI-SDK-orange.svg)](https://github.com/openai/openai-python)
[![MySQL](https://img.shields.io/badge/MySQL-Aiven-blueviolet.svg)](https://aiven.io/)

**Echo Mind** is a production-grade, multi-modal AI assistant and operating system styled with a modern, responsive Gemini-inspired interface. It bridges high-speed cloud intelligence models with robust persistent memory, multi-format document/image parsing, voice synthesis, real-time speech translation, and web RAG capabilities.

---

## 🛠️ Tech Stack & Tools

* **Frontend & UI/UX:** Streamlit, Custom HTML5/CSS3 (Gemini Dark Theme, Responsive Glassmorphism, Fixed Layout Bars)
* **AI & LLM Orchestration:** OpenAI Python SDK, Puter AI Proxy, Google Gemini 3.5 Flash
* **Database & Memory:** Aiven MySQL (Relational persistence, RAG long-term context search)
* **Data Retrieval (RAG):** `ddgs` (DuckDuckGo Search engine wrapper)
* **Multimedia & Utilities:** 
  * `PyPDF` (Document and PDF parsing)
  * `SpeechRecognition` & `gTTS` (Speech-to-Text and Text-to-Speech audio pipeline)
  * `base64` (Multi-modal image encoding for vision-based queries)

---

## 💡 Core Skills & Engineering Highlights

* **Full-Stack AI Development:** Combining dynamic web interfaces with asynchronous LLM endpoints.
* **Multi-Modal Integration:** Seamlessly handling text, voice audio blobs, local text files, PDFs, and image matrices within a unified interface.
* **Dual Memory Architecture:** Merging short-term session state with long-term keyword-indexed database storage for context-aware interactions.
* **Resilient Error Handling:** Graceful fallback mechanisms for web search rate limits, connection drops, and fallback data workflows.

---

## 🔄 System Architecture & Workflow

```text
 [User Input] 
    ├── (Text / Prompt) ──┐
    ├── (Voice / Audio) ──┼──> [Streamlit UI Layer] ──> [Smart Router / Gemini 3.5 Flash] ──> [AI Response]
    ├── (Images / OCR) ───┤          │                                                          │
    └── (PDF / Files) ────┘          ▼                                                          ▼
                           [Aiven MySQL Database]                                     [gTTS Audio / UI Output]
                           (Long-term RAG Memory)
Input Stage: The user interacts via text input or the custom inline + popover attachment menu (supporting audio recordings, images, PDFs, and text files).

Context Augmentation (RAG):

Web Context: Live search queries are fetched via ddgs to inject real-time data into the system prompt.

Database Context: Past messages are filtered and pulled from Aiven MySQL to maintain conversational continuity.

Inference Execution: Payloads are routed through the unified OpenAI client wrapper targeting high-speed multi-modal endpoints (Gemini 3.5 Flash).

Output Layer: Responses are rendered in real-time, saved back to permanent database storage, and optionally voiced out using text-to-speech synthesis or live-translated.

📖 User Manual & Guide
Modes Available
💬 General Chat: Standard conversational agent with full multi-modal attachment support (+ popover menu) and live web RAG.

🌐 Live Interpreter: Real-time speech-to-speech and text translation tool supporting multiple global languages (Hindi, Spanish, French, Japanese, Telugu, Tamil, Arabic, etc.).

🎨 Creative Studio: Generative media interface utilizing standard image endpoints.

👨‍🏫 Tutor Mode / 💻 Coding Agent: Specialized system personas designed for Socratic teaching and clean software engineering architectures.

🎙️ Voice Mode: Dedicated speech assessment environment with visual listening states.

🚀 Getting Started Locally
1. Clone the Repository
Bash
git clone [https://github.com/YOUR_USERNAME/echo-mind-ai.git](https://github.com/YOUR_USERNAME/echo-mind-ai.git)
cd echo-mind-ai
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configure Secrets
Create a .streamlit/secrets.toml file in your root directory with your credentials:

Ini, TOML
PUTER_AUTH_TOKEN = "your_puter_auth_token_here"

[mysql]
host = "your_mysql_host_here"
port = 3306
user = "your_mysql_user"
password = "your_mysql_password"
database = "your_database_name"
(Note: Ensure your Aiven MySQL SSL certificate (ca.pem) is placed in the root directory if required by your database tier).

4. Run the Application
Bash
streamlit run echo_mind.py
