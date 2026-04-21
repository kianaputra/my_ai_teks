import streamlit as st
import google.generativeai as genai

# =========================
# CONFIG PAGE
# =========================
st.set_page_config(
    page_title="AI Generator",
    page_icon="🤖",
    layout="centered"
)

# =========================
# CUSTOM CSS (BIAR CAKEP)
# =========================
st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}

.chat-container {
    display: flex;
    flex-direction: column;
}

.user-bubble {
    background-color: #dbeafe;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    align-self: flex-end;
}

.ai-bubble {
    background-color: #e5e7eb;
    padding: 10px 15px;
    border-radius: 15px;
    margin: 5px 0;
    max-width: 70%;
    align-self: flex-start;
}

.input-box {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.title("🤖 My Public AI Generator")
st.caption("AI sederhana dengan tampilan seperti chat")

# =========================
# API KEY CONFIG
# =========================
try:
    if "MY_API_KEY" in st.secrets:
        api_key = st.secrets["MY_API_KEY"]
    else:
        api_key = st.sidebar.text_input("Masukkan API Key:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Masukkan API Key dulu ya")
except Exception as e:
    st.error(f"Error: {e}")

# =========================
# SESSION STATE (CHAT HISTORY)
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# TAMPILKAN CHAT
# =========================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div class="user-bubble">{chat["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{chat["message"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# INPUT USER
# =========================
MAX_CHAR = 500

prompt_user = st.text_area(
    "Ketik pesan:",
    height=100,
    placeholder="Tulis sesuatu...",
)

char_count = len(prompt_user)

st.caption(f"{char_count}/{MAX_CHAR} karakter")

# =========================
# VALIDASI PANJANG TEKS
# =========================
if char_count > MAX_CHAR:
    st.warning("Teks terlalu panjang! Maksimal 500 karakter.")

# =========================
# BUTTON
# =========================
if st.button("Kirim"):
    if not prompt_user:
        st.warning("Tulis dulu pesannya")
    elif char_count > MAX_CHAR:
        st.error("Pesan terlalu panjang")
    else:
        try:
            # simpan user message
            st.session_state.chat_history.append({
                "role": "user",
                "message": prompt_user
            })

            # cari model
            available_models = [
                m.name for m in genai.list_models()
                if 'generateContent' in m.supported_generation_methods
            ]

            if available_models:
                model = genai.GenerativeModel(available_models[0])

                with st.spinner("AI sedang berpikir..."):
                    response = model.generate_content(prompt_user)

                ai_reply = response.text

                # simpan AI response
                st.session_state.chat_history.append({
                    "role": "ai",
                    "message": ai_reply
                })

                st.rerun()
            else:
                st.error("Tidak ada model tersedia")

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# CLEAR CHAT
# =========================
if st.button("🗑️ Hapus Chat"):
    st.session_state.chat_history = []
    st.rerun()
