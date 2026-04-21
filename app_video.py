import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Text Generator", page_icon="📝")
st.title("📝 My AI Text Generator")

with st.sidebar:
    api_key = "AIzaSyBBn17le6vdtI6iT0CEvzyM9wcp3DhDGYE" # Masukkan API Key asli Anda di sini di antara tanda kutip
    genai.configure(api_key=api_key)

prompt_user = st.text_area("Apa yang ingin Anda tanyakan?", 
                           placeholder="Contoh: Ceritakan tentang anak yang hilang...")

if st.button("Mulai Proses"):
    if not api_key:
        st.error("Masukkan API Key di samping!")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # --- LOGIKA OTOMATIS MENCARI MODEL ---
            available_models = [m.name for m in genai.list_models() 
                               if 'generateContent' in m.supported_generation_methods]
            
            if not available_models:
                st.error("Tidak ada model yang ditemukan untuk API Key ini.")
            else:
                # Pilih model pertama yang tersedia (biasanya yang paling stabil)
                model_name = available_models[0]
                model = genai.GenerativeModel(model_name)
                
                with st.spinner(f"Menggunakan {model_name}... Sedang berpikir..."):
                    response = model.generate_content(prompt_user)
                    
                st.success(f"Berhasil menggunakan {model_name}!")
                st.write("### Jawaban AI:")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            st.info("Saran: Coba buat API Key baru di Google AI Studio, mungkin project yang sekarang ada kendala teknis.")