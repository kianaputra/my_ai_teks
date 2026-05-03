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
# CSS
# =========================
st.markdown("""
<style>

/* Hilangkan padding atas biar naik */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem;
}

/* Background clean */
body {
    background-color: #f5f7fb;
}

/* Banner */
.banner {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: -20px;
    margin-bottom: 10px;
}

/* Title */
.title {
    font-size: 26px;
    font-weight: 700;
    color: #1f2d3d;
}

/* Subtitle */
.subtitle {
    font-size: 14px;
    color: #6b7280;
}

/* User bubble */
.user-bubble {
    background-color: #2563eb;
    color: white;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
}

/* AI bubble */
.ai-bubble {
    background-color: white;
    color: #111;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 8px 0;
    max-width: 70%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

/* Input box */
textarea {
    border-radius: 12px !important;
}

/* Button */
.stButton>button {
    border-radius: 10px;
    background-color: #2563eb;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
}

/* Hilangkan footer */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="banner">', unsafe_allow_html=True)

st.image("1.png", width=250)

st.markdown("""
<div>
    <div class="title">AI Chat Sekolah ORA et LABORA</div>
    <div class="subtitle">Dengan Memory + Voice + Data Sekolah</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# DATA GAMBAR
# =========================
data_gambar = {
    "brosur": "data/gambar1.PNG",
    "psb 2026": "data/gambar1.PNG",
    "psb 2026-2027": "data/gambar1.PNG",
    "jadwal sekolah": "data/jadwal.png"
}

# =========================
# API KEY
# =========================
if "MY_API_KEY" in st.secrets:
    api_key = st.secrets["MY_API_KEY"]
else:
    api_key = st.sidebar.text_input("API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("Masukkan API Key dulu ya")
    st.stop()

# =========================
# SESSION
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# SIDEBAR
# =========================
st.sidebar.title("💬 Chat History")

for chat in st.session_state.chat_history:
    role = "🧑" if chat["role"] == "user" else "🤖"
    st.sidebar.write(f"{role} {chat['message'][:40]}...")

if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# =========================
# LOAD DATA (LOCAL + GOOGLE SHEET)
# =========================
@st.cache_data(ttl=60)
def load_all_data(folder_path="data"):
    all_text = ""

    # =========================
    # 1. LOAD FILE LOKAL
    # =========================
    if os.path.exists(folder_path):
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

    # =========================
    # 2. LOAD GOOGLE SHEET
    # =========================
    try:
        sheet_urls = [ 
            # FILE 1 (2 sheet)
            "https://docs.google.com/spreadsheets/d/1suSM7789E8zsoPsb9YH0G1BIoKxi3nci02dLm5xBW2g/export?format=csv&gid=0",
            "https://docs.google.com/spreadsheets/d/1suSM7789E8zsoPsb9YH0G1BIoKxi3nci02dLm5xBW2g/export?format=csv&gid=1368700838",

            # FILE 2 (1 sheet)
            "https://docs.google.com/spreadsheets/d/1FY9zao3G8oHuEttMAxKkpfIC2aET8BS_w3IuWgMfY14/export?format=csv"
        ]

        for url in sheet_urls:
            try:
                df = pd.read_csv(url)

                all_text += f"\n\n=== DATA DARI: {url} ===\n\n"

                for _, row in df.iterrows():
                    row_text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
                    all_text += row_text + "\n"

            except Exception as e:
                all_text += f"\n(Gagal load salah satu sheet: {e})\n"

    except Exception as e:
        all_text += f"\n(Gagal load Google Sheet: {e})\n"

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
# TAMPILKAN CHAT + GAMBAR
# =========================
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div class="user-bubble">{chat["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{chat["message"]}</div>', unsafe_allow_html=True)

        # tampilkan gambar kalau ada
        if "images" in chat:
            for path, caption in chat["images"]:
                st.image(path, caption=caption)

# =========================
# INPUT
# =========================
MAX_CHAR = 500
prompt_user = st.text_area("Ketik apa yang mau kamu tanya:", height=100)
char_count = len(prompt_user)
st.caption(f"{char_count}/{MAX_CHAR} karakter")

# =========================
# BUTTON
# =========================
if st.button("Kirim"):

    if not prompt_user.strip():
        st.warning("Isi dulu ya")
        st.stop()

    if char_count > MAX_CHAR:
        st.error("Terlalu panjang!")
        st.stop()

    try:
        # simpan user
        st.session_state.chat_history.append({
            "role": "user",
            "message": prompt_user
        })

        # =========================
        # CEK GAMBAR
        # =========================
        images_found = []
        for keyword, path in data_gambar.items():
            if keyword in prompt_user.lower():
                images_found.append((path, keyword))

        # =========================
        # DATA SEKOLAH
        # =========================
        data_sekolah = load_all_data()[:3000]

        # =========================
        # CONTEXT
        # =========================
        context = f"""
Kamu adalah AI resmi Sekolah ORA et LABORA.
Jawab dengan jelas dan singkat.

Data sekolah:
{data_sekolah}

Pertanyaan:
{prompt_user}
"""

        # =========================
        # MODEL
        # =========================
        model = genai.GenerativeModel("gemini-2.5-flash")

        with st.spinner("AI sedang berpikir..."):
            response = model.generate_content(context)

        ai_reply = getattr(response, "text", "Tidak ada respon dari AI")

        # simpan AI + gambar
        st.session_state.chat_history.append({
            "role": "ai",
            "message": ai_reply,
            "images": images_found
        })

        # VOICE
        audio_file = text_to_speech(ai_reply)
        st.audio(audio_file)

        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
