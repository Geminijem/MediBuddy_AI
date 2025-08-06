# 🔌 Libraries
import streamlit as st
import pandas as pd
import datetime
from gtts import gTTS
import os
import tempfile

# 🧠 BioBERT AI Q&A
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import requests, re
from bs4 import BeautifulSoup

# 🎤 Voice input
import speech_recognition as sr

# 🌐 Init BioBERT
model_name = "ktrapeznikov/biobert_v1.1_pubmed_squad_v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

# 🔎 Search Wikipedia
def search_wikipedia_summary(query):
    try:
        search_url = f"https://en.wikipedia.org/w/index.php?search={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        search_response = requests.get(search_url, headers=headers, timeout=20)
        soup = BeautifulSoup(search_response.text, 'html.parser')
        result_link = soup.select_one("ul.mw-search-results li a")
        article_url = "https://en.wikipedia.org" + result_link["href"] if result_link else search_response.url
        article_response = requests.get(article_url, headers=headers, timeout=20)
        soup = BeautifulSoup(article_response.text, 'html.parser')
        for para in soup.select("div.mw-parser-output > p"):
            text = para.get_text().strip()
            if len(text) > 100:
                text = re.sub(r'\[[^\]]*\]', '', text)
                return text
        return "⚠️ Couldn't extract readable Wikipedia paragraph."
    except Exception as e:
        return f"❌ Wikipedia error: {str(e)}"

# 🤖 Ask AI (BioBERT)
def get_medical_answer(question):
    try:
        context = search_wikipedia_summary(question)
        if "❌" in context or "⚠️" in context:
            return f"📚 Wikipedia says:\n{context}"
        result = qa_pipeline(question=question, context=context)
        answer = result['answer']
        if len(answer.strip()) < 5:
            raise ValueError("Too short")
        return f"🤖 AI (BioBERT): {answer.strip()}"
    except Exception:
        return f"📚 Wikipedia says:\n{search_wikipedia_summary(question)}"

# 🔊 Speak Text
def speak_text(text):
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            tts.save(tmpfile.name)
            audio_file = open(tmpfile.name, "rb")
            st.audio(audio_file.read(), format="audio/mp3")
    except Exception as e:
        st.error(f"🔊 TTS Error: {e}")

# 🎤 Record Voice Input
def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak your medical question now...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        return f"❌ Voice error: {e}"

# 🔠 Navigation
st.set_page_config(page_title="Clinical AI Assistant", layout="wide")
st.sidebar.title("🧠 Clinical AI Assistant")

menu = st.sidebar.radio("Go to", (
    "🏠 Home", "🧠 Ask AI", "📅 Study Planner", "📈 Study Charts",
    "🧠 Daily Tracker", "🗃️ Fact Vault", "📋 Flashcards", "📝 Quizzes",
    "📚 Mnemonics", "🩺 OSCE Simulations", "📆 Weekly Goals", "💡 Quotes"
))

st.title("👨‍⚕️ Clinical Assistant Dashboard")

# 🏠 HOME
if menu == "🏠 Home":
    st.header("Welcome to the Clinical AI Assistant")
    st.markdown("""
- Plan studies via Google Form  
- Track study progress  
- Log mood/focus/hours  
- Store mnemonics and facts  
- Ask BioBERT AI anything medical  
- Simulate OSCE cases  
""")

# 🧠 Ask AI
elif menu == "🧠 Ask AI":
    st.subheader("🧠 Medical Q&A Assistant (BioBERT)")
    input_method = st.radio("Choose Input Method", ["🎤 Voice", "⌨️ Text"])

    if input_method == "🎤 Voice":
        if st.button("🎙️ Record Question"):
            q = record_voice()
            st.write(f"**You asked:** {q}")
            response = get_medical_answer(q)
            st.success(response)
            speak_text(response)

    else:
        question = st.text_input("Ask a medical question")
        if st.button("Get Answer"):
            response = get_medical_answer(question)
            st.success(response)
            speak_text(response)

# 📅 Study Planner
elif menu == "📅 Study Planner":
    st.subheader("📅 Study Planner")
    st.markdown('[📝 Fill Weekly Plan](https://forms.gle/2XEtmd7iZ19Uh6hc8)')
    try:
        df = pd.read_csv("https://docs.google.com/spreadsheets/d/1L3sLBdeV9R4xCAUfVBycsU1Wq7EVZklHifN2hvp9bnA/export?format=csv")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to load planner: {e}")

# 📈 Study Charts
elif menu == "📈 Study Charts":
    st.subheader("📈 Study Progress")
    df = pd.DataFrame({
        "Date": pd.date_range("2025-08-01", periods=7),
        "Hours": [1.5, 2, 2.5, 3, 2, 3.5, 4]
    })
    st.line_chart(df.set_index("Date"))

# 🧠 Daily Tracker
elif menu == "🧠 Daily Tracker":
    st.subheader("🧠 Daily Check-in")
    with st.form("checkin_form"):
        mood = st.selectbox("Mood", ["😊", "😐", "😞"])
        focus = st.slider("Focus (1-10)", 1, 10)
        hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)
        revised = st.text_area("What did you revise?")
        save = st.form_submit_button("Save")
    if save:
        st.success("Saved!")

