import streamlit as st
import random
from datetime import datetime
import pyttsx3
import speech_recognition as sr
from fpdf import FPDF

# ---------------------------- Voice Support ----------------------------
engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source, timeout=5)
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            st.warning("Sorry, I could not understand your voice.")
        except sr.RequestError:
            st.error("Could not request results. Check your internet.")
    return ""

# ---------------------------- Clinical Q&A ----------------------------
def clinical_response(user_input):
    if "pancreatitis" in user_input.lower():
        return "Pancreatitis is inflammation of the pancreas, often caused by gallstones or alcohol."
    elif "asthma" in user_input.lower():
        return "Asthma is a chronic condition causing airway inflammation and difficulty in breathing."
    return "Sorry, I don't know that yet. Please rephrase or try a simpler term."

# ---------------------------- Flashcard Quiz ----------------------------
quiz_data = {
    "Pharmacology": {"What is the antidote for heparin?": "Protamine sulfate"},
    "Pathology": {"What cell is characteristic in Hodgkin lymphoma?": "Reed-Sternberg cell"}
}

# ---------------------------- Mnemonics ----------------------------
mnemonics = {
    "Pharmacology": {"Beta-blockers": "A-M are cardioselective, N-Z are non-selective"},
    "Pathology": {"Causes of clubbing": "CLUB - Cyanotic heart disease, Lung disease, Ulcerative colitis, Biliary cirrhosis"}
}

# ---------------------------- OSCE Simulation ----------------------------
osce_cases = [
    {"case": "Patient with chest pain", "questions": ["What are the possible causes?", "How would you manage it?"]},
    {"case": "Unconscious patient", "questions": ["What is your immediate action?", "List differential diagnoses."]}
]

# ---------------------------- Study Planner ----------------------------
study_goals = []

# ---------------------------- Motivation + Mood Tracker ----------------------------
daily_quotes = [
    "Keep pushing. You're closer than you think.",
    "Every expert was once a beginner.",
    "Study smart, not just hard."
]

# ---------------------------- PDF Export ----------------------------
def export_summary(goals, mood, notes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Study Summary", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, txt=f"Mood: {mood}", ln=True)
    pdf.multi_cell(0, 10, txt="Goals:\n" + "\n".join(goals))
    pdf.multi_cell(0, 10, txt=f"Notes:\n{notes}")
    pdf.output("/mnt/data/study_summary.pdf")
    st.success("📄 Study summary exported successfully!")
    st.download_button("Download PDF", data=open("/mnt/data/study_summary.pdf", "rb"), file_name="study_summary.pdf")

# ---------------------------- Streamlit UI ----------------------------
st.set_page_config(page_title="Clinical AI Assistant", layout="wide")
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", ["Home", "Ask AI", "Flashcards Quiz", "OSCE Simulation", "Mnemonics", "Study Planner", "Mood + Quote", "Export Summary"])

# ---------------------------- Sections ----------------------------
if section == "Home":
    st.title("Clinical AI Assistant Dashboard")
    st.markdown("""
    Welcome to your all-in-one MBBS study assistant!
    
    **Features:**
    - Clinical AI Q&A (text/voice)
    - Flashcards + Quiz
    - OSCE Simulation
    - Mnemonics Memory Bank
    - Study Goals & Planner
    - Daily Mood Tracker & Quotes
    - Export Study Summaries as PDF
    """)

elif section == "Ask AI":
    st.header("Ask Medical Questions")
    input_method = st.radio("Choose input method:", ["Text", "Voice"])
    user_query = ""
    if input_method == "Text":
        user_query = st.text_input("Type your question here:")
    else:
        if st.button("🎤 Listen"):
            user_query = listen()
    if user_query:
        reply = clinical_response(user_query)
        st.success(reply)
        if st.button("🔊 Speak Answer"):
            speak(reply)

elif section == "Flashcards Quiz":
    st.header("Flashcard Quiz")
    subject = st.selectbox("Choose Subject", list(quiz_data.keys()))
    for question, answer in quiz_data[subject].items():
        user_ans = st.text_input(f"{question}")
        if user_ans:
            if user_ans.strip().lower() == answer.lower():
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect! Correct answer: {answer}")

elif section == "OSCE Simulation":
    st.header("OSCE Simulator")
    for i, case in enumerate(osce_cases):
        with st.expander(f"Case {i+1}: {case['case']}"):
            for q in case["questions"]:
                st.write(f"Q: {q}")
                st.text_area("Your Answer")

elif section == "Mnemonics":
    st.header("Pharma/Patho Mnemonics")
    subject = st.selectbox("Select Subject", list(mnemonics.keys()))
    topic = st.selectbox("Select Topic", list(mnemonics[subject].keys()))
    st.write("Mnemonic:", mnemonics[subject][topic])

elif section == "Study Planner":
    st.header("Your Study Goals")
    new_goal = st.text_input("Add new goal:")
    if st.button("Add Goal"):
        study_goals.append(new_goal)
    if study_goals:
        for i, goal in enumerate(study_goals):
            st.write(f"{i+1}. {goal}")

elif section == "Mood + Quote":
    st.header("Track Mood & Daily Quote")
    mood = st.selectbox("How do you feel today?", ["😊 Happy", "😐 Okay", "😔 Tired"])
    st.success(f"Quote of the Day: {random.choice(daily_quotes)}")
    notes = st.text_area("Study Notes or Reflections")

elif section == "Export Summary":
    st.header("📤 Export Study Summary")
    if st.button("Export as PDF"):
        mood = st.selectbox("Mood for the day", ["😊 Happy", "😐 Okay", "😔 Tired"])
        notes = st.text_area("Notes:")
        export_summary(study_goals, mood, notes)
