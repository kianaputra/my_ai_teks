import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile
import pandas as pd
from pypdf import PdfReader
import docx

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Sekolah ORA et LABORA",
    page_icon="oel.png",
    layout="wide"
)

# =========================
# SESSION (WAJIB PALING ATAS)
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# =========================
# CSS
# =========================
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
body {background-color: #f5f7fb;}

.user-bubble {
    background-color: #2563eb;
    color: white;
    padding: 10px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    margin-left: auto;
}

.ai-bubble {
    background-color: white;
    padding: 10px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR MENU
# =========================
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Pilih", ["💬 Chat AI", "📊 Dashboard", "🏫 Data Sekolah"])

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# =========================
# API KEY
# =========================
if "MY_API_KEY" in st.secrets:
    api_key = st.secrets["MY_API_KEY"]
else:
    api_key = st.sidebar.text_input("API Key", type="password")

if not api_key:
    st.warning("Masukkan API Key dulu ya")
    st.stop()

genai.configure(api_key=api_key)

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=60)
def load_all_data(folder_path="data"):
    all_text = ""

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            try:
                if filename.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        all_text += f.read()

                elif filename.endswith(".pdf"):
                    reader = PdfReader(file_path)
                    for page in reader.pages:
                        if page.extract_text():
                            all_text += page.extract_text()

                elif filename.endswith(".docx"):
                    doc = docx.Document(file_path)
                    for para in doc.paragraphs:
                        all_text += para.text

            except:
                pass

    return all_text

# =========================
# TEXT TO SPEECH
# =========================
def text_to_speech(text):
    tts = gTTS(text=text, lang='id')
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

# =========================
# HALAMAN CHAT
# =========================
if menu == "💬 Chat AI":

    st.title("🤖 AI Chat Sekolah ORA et LABORA")

    # tampilkan chat
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f'<div class="user-bubble">🧑 {chat["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-bubble">🤖 {chat["message"]}</div>', unsafe_allow_html=True)

    # INPUT MODERN (ANTI DOUBLE)
    prompt_user = st.chat_input("Tulis pertanyaan kamu...")

    if prompt_user:

        # 🔥 CEGAH DOUBLE
        if prompt_user == st.session_state.last_input:
            st.stop()

        st.session_state.last_input = prompt_user

        try:
            # simpan user
            st.session_state.chat_history.append({
                "role": "user",
                "message": prompt_user
            })

            data_sekolah = load_all_data()[:3000]

            context = f"""
Kamu adalah AI resmi Sekolah ORA et LABORA.
Jawab dengan jelas dan singkat.

Data:
{data_sekolah}

Pertanyaan:
{prompt_user}
"""

            model = genai.GenerativeModel("gemini-2.5-flash")

            with st.spinner("🤖 AI sedang berpikir..."):
                response = model.generate_content(context)

            ai_reply = getattr(response, "text", "Tidak ada respon")

            # simpan AI
            st.session_state.chat_history.append({
                "role": "ai",
                "message": ai_reply
            })

            # voice
            audio = text_to_speech(ai_reply)
            st.audio(audio)

            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# DASHBOARD
# =========================
elif menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.write("Total Chat:", len(st.session_state.chat_history))

# =========================
# DATA SEKOLAH
# =========================
elif menu == "🏫 Data Sekolah":
    st.title("🏫 Data Sekolah")
    st.write(load_all_data()[:2000])
