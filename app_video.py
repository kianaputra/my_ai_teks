import streamlit as st
import google.generativeai as genai

# 1. Judul dan Tampilan
st.set_page_config(page_title="AI Generator", page_icon="🤖")
st.title("🤖 My Public AI Generator")

# 2. Konfigurasi API Key secara rahasia
# Bagian ini akan membaca API Key Anda secara otomatis dari sistem Streamlit
try:
    if "MY_API_KEY" in st.secrets:
        api_key = st.secrets["MY_API_KEY"]
    else:
        # Ini hanya untuk cadangan jika Anda masih mengetes di komputer sendiri
        api_key = st.sidebar.text_input("Masukkan API Key untuk Testing:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.warning("Menunggu API Key dikonfigurasi...")
except Exception as e:
    st.error(f"Koneksi ke sistem rahasia gagal: {e}")

# 3. Input Pengguna
prompt_user = st.text_area("Tuliskan apa yang ingin Anda buat:")

# 4. Proses AI
if st.button("Mulai Proses"):
    if not prompt_user:
        st.warning("Ketikkan sesuatu dulu ya!")
    else:
        try:
            # Mencari model secara otomatis agar tidak error 404
            available_models = [m.name for m in genai.list_models() 
                               if 'generateContent' in m.supported_generation_methods]
            
            if available_models:
                model = genai.GenerativeModel(available_models[0])
                with st.spinner("AI sedang berpikir..."):
                    response = model.generate_content(prompt_user)
                
                st.success("Selesai!")
                st.write("### Hasil:")
                st.write(response.text)
            else:
                st.error("Tidak ada model AI yang aktif di akun ini.")
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")
