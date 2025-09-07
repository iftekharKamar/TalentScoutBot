# 🤖 TalentScoutBot – AI-Powered Interview Screener

**TalentScoutBot** is an AI-powered technical interview screener built with **Streamlit** and **Ollama's Mistral model**. It interactively collects candidate information, generates role-specific questions, evaluates candidate answers using LLMs, and stores the results for later review.

---

## Features

- Conversational chatbot interface (Streamlit chat)
- AI-generated technical questions based on:
- Tech stack
- Years of experience
- Real-time answer evaluation with:
- Scoring (0 to 5)
- Feedback for each response
- Privacy-first: phone number and email are **hashed**
- Results stored locally as JSON files (in `candidates_data/`)

---

##  How It Works

### 1. Candidate Introduction
The bot collects:
- Full name
- Email address (hashed)
- Phone number (hashed)
- Applied job role
- Years of experience
- Tech skills (comma-separated)

### 2.  Question Generation
For each tech skill, the app prompts the **Mistral model** (via Ollama) to generate 3 concise, experience-appropriate technical questions.

### 3.  Answer Collection
- The candidate answers the questions one by one through chat.
- Answers are temporarily stored in memory.

### 4.  Answer Evaluation
The app asks the LLM to strictly score and review each answer, using a rubric from 0 to 5.

### 5.  Data Storage
All candidate data (excluding unhashed contact info) is saved to a JSON file with a unique ID.

---

##  Project Structure

talentscoutbot/<br>
├── app.py # Streamlit app source code<br>
├── requirements.txt # Python dependencies<br>
├── candidates_data/ # Local folder for JSON results<br>
└── README.md # This documentation

---

## Install and start Ollama
Download from ollama.com, then run:

ollama pull mistral
ollama serve

---

## Running the App

streamlit run app.py<br>
Then open:
📍 http://localhost:8501

---

## ❗ Limitations

❌ Not deployable on Streamlit Community Cloud due to Ollama requiring local models and background server access.<br>
❌ Streamlit Cloud does not support file writing or LLM servers.<br>
✅ This app is designed for local or VPS-based deployments only.<br>

---

## 🙋‍♂️ Author

Developed by **Iftekhar Kamar**<br>
Built with ❤️ using Streamlit, Python, and Mistral via Ollama.
