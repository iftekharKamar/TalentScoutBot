
import streamlit as st
import ollama
import json
import uuid
import hashlib
from datetime import datetime


def generate_questions(tech_stack_str, experience_level):
    techs = [t.strip() for t in tech_stack_str.split(",") if t.strip()]
    questions = []

    for tech in techs:
        prompt = (
            f"You are an interviewer. Generate 3 technical interview questions for a candidate with {experience_level} years of "
            f"experience skilled in {tech}. Keep them concise and clear. Number each question."
        )
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        text = response['message']['content']
        tech_questions = [line.lstrip("0123456789. ").strip() for line in text.splitlines() if line.strip()]
        questions.extend(tech_questions[:3])

    return questions



def evaluate_answers(questions, answers_dict):
    prompt = (
    "You are a strict and objective technical interviewer evaluating candidate answers.\n\n"
    "For each answer provided:\n"
    "- Carefully assess its correctness, completeness, and clarity.\n"
    "- Score the answer on a scale of 0 to 5 as follows:\n\n"
    "  • 0 = No answer, irrelevant, gibberish, or completely incorrect\n"
    "  • 1 = Very poor understanding, mostly incorrect\n"
    "  • 2 = Partially correct, missing key elements\n"
    "  • 3 = Generally correct but lacking depth or examples\n"
    "  • 4 = Mostly correct with minor gaps\n"
    "  • 5 = Completely correct, well-structured, and clearly explained\n\n"
    "Return output as JSON with keys:\n"
    "- 'evaluations': a list of objects with {question, answer, score, feedback}\n"
    "- 'average_score': the average of all scores (as float)\n\n"
    "Be strict in your grading. If an answer is empty or nonsense, assign a score of 0 and explain why.\n\n"
)

    for q in questions:
        prompt += f"Q: {q}\nA: {answers_dict.get(q, '')}\n\n"

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return json.loads(response['message']['content'])
    except:
        return {"raw": response['message']['content']}

import os

def save_result(candidate_data):
    save_dir = "candidates_data"
    os.makedirs(save_dir, exist_ok=True)

    candidate_id = str(uuid.uuid4())
    safe_name = candidate_data['name'].replace(' ', '_').lower()
    filename = f"{candidate_id}_{safe_name}.json"

    filepath = os.path.join(save_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(candidate_data, f, indent=2)

    return filepath


def chat(role, content):
    with st.chat_message(role):
        st.markdown(content)
    st.session_state.messages.append({"role": role, "content": content})

def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


st.set_page_config(page_title="TalentScoutBot", layout="centered")
st.title("🤖 TalentScoutBot – AI Interview Screener")

if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.stage = 'intro' 
    st.session_state.candidate = {}
    st.session_state.question_index = 0
    st.session_state.questions = []
    st.session_state.answers = {}


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


user_input = st.chat_input("Type your response here...")

if st.session_state.stage == 'intro':
    if 'intro_shown' not in st.session_state:
        chat("assistant", "Hello! I'm TalentScoutBot. What's your name?")
        st.session_state.intro_shown = True

    elif user_input:
        name = user_input.strip()
        st.session_state.candidate['name'] = name
        chat("user", user_input)
        chat("assistant", f"Hello **{name}**, nice to meet you! Could you share your **email address**?")
        st.session_state.stage = 'ask_email'

elif st.session_state.stage == 'ask_email':
    if user_input:
        email = user_input.strip()
        st.session_state.candidate['email'] = hash_data(email)
        chat("user", user_input)
        chat("assistant", f"Thanks! And what's your **phone number**?")
        st.session_state.stage = 'ask_phone'

elif st.session_state.stage == 'ask_phone':
    if user_input:
        phone = user_input.strip()
        st.session_state.candidate['phone'] = hash_data(phone)
        chat("user", user_input)
        chat("assistant", f"Great! What **role** are you applying for?")
        st.session_state.stage = 'ask_role'

elif st.session_state.stage == 'ask_role':
    if user_input:
        role = user_input.strip()
        st.session_state.candidate['role'] = role
        chat("user", user_input)
        chat("assistant", f"Nice! How many **years of experience** do you have?")
        st.session_state.stage = 'ask_experience'

elif st.session_state.stage == 'ask_experience':
    if user_input:
        exp = user_input.strip()
        st.session_state.candidate['experience'] = exp
        chat("user", user_input)
        chat("assistant", f"And finally, what are your main **tech skills**? (Separate by commas)")
        st.session_state.stage = 'ask_tech_stack'

elif st.session_state.stage == 'ask_tech_stack':
    if user_input:
        tech_stack = user_input.strip()
        st.session_state.candidate['tech_stack'] = tech_stack
        chat("user", user_input)
        chat("assistant", "Thanks! Generating your interview questions, please wait...")
        st.session_state.questions = generate_questions(tech_stack, st.session_state.candidate['experience'])
        st.session_state.stage = 'ask_questions'
        st.rerun()

elif st.session_state.stage == 'ask_questions':
    idx = st.session_state.question_index
    questions = st.session_state.questions

    if idx < len(questions):
        current_question = questions[idx]

        if not any(current_question in m["content"] for m in st.session_state.messages if m["role"] == "assistant"):
            chat("assistant", f"{current_question}")

        if user_input:
            st.session_state.answers[current_question] = user_input.strip()
            chat("user", user_input)
            st.session_state.question_index += 1
            if st.session_state.question_index < len(questions):
                st.rerun()
            else:
                chat("assistant", "Thanks for answering all questions! Evaluating your responses...")
                st.session_state.stage = 'evaluate'
                st.rerun()

elif st.session_state.stage == 'evaluate':
    eval_result = evaluate_answers(st.session_state.questions, st.session_state.answers)

    st.session_state.candidate['answers'] = st.session_state.answers
    st.session_state.candidate['questions'] = st.session_state.questions
    st.session_state.candidate['evaluation'] = eval_result

    save_result(st.session_state.candidate)
    chat("assistant", " Thank you! If everything looks good, our HR team will reach out to you within 24 hours.")
    st.session_state.stage = 'done'

elif st.session_state.stage == 'done':
    st.markdown("---")
    st.success("Interview session complete. You may now close this tab.")