# 📚 Mnemonics
elif menu == "📚 Mnemonics":
    if "mnemonics_data" not in st.session_state:
        st.session_state.mnemonics_data = []

    st.subheader("📚 Add/Edit Mnemonics")
    with st.form("mnemonic_form"):
        course = st.text_input("Course")
        topic = st.text_input("Topic")
        name = st.text_input("Mnemonic Name")
        content = st.text_area("Content")
        submit = st.form_submit_button("➕ Save")
        if submit and all([course, topic, name, content]):
            st.session_state.mnemonics_data.append({
                "Course": course, "Topic": topic, "Name": name, "Content": content
            })
            st.success("Saved!")

    st.markdown("### Saved Mnemonics")
    if st.session_state.mnemonics_data:
        df = pd.DataFrame(st.session_state.mnemonics_data)
        st.dataframe(df)

        for i, row in df.iterrows():
            st.markdown(f"**{row['Name']}** - _{row['Topic']} ({row['Course']})_")
            st.markdown(f"`{row['Content']}`")
            if st.button("🗑️ Delete", key=f"del_{i}"):
                st.session_state.mnemonics_data.pop(i)
                st.experimental_rerun()

# 📋 Flashcards
elif menu == "📋 Flashcards":
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []

    st.subheader("📋 Add Flashcards")
    with st.form("flashcard_form"):
        course = st.text_input("Course")
        topic = st.text_input("Topic")
        question = st.text_area("Question")
        answer = st.text_area("Answer")
        submit = st.form_submit_button("Save")
        if submit and all([course, topic, question, answer]):
            st.session_state.flashcards.append({
                "Course": course, "Topic": topic,
                "Question": question, "Answer": answer
            })
            st.success("Saved!")

    st.markdown("### Flashcards")
    for i, card in enumerate(st.session_state.flashcards):
        st.markdown(f"**Q:** {card['Question']}")
        with st.expander("💡 View Answer"):
            st.markdown(f"{card['Answer']}")
        if st.button("🗑️ Delete", key=f"flash_del_{i}"):
            st.session_state.flashcards.pop(i)
            st.experimental_rerun()

# 📝 Quizzes
elif menu == "📝 Quizzes":
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []

    st.subheader("📝 Create Quiz")
    with st.form("quiz_form"):
        q = st.text_input("Question")
        a = st.text_input("A")
        b = st.text_input("B")
        c = st.text_input("C")
        d = st.text_input("D")
        correct = st.selectbox("Correct", ["A", "B", "C", "D"])
        submit = st.form_submit_button("Add")
        if submit and all([q, a, b, c, d]):
            st.session_state.quiz_data.append({
                "Q": q, "A": a, "B": b, "C": c, "D": d, "Correct": correct
            })
            st.success("Question added!")

    if st.session_state.quiz_data:
        if "quiz_index" not in st.session_state:
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.answers = []

        index = st.session_state.quiz_index
        if index < len(st.session_state.quiz_data):
            current = st.session_state.quiz_data[index]
            st.markdown(f"**Q{index+1}: {current['Q']}**")
            choice = st.radio("Choose:", [f"A. {current['A']}", f"B. {current['B']}", f"C. {current['C']}", f"D. {current['D']}"])
            if st.button("Submit"):
                selected = choice[0]
                correct = current["Correct"]
                st.session_state.answers.append({
                    "Q": current["Q"], "You": selected, "Correct": correct,
                    "✅": selected == correct
                })
                if selected == correct:
                    st.session_state.score += 1
                st.session_state.quiz_index += 1
                st.experimental_rerun()
        else:
            st.success(f"Score: {st.session_state.score}/{len(st.session_state.answers)}")
            st.dataframe(pd.DataFrame(st.session_state.answers))
            if st.button("🔁 Retake"):
                del st.session_state.quiz_index
                del st.session_state.score
                del st.session_state.answers
                st.experimental_rerun()

# 🗃️ Fact Vault
elif menu == "🗃️ Fact Vault":
    if "vault" not in st.session_state:
        st.session_state.vault = []

    st.subheader("🗃️ Add Fact")
    with st.form("vault_form"):
        topic = st.text_input("Topic")
        fact = st.text_area("Fact")
        save = st.form_submit_button("Save")
        if save and topic and fact:
            st.session_state.vault.append({"Topic": topic, "Fact": fact})
            st.success("Saved!")

    if st.session_state.vault:
        st.dataframe(pd.DataFrame(st.session_state.vault))

# 🩺 OSCE Simulations
elif menu == "🩺 OSCE Simulations":
    st.subheader("🩺 OSCE Simulation")
    st.markdown("**Case:** Abdominal Pain")
    st.text_area("Type your approach")
    st.button("✅ Submit")

# 📆 Weekly Goals
elif menu == "📆 Weekly Goals":
    st.subheader("📆 Weekly Goals (manual)")
    goal = st.text_area("Enter your goal")
    if st.button("Save Goal"):
        st.success("Goal saved!")

# 💡 Motivational Quotes
elif menu == "💡 Quotes":
    st.subheader("💡 Daily Quote")
    st.info("“Success is not final, failure is not fatal: It is the courage to continue that counts.” – Winston Churchill")
