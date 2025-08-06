#BioBERT Q&A system (medical question answering)
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import requests, re
from bs4 import BeautifulSoup

# Load QA pipeline
model_name = "ktrapeznikov/biobert_v1.1_pubmed_squad_v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)
qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

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

def get_medical_answer(question):
    try:
        context = search_wikipedia_summary(question)
        if "❌" in context or "⚠️" in context:
            return f"📚 Wikipedia says:\n{context}"
        result = qa_pipeline(question=question, context=context)
        answer = result['answer']
        if len(answer.strip()) < 5:
            raise ValueError("Too short")
        return f"🤖 AI (BioBERT) says:\n{answer.strip()}"
    except Exception:
        return f"📚 Wikipedia says:\n{search_wikipedia_summary(question)}"

#Text to speech function with gtts
from gtts import gTTS
import streamlit as st

def speak_text(text, filename="tts_output.mp3"):
    try:
        tts = gTTS(text)
        tts.save(filename)
        audio_file = open(filename, "rb")
        st.audio(audio_file.read(), format="audio/mp3")
    except Exception as e:
        st.error(f"🔊 TTS Error: {e}")

#Editable mnemonics section 
import streamlit as st
import pandas as pd

if "mnemonics_data" not in st.session_state:
    st.session_state.mnemonics_data = []

st.subheader("🧠 Add/Edit Mnemonics")

with st.form("mnemonic_form"):
    course = st.text_input("Course")
    topic = st.text_input("Topic")
    name = st.text_input("Mnemonic Name")
    content = st.text_area("Mnemonic Content")
    submitted = st.form_submit_button("➕ Save Mnemonic")

    if submitted and course and topic and name and content:
        st.session_state.mnemonics_data.append({
            "Course": course,
            "Topic": topic,
            "Name": name,
            "Content": content
        })
        st.success("Mnemonic added!")

st.markdown("---")
st.subheader("📚 Saved Mnemonics")

if st.session_state.mnemonics_data:
    df = pd.DataFrame(st.session_state.mnemonics_data)
    st.dataframe(df, use_container_width=True)

    for i, row in df.iterrows():
        st.markdown(f"**{row['Name']}** - _{row['Topic']} ({row['Course']})_")
        st.markdown(f"`{row['Content']}`")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete", key=f"del_{i}"):
                st.session_state.mnemonics_data.pop(i)
                st.experimental_rerun()

    if st.button("📤 Export Mnemonics to CSV"):
        csv = pd.DataFrame(st.session_state.mnemonics_data).to_csv(index=False)
        st.download_button("⬇️ Download Mnemonics CSV", csv, file_name="mnemonics.csv")
else:
    st.info("No mnemonics added yet.")

#Editable flashcards
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []

st.subheader("🗂️ Add Flashcards")

with st.form("flashcard_form"):
    f_course = st.text_input("Course")
    f_topic = st.text_input("Topic")
    f_question = st.text_area("Question")
    f_answer = st.text_area("Answer")
    flash_submit = st.form_submit_button("➕ Save Flashcard")

    if flash_submit and f_course and f_topic and f_question and f_answer:
        st.session_state.flashcards.append({
            "Course": f_course,
            "Topic": f_topic,
            "Question": f_question,
            "Answer": f_answer
        })
        st.success("Flashcard saved!")

st.markdown("---")
st.subheader("📋 Flashcards List")

if st.session_state.flashcards:
    for i, card in enumerate(st.session_state.flashcards):
        st.markdown(f"**Q:** {card['Question']}")
        with st.expander("💡 View Answer"):
            st.markdown(f"{card['Answer']}")
        if st.button("🗑️ Delete", key=f"flash_del_{i}"):
            st.session_state.flashcards.pop(i)
            st.experimental_rerun()
else:
    st.info("No flashcards yet.")

#Quizzes: Builder and Quiz mode
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

st.subheader("📝 Create Quiz Question")

with st.form("quiz_form"):
    q_course = st.text_input("Course")
    q_question = st.text_area("Question")
    q_a = st.text_input("Option A")
    q_b = st.text_input("Option B")
    q_c = st.text_input("Option C")
    q_d = st.text_input("Option D")
    q_correct = st.selectbox("Correct Answer", ["A", "B", "C", "D"])
    quiz_submit = st.form_submit_button("➕ Add Question")

    if quiz_submit and q_course and q_question and q_a and q_b and q_c and q_d:
        st.session_state.quiz_data.append({
            "Course": q_course,
            "Question": q_question,
            "A": q_a,
            "B": q_b,
            "C": q_c,
            "D": q_d,
            "Correct": q_correct
        })
        st.success("Question added!")

st.markdown("---")
st.subheader("🎮 Take a Quiz")

