import streamlit as st
from gtts import gTTS
import io
import os

# Configuração da página
st.set_page_config(
    page_title="Voicify - TTS Multilíngue", 
    page_icon="🎤", 
    layout="wide"
)

# Título principal
st.markdown("""
    <h1 style='text-align: center; color: #1E88E5; margin-bottom: 0;'>
        Voicify
    </h1>
    <h3 style='text-align: center; color: #666; margin-top: 0;'>
        Gerador de Voz Multilíngue com IA
    </h3>
    """, unsafe_allow_html=True)

st.markdown("---")

# Interface principal
col1, col2 = st.columns([2, 1])

with col1:
    # Nome do áudio
    audio_name = st.text_input(
        "Nome do áudio:",
        placeholder="Digite o nome base para o(s) arquivo(s)"
    )
    
    # Área de texto
    text_input = st.text_area(
        "Digite o texto para converter em áudio:",
        height=200,
        placeholder="Digite seu texto aqui..."
    )

with col2:
    st.subheader("⚙️ Configurações")
    
    # Seleção de idioma
    languages = {
        "Português": "pt",
        "Inglês": "en",
        "Espanhol": "es",
        "Francês": "fr",
        "Alemão": "de",
        "Italiano": "it",
        "Russo": "ru",
        "Chinês": "zh-cn",
        "Japonês": "ja",
        "Coreano": "ko"
    }
    
    selected_language = st.selectbox(
        "Idioma:",
        list(languages.keys()),
        index=0
    )

# Botão de geração
if st.button("🎙️ Gerar Áudio", type="primary"):
    if not text_input:
        st.warning("⚠️ Por favor, digite algum texto")
    elif not audio_name:
        st.warning("⚠️ Por favor, forneça um nome para o áudio")
    else:
        try:
            with st.spinner("Gerando áudio..."):
                # Gerar áudio
                tts = gTTS(text=text_input, lang=languages[selected_language])
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                
                # Exibir player de áudio
                st.success("✅ Áudio gerado com sucesso!")
                st.audio(audio_buffer, format='audio/mp3')
                
                # Botão de download
                st.download_button(
                    label="📥 Baixar Áudio",
                    data=audio_buffer,
                    file_name=f"{audio_name}.mp3",
                    mime="audio/mp3"
                )
                
        except Exception as e:
            st.error(f"❌ Erro ao gerar áudio: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h2 style='color: #1E88E5;'>Voicify</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.header("ℹ️ Informações")
    st.markdown("""
    ### Como usar
    1. Digite um nome para o áudio
    2. Cole ou digite seu texto
    3. Escolha o idioma
    4. Clique em 'Gerar Áudio'
    
    ### Recursos
    - Suporte a múltiplos idiomas
    - Download em MP3
    - Interface simples e rápida
    """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Voicify - Desenvolvido com ❤️ usando Streamlit e gTTS</p>
    </div>

    """, unsafe_allow_html=True)
