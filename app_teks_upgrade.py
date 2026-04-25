import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

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
# CSS (PRO UI)
# =========================
st.markdown("""
<style>
body { background-color: #fff1f2; }

/* Header */
.header-title {
    font-size: 28px;
    font-weight: bold;
    color: #be123c;
}

/* Chat container */
.chat-container {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 15px;
    height: 60vh;
    overflow-y: auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* Chat bubbles */
.user-bubble {
    background-color: #fecdd3;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
}

.ai-bubble {
    background-color: #ffe4e6;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    max-width: 70%;
}

/* Button */
.stButton>button {
    background-color: #be123c;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1,6])

with col1:
    st.image("oel.png", width=70)

with col2:
    st.markdown("<div class='header-title'>AI Sekolah ORA et LABORA</div>", unsafe_allow_html=True)

st.caption("Asisten pintar sekolah • Data + AI + Voice")

# =========================
# API KEY
# =========================
try:
    if "MY_API_KEY" in st.secrets:
        api_key = st.secrets["MY_API_KEY"]
    else:
        api_key = st.sidebar.text_input("API Key", type="password")

    if api_key:
        genai.configure(api_key=api_key)
except:
    st.warning("Masukkan API Key dulu ya")

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# SIDEBAR
# =========================
st.sidebar.image("oel.png", width=120)
st.sidebar.markdown("## 🤖 AI Sekolah")

for chat in st.session_state.chat_history:
    role = "🧑" if chat["role"] == "user" else "🤖"
    st.sidebar.write(f"{role} {chat['message'][:40]}...")

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_all_data(folder_path="data"):
    all_text = ""

    if not os.path.exists(folder_path):
        return "Data tidak ditemukan."

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    all_text += f.read() + "\n\n"

            elif filename.endswith(".pdf"):
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n\n"

            elif filename.endswith(".docx"):
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    all_text += para.text + "\n\n"

        except:
            all_text += f"(Gagal baca {filename})\n"

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
# CHAT CONTAINER
# =========================
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"<div class='user-bubble'>{chat['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='ai-bubble'>{chat['message']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# INPUT AREA
# =========================
col1, col2 = st.columns([5,1])

with col1:
    prompt_user = st.text_input("Ketik pesan...", label_visibility="collapsed")

with col2:
    kirim = st.button("Kirim")

# =========================
# LOGIC
# =========================
if kirim:
    if not prompt_user:
        st.warning("Isi dulu ya")
    else:
        try:
            st.session_state.chat_history.append({
                "role": "user",
                "message": prompt_user
            })

            data_sekolah = load_all_data()

            context = f"""
Kamu adalah AI resmi Sekolah ORA et LABORA.

Aturan:
1. Jika pertanyaan tentang sekolah, gunakan data berikut.
2. Jika tidak ada di data, jawab dengan pengetahuan umum.
3. Jika benar-benar tidak tahu, jawab jujur.

Data sekolah:
{data_sekolah}
"""

            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    context += f"User: {chat['message']}\n"
                else:
                    context += f"AI: {chat['message']}\n"

            model = genai.GenerativeModel("gemini-1.5-flash-latest")

            with st.spinner("AI sedang berpikir..."):
                response = model.generate_content(context)

            ai_reply = response.text

            st.session_state.chat_history.append({
                "role": "ai",
                "message": ai_reply
            })

            audio_file = text_to_speech(ai_reply)
            st.audio(audio_file)

            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
