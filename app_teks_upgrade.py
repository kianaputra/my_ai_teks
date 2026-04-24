import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Sekolah ORA et LABORA",
    page_icon="🤖",
    layout="wide"
)

# =========================
# CSS (WARNA SALEM LEMBUT)
# =========================
st.markdown("""
<style>
body {
    background-color: #fff1f2;
}

.main {
    background-color: #fff1f2;
}

.user-bubble {
    background-color: #fecdd3;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    margin-left: auto;
}

.ai-bubble {
    background-color: #ffe4e6;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
}

.sidebar .sidebar-content {
    background-color: #ffe4e6;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🤖 AI Chat Sekolah ORA et LABORA")
st.caption("Dengan Memory + Voice + Sidebar History")

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
# SIDEBAR (CHAT HISTORY)
# =========================
st.sidebar.title("💬 Chat History")

for i, chat in enumerate(st.session_state.chat_history):
    role = "🧑" if chat["role"] == "user" else "🤖"
    st.sidebar.write(f"{role} {chat['message'][:40]}...")

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# =========================
# TAMPILKAN CHAT UTAMA
# =========================
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div class="user-bubble">{chat["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{chat["message"]}</div>', unsafe_allow_html=True)

# =========================
# INPUT
# =========================
MAX_CHAR = 500

prompt_user = st.text_area("Ketik pesan kamu:", height=100)
char_count = len(prompt_user)

st.caption(f"{char_count}/{MAX_CHAR} karakter")

# =========================
# FUNCTION: TEXT TO SPEECH
# =========================
def text_to_speech(text):
    tts = gTTS(text=text, lang='id')
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

# =========================
# BUTTON
# =========================
if st.button("Kirim"):
    if not prompt_user:
        st.warning("Isi dulu ya")
    elif char_count > MAX_CHAR:
        st.error("Terlalu panjang!")
    else:
        try:
            # simpan user
            st.session_state.chat_history.append({
                "role": "user",
                "message": prompt_user
            })

            # =========================
            # MEMORY AI (AMBIL HISTORY)
            # =========================
            context = ""
            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    context += f"User: {chat['message']}\n"
                else:
                    context += f"AI: {chat['message']}\n"

            # =========================
            # MODEL
            # =========================
            available_models = [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]

            model = genai.GenerativeModel(available_models[0])

            with st.spinner("AI sedang berpikir..."):
                response = model.generate_content(context)

            ai_reply = response.text

            # simpan AI
            st.session_state.chat_history.append({
                "role": "ai",
                "message": ai_reply
            })

            # =========================
            # TEXT TO SPEECH
            # =========================
            audio_file = text_to_speech(ai_reply)
            st.audio(audio_file)

            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
