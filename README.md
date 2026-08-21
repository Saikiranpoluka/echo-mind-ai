# 🧠 Echo Mind: Multimodal AI Workspace

## 📌 Overview
Echo Mind is a production-grade, multi-tenant AI workspace featuring a liquid-smooth custom UI built on Streamlit. The platform utilizes a dual-client API architecture, leveraging Google's cutting-edge **Gemini 3.6 Flash** for high-speed, long-context text processing and **Stable Diffusion 3** (via Puter) for image generation. 

Designed for security and persistence, Echo Mind features custom MySQL-backed user authentication (bcrypt) and threaded long-term memory retrieval (RAG) for personalized chat sessions.

---

## 🎯 Key Features
* **Dual-Client AI Architecture:** Routes text/vision tasks to Google Gemini and image generation tasks to Puter, optimizing API efficiency and bypassing proxy firewalls.
* **Secure Multi-Tenant Auth:** Fully functional login/signup system with hashed passwords (bcrypt) stored in a secure Aiven MySQL database.
* **Long-Term Context Memory:** Automatically saves user chat histories to the database and retrieves relevant context (RAG) for continuous, intelligent conversations.
* **Live Web Browsing:** Integrates DuckDuckGo Search (DDGS) to pull real-time data, prices, and news directly into the LLM's context window.
* **Multimodal Processing:** Native support for PDF text extraction, Image analysis (Base64 encoding), and Voice Input/Output (SpeechRecognition & gTTS) across 8 global languages.
* **Liquid UI:** A highly customized, CSS-injected Streamlit interface featuring floating inputs, hidden navigation, and responsive chat bubbles.

---

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Custom CSS)
* **AI Models:** Google Gemini 3.6 Flash, Stable Diffusion 3
* **Database:** Aiven MySQL (Secure SSL connection)
* **Security:** `bcrypt` for password hashing
* **Audio & Speech:** `SpeechRecognition`, `gTTS`
* **Data Processing:** `pypdf`, `duckduckgo-search`

---

## 📂 Project Structure
```text
echo-mind/
├── app/
│   └── app.py                     # Main Streamlit application and UI logic
├── .streamlit/
│   └── secrets.toml               # API keys and Database credentials (Git-ignored)
├── ca.pem                         # Aiven MySQL SSL Certificate
├── .gitignore
├── README.md
└── requirements.txt
🚀 Getting Started Locally
Prerequisites
Python 3.12+

An Aiven MySQL Database

API Keys from Google AI Studio and Puter

Installation
Clone the repository:

Bash
git clone [https://github.com/Saikiranpoluka/echo-mind.git](https://github.com/Saikiranpoluka/echo-mind.git)
cd echo-mind
Create and activate a virtual environment:

Bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
Install dependencies:

Bash
pip install -r requirements.txt
Configure your .streamlit/secrets.toml:

Ini, TOML
PUTER_AUTH_TOKEN = "your_puter_key_here"
GEMINI_API_KEY = "your_gemini_key_here"

[mysql]
host = "your_database_host"
port = 25138
user = "your_database_user"
password = "your_database_password"
database = "your_database_name"
Launch the application:

Bash
streamlit run app/app.py
☁️ Cloud Deployment (Streamlit Community Cloud)
When deploying to Streamlit Community Cloud, ensure the following steps are taken to bypass security constraints:

Do not push .streamlit/secrets.toml to GitHub. Add your secrets directly into the Streamlit Cloud dashboard under App Settings > Secrets.

Ensure the ca.pem file is pushed to the root of your GitHub repository so the cloud server can establish a secure SSL connection to the MySQL database.

Author: Poluka Venkata Sai Kiran Reddy

Degree: B.Tech Electronics and Communications Engineering

Focus: Full-Stack AI Engineering & Database Architectures
