#✅ Full Working Clinical AI Assistant App (With Voice Input/Output + BioBERT)

#Includes: AI Medical Q&A, Voice Input/Output, Clean Layout

import streamlit as st import speech_recognition as sr from gtts import gTTS import os import torch from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline import requests, re from bs4 import BeautifulSoup import tempfile

st.set_page_config(page_title="Clinical AI Assistant", layout="centered") st.title("👨‍⚕️ Clinical AI Assistant")

---------------------- Load BioBERT QA pipeline ----------------------

st.info("Loading AI model... (BioBERT)") model_name = "ktrapeznikov/biobert_v1.1_pubmed_squad_v2" tokenizer = AutoTokenizer.from_pretrained(model_name) model = AutoModelForQuestionAnswering.from_pretrained(model_name) qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

---------------------- Wikipedia Context Search ----------------------

def search_wikipedia_summary(query): try: search_url = f"https://en.wikipedia.org/w/index.php?search={query.replace(' ', '+')}" headers = {"User-Agent": "Mozilla/5.0"} search_response = requests.get(search_url, headers=headers, timeout=20) soup = BeautifulSoup(search_response.text, 'html.parser') result_link = soup.select_one("ul.mw-search-results li a") article_url = "https://en.wikipedia.org" + result_link["href"] if result_link else search_response.url article_response = requests.get(article_url, headers=headers, timeout=20) soup = BeautifulSoup(article_response.text, 'html.parser') for para in soup.select("div.mw-parser-output > p"): text = para.get_text().strip() if len(text) > 100: text = re.sub(r']*]', '', text) return text return "⚠️ Couldn't extract readable Wikipedia paragraph." except Exception as e: return f"❌ Wikipedia error: {str(e)}"

---------------------- Answer Medical Question ----------------------

def get_medical_answer(question): try: context = search_wikipedia_summary(question) if "❌" in context or "⚠️" in context: return f"📚 Wikipedia says:\n{context}" result = qa_pipeline(question=question, context=context) answer = result['answer'] if len(answer.strip()) < 5: raise ValueError("Too short") return f"🤖 AI (BioBERT) says:\n{answer.strip()}" except Exception: return f"📚 Wikipedia says:\n{search_wikipedia_summary(question)}"

---------------------- Voice Input Handler ----------------------

def listen_to_voice(): recognizer = sr.Recognizer() with sr.Microphone() as source: st.info("🎤 Listening... Speak now!") audio = recognizer.listen(source, timeout=5, phrase_time_limit=10) try: st.success("✅ Voice captured. Transcribing...") text = recognizer.recognize_google(audio) return text except sr.UnknownValueError: return "❌ Could not understand audio." except sr.RequestError: return "❌ Could not request results."

---------------------- Text-to-Speech Handler ----------------------

def speak_text(text): try: tts = gTTS(text) with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp: tts.save(fp.name) st.audio(fp.name, format="audio/mp3") except Exception as e: st.error(f"🔊 TTS Error: {e}")

---------------------- Sidebar Navigation ----------------------

menu = st.sidebar.radio("🧠 Navigate", ["🏠 Home", "🎤 Ask Medical Question (Voice)", "⌨️ Ask Medical Question (Text)"])

---------------------- 🏠 Home ----------------------

if menu == "🏠 Home": st.subheader("📋 Welcome") st.markdown(""" Clinical AI Assistant Features: - 🤖 Ask medical questions via BioBERT AI - 🎤 Use voice input to ask - 🔊 Get spoken answers back - 📚 Wikipedia context-powered AI """)

---------------------- 🎤 Ask via Voice ----------------------

elif menu == "🎤 Ask Medical Question (Voice)": st.subheader("🎤 Voice Medical Q&A") if st.button("🎙️ Start Listening"): question = listen_to_voice() st.write(f"🗣️ You asked: {question}") response = get_medical_answer(question) st.success(response) speak_text(response)

---------------------- ⌨️ Ask via Text ----------------------

elif menu == "⌨️ Ask Medical Question (Text)": st.subheader("⌨️ Text-based Medical Q&A") user_q = st.text_input("Ask a medical question") if st.button("Get Answer") and user_q: response = get_medical_answer(user_q) st.success(response) speak_text(response)