if st.session_state.quiz_data:
    quiz_df = pd.DataFrame(st.session_state.quiz_data)
    selected_course = st.selectbox("📚 Select Course", ["All"] + list(quiz_df["Course"].unique()))
    if selected_course != "All":
        quiz_df = quiz_df[quiz_df["Course"] == selected_course]

    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
        st.session_state.score = 0
        st.session_state.answers = []

    if st.session_state.quiz_index < len(quiz_df):
        current = quiz_df.iloc[st.session_state.quiz_index]
        st.markdown(f"**Q{st.session_state.quiz_index + 1}: {current['Question']}**")
        user_choice = st.radio(
            "Choose your answer:",
            [f"A. {current['A']}", f"B. {current['B']}", f"C. {current['C']}", f"D. {current['D']}"],
            key=f"quiz_q_{st.session_state.quiz_index}"
        )

        if st.button("✅ Submit Answer"):
            selected_letter = user_choice.split(".")[0]
            st.session_state.answers.append({
                "Question": current["Question"],
                "Your Answer": selected_letter,
                "Correct Answer": current["Correct"],
                "Is Correct": selected_letter == current["Correct"]
            })
            if selected_letter == current["Correct"]:
                st.session_state.score += 1
            st.session_state.quiz_index += 1
            st.experimental_rerun()
    else:
        total = len(st.session_state.answers)
        st.success(f"🎉 Completed! Your score: {st.session_state.score}/{total}")
        st.dataframe(pd.DataFrame(st.session_state.answers), use_container_width=True)
        if st.button("🔁 Retake Quiz"):
            del st.session_state.quiz_index
            del st.session_state.score
            del st.session_state.answers
            st.experimental_rerun()
else:
    st.info("No quiz questions available.")

import streamlit as st import pandas as pd import datetime

🧠 Sidebar Navigation

st.sidebar.title("🧠 Clinical AI Assistant") menu = st.sidebar.radio("Go to", ( "🏠 Home", "📅 Study Planner", "📈 Study Charts", "🧠 Daily Tracker", "🗃️ Fact Vault", "🤖 GPT Chat", "🩺 OSCE Simulations" ))

st.title("👨‍⚕️ Clinical Assistant Dashboard")

🏠 Home Section

if menu == "🏠 Home": st.header("Welcome to the Clinical AI Assistant") st.markdown(""" Use the sidebar to navigate between tools: - Plan studies via Google Form - Track study progress with charts - Log your mood, focus, and hours - Store important facts in vaults - Ask GPT medical questions - Simulate cases via OSCE tool """)

📅 Study Planner (Google Form link)

elif menu == "📅 Study Planner": st.subheader("📅 Study Planner") st.write("Plan your study using the form below:") st.markdown(""" 📝 Fill the Google Study Planner Form """)

📈 Study Charts (Mockup chart for now)

elif menu == "📈 Study Charts": st.subheader("📈 Study Progress Tracker") st.write("Below is a sample chart for visualization:")

df = pd.DataFrame({
    "Date": pd.date_range(start="2025-08-01", periods=7),
    "Hours": [1.5, 2, 2.5, 3, 2, 3.5, 4]
})
st.line_chart(df.set_index("Date"))

🧠 Daily Mood / Focus / Revision Tracker

elif menu == "🧠 Daily Tracker": st.subheader("🧠 Daily Mood / Focus / Study Tracker") with st.form("daily_checkin_form"): mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😞 Sad"]) focus = st.slider("Focus Level (1-10)", 1, 10, 5) hours = st.number_input("Hours of Study", min_value=0.0, step=0.5) revised = st.text_area("What did you revise today?") submitted = st.form_submit_button("Save Entry")

if submitted:
    st.success("✔️ Entry saved (mockup).")

🗃️ Fact Vault

elif menu == "🗃️ Fact Vault": st.subheader("🗃️ Medical Fact Vault") if "vault" not in st.session_state: st.session_state.vault = []

with st.form("vault_form"):
    topic = st.text_input("Topic")
    content = st.text_area("Important Fact")
    save = st.form_submit_button("➕ Save Fact")

if save and topic and content:
    st.session_state.vault.append({"Topic": topic, "Fact": content})
    st.success("💾 Fact Saved")

if st.session_state.vault:
    st.write("Saved Facts:")
    vault_df = pd.DataFrame(st.session_state.vault)
    st.dataframe(vault_df, use_container_width=True)

🤖 GPT Chat Support (Placeholder only)

elif menu == "🤖 GPT Chat": st.subheader("🤖 Ask GPT Medical Questions") st.info("Use built-in AI chat in Colab app for now.")

🩺 OSCE Simulation (Mock version)

elif menu == "🩺 OSCE Simulations": st.subheader("🩺 OSCE Case Simulation") st.markdown(""" Case 1: Abdominal Pain

A 24-year-old male presents with right lower quadrant abdominal pain, nausea, and fever.

- What is your differential diagnosis?
- What examinations would you perform?
- What investigations are needed?
- Outline your management plan.
""")
st.text_area("💬 Type your simulated response:")
st.button("✅ Submit Case")

