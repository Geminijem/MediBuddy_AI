import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from transformers import pipeline
import random

# Simulated models for AI (Hugging Face-style)
@st.cache_resource
def load_medical_model():
    return pipeline("text-generation", model="distilgpt2")

medical_ai = load_medical_model()

# App State
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

if "quizzes" not in st.session_state:
    st.session_state.quizzes = []

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "checkins" not in st.session_state:
    st.session_state.checkins = []

if "reminders" not in st.session_state:
    st.session_state.reminders = []

# Sidebar Menu
menu = st.sidebar.radio("📌 Menu", [
    "🏠 Home",
    "🧠 Medical AI",
    "📋 Flashcards",
    "📝 Quiz Section",
    "💡 Daily Quote",
    "📚 Notes Vault",
    "🗓️ Study Planner",
    "🤖 Backup AI",
    "📊 Study Chart",
    "📆 Daily Check-In",
    "📤 Export Progress"
])

# Pages
if menu == "🏠 Home":
    st.title("🏥 Clinical AI Assistant")
    st.markdown("Welcome! Choose an option from the sidebar.")

elif menu == "🧠 Medical AI":
    st.header("Ask a Medical Question")
    query = st.text_input("Type your question here:")
    if st.button("Ask AI"):
        if query:
            response = medical_ai(query, max_length=50)[0]['generated_text']
            st.success(response)

elif menu == "📋 Flashcards":
    st.header("🧠 Flashcards")
    course = st.text_input("Course")
    topic = st.text_input("Topic")
    name = st.text_input("Mnemonic Name")
    content = st.text_area("Mnemonic Content")
    if st.button("Save Flashcard"):
        st.session_state.flashcards.append({"course": course, "topic": topic, "name": name, "content": content})
        st.success("Saved!")

    st.subheader("Saved Flashcards")
    for i, card in enumerate(st.session_state.flashcards):
        st.markdown(f"**{card['name']}** — *{card['topic']}*")
        st.write(card['content'])
        if st.button(f"Edit {i}"):
            st.session_state.flashcards[i] = {
                "course": st.text_input("Course", value=card['course'], key=f"ec{i}"),
                "topic": st.text_input("Topic", value=card['topic'], key=f"et{i}"),
                "name": st.text_input("Name", value=card['name'], key=f"en{i}"),
                "content": st.text_area("Content", value=card['content'], key=f"ed{i}")
            }
        if st.button(f"Delete {i}"):
            st.session_state.flashcards.pop(i)
            st.experimental_rerun()

elif menu == "📝 Quiz Section":
    st.header("📋 Quizzes")
    question = st.text_input("Question")
    answer = st.text_input("Answer")
    if st.button("Save Quiz"):
        st.session_state.quizzes.append({"q": question, "a": answer})
        st.success("Quiz Saved!")

    st.subheader("Saved Quizzes")
    for i, q in enumerate(st.session_state.quizzes):
        st.markdown(f"**Q:** {q['q']}")
        st.markdown(f"**A:** {q['a']}")
        if st.button(f"Edit Quiz {i}"):
            st.session_state.quizzes[i] = {
                "q": st.text_input("Q", value=q['q'], key=f"qq{i}"),
                "a": st.text_input("A", value=q['a'], key=f"qa{i}")
            }
        if st.button(f"Delete Quiz {i}"):
            st.session_state.quizzes.pop(i)
            st.experimental_rerun()

elif menu == "💡 Daily Quote":
    st.header("💡 Daily Medical Quote")
    quotes = [
        "“Wherever the art of Medicine is loved, there is also a love of Humanity.” – Hippocrates",
        "“Medicine is a science of uncertainty and an art of probability.” – William Osler",
        "“The good physician treats the disease; the great physician treats the patient.” – Osler"
    ]
    st.success(random.choice(quotes))

elif menu == "📚 Notes Vault":
    st.header("🗂️ Medical Notes Vault")
    st.session_state.notes = st.text_area("Edit your medical notes here:", value=st.session_state.notes)
    if st.button("Save Notes"):
        st.success("Notes saved!")

elif menu == "🗓️ Study Planner":
    st.header("📆 Study Planner / Reminder")
    task = st.text_input("What do you want to study?")
    date = st.date_input("Date", datetime.date.today())
    if st.button("Add Reminder"):
        st.session_state.reminders.append({"task": task, "date": date})
        st.success("Reminder added!")
    for r in st.session_state.reminders:
        st.write(f"📌 {r['task']} on {r['date']}")

elif menu == "🤖 Backup AI":
    st.header("🤖 Backup Chatbot (simulated response)")
    backup_query = st.text_input("Ask ChatGPT backup:")
    if st.button("Ask Backup"):
        if backup_query:
            st.info(f"🔁 This is a simulated backup response for: **{backup_query}**")

elif menu == "📊 Study Chart":
    st.header("📈 Study Chart")
    if st.session_state.checkins:
        df = pd.DataFrame(st.session_state.checkins)
        st.line_chart(df.set_index("date")[["focus", "hours"]])
    else:
        st.warning("No check-in data yet.")

elif menu == "📆 Daily Check-In":
    st.header("📋 Daily Study Check-In")
    mood = st.selectbox("Mood", ["😃 Happy", "😐 Neutral", "😔 Tired"])
    focus = st.slider("Focus Level (0-10)", 0, 10)
    hours = st.slider("Hours Studied", 0, 12)
    if st.button("Submit Check-in"):
        st.session_state.checkins.append({
            "date": str(datetime.date.today()),
            "mood": mood,
            "focus": focus,
            "hours": hours
        })
        st.success("Check-in saved!")

elif menu == "📤 Export Progress":
    st.header("📁 Export Study Progress")
    if st.session_state.checkins:
        df = pd.DataFrame(st.session_state.checkins)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Check-in Data as CSV", data=csv, file_name="study_checkins.csv")
    else:
        st.warning("No check-in data to export.")
