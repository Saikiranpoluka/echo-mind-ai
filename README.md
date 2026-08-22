# 🧠 Echo Mind — Multimodal AI Workspace

> A Python/Streamlit AI workspace that combines multimodal LLM interactions, retrieval-augmented conversation memory, document and image processing, web search, voice features, and MySQL-backed authentication.

## 📌 Overview

Echo Mind is an AI application designed to provide a persistent, multimodal chat experience rather than a single-turn chatbot.

The application combines an LLM client for text and vision tasks with an image-generation service, while storing user accounts and conversation history in MySQL. Relevant previous conversations can be retrieved to provide longer-term context.

## ✨ Key Capabilities

- **Multimodal AI:** Text and image-based interactions.
- **RAG-style conversation memory:** Stores chat history and retrieves relevant previous context for ongoing conversations.
- **Document processing:** Extracts text from PDF files for AI-assisted interactions.
- **Web retrieval:** Uses DuckDuckGo search to bring external information into the application workflow.
- **Voice features:** Speech recognition and text-to-speech support.
- **Image generation:** Integrates an external image-generation service through Puter.
- **User authentication:** MySQL-backed accounts with password hashing using `bcrypt`.
- **Streamlit UI:** Custom chat interface with responsive styling and application controls.

## 🏗️ High-Level Architecture

```text
                    ┌──────────────────────┐
                    │     Streamlit UI     │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
             Text/Image     PDF/Voice     Web Search
                 │             │             │
                 └─────────────┼─────────────┘
                               ▼
                     ┌──────────────────┐
                     │   AI Orchestration│
                     └────────┬─────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          Gemini API     Image Service      Retrieval
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                       ┌─────────────┐
                       │   MySQL DB  │
                       │ Users + Chat│
                       └─────────────┘
```

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| Application | Python, Streamlit |
| AI | Google Gemini, external image-generation API |
| Retrieval | Conversation-history retrieval, DuckDuckGo Search |
| Database | MySQL |
| Authentication | bcrypt |
| Documents | pypdf |
| Voice | SpeechRecognition, gTTS |

## 📂 Project Structure

```text
echo-mind-ai/
├── app/
│   └── app.py
├── .streamlit/
│   └── secrets.toml.example
├── .gitignore
├── README.md
└── requirements.txt
```

> Local secrets and private certificates are intentionally excluded from version control.

## 🚀 Run Locally

### Prerequisites

- Python 3.12+
- MySQL database
- Gemini API credentials
- Puter/image-generation credentials if image generation is enabled

### 1. Clone the repository

```bash
git clone https://github.com/Saikiranpoluka/echo-mind-ai.git
cd echo-mind-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Streamlit secrets

Create `.streamlit/secrets.toml` locally. **Do not commit this file.**

Example:

```toml
GEMINI_API_KEY = "your_gemini_key"
PUTER_AUTH_TOKEN = "your_puter_key"

[mysql]
host = "your_database_host"
port = 3306
user = "your_database_user"
password = "your_database_password"
database = "your_database_name"
```

Use the actual connection details supplied by your database provider rather than copying values from this example.

### 4. Start the application

```bash
streamlit run app/app.py
```

## 🔐 Security Notes

- Never commit `.streamlit/secrets.toml`.
- Never commit API keys, database passwords, or private certificates.
- The repository ignores `.pem` files and local secret configuration.
- If a secret has ever been committed, rotate it and remove it from Git history; `.gitignore` alone does not remove previously committed secrets.

## ☁️ Deployment

The application can be deployed to Streamlit Community Cloud or another Python-compatible hosting platform.

For hosted deployments, configure secrets through the platform's secret-management interface rather than storing credentials in the repository.

If the MySQL provider requires an SSL certificate, provide the certificate through the hosting environment's supported secret/file mechanism instead of committing private infrastructure material to the repository.

## 🎯 Engineering Highlights

- Designed a multi-component AI application rather than a single LLM prompt interface.
- Combined AI inference, retrieval, persistent storage, authentication, document processing, and web retrieval in one workflow.
- Used hashed passwords rather than storing plaintext credentials.
- Separated local secrets from source control using Streamlit secrets and `.gitignore`.

## 🔮 Future Improvements

- Add automated unit and integration tests.
- Split AI, retrieval, database, and authentication logic into dedicated modules.
- Add structured logging and error monitoring.
- Introduce conversation-level retrieval evaluation and relevance metrics.
- Add API endpoints for external clients.
- Add rate limiting and stronger session/authorization controls.
- Add containerized deployment and CI checks.
- Add observability for latency, model usage, failures, and database operations.

## 👤 Author

**Poluka Venkata Sai Kiran Reddy**  
B.Tech — Electronics and Communication Engineering

**Focus:** Python Development • AI/ML Engineering • LLM Applications • Data & Backend Systems
