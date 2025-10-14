"""
Voicify - TTS Multilíngue Avançado
Versão 2.0 com recursos melhorados
"""
import streamlit as st
import io
import os
import time
from datetime import datetime
from typing import List, Dict, Any

# Imports locais (se usar arquivos separados)
# from config import VoicifyConfig, LanguageConfig, CUSTOM_CSS
# from utils import (sanitize_filename, validate_text, estimate_audio_duration, 
#                    format_duration, format_file_size, count_words, 
#                    count_characters, split_text_into_chunks, setup_logging)
# from audio_generator import AudioGenerator

# OU imports diretos se preferir tudo em um arquivo:
from gtts import gTTS
import re
import hashlib
import logging

# ============================================
# CONFIGURAÇÕES (inline - pode separar depois)
# ============================================

class VoicifyConfig:
    APP_TITLE = "Voicify - TTS Multilíngue Avançado"
    APP_ICON = "🎤"
    VERSION = "2.0"
    MAX_TEXT_LENGTH = 10000
    MAX_BATCH_SIZE = 10
    DEFAULT_SPEED = 1.0
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0
    ENABLE_CACHE = True
    CACHE_DIR = ".audio_cache"

class LanguageConfig:
    LANGUAGES = {
        "🇧🇷 Português (Brasil)": {"code": "pt-br", "tld": "com.br"},
        "🇵🇹 Português (Portugal)": {"code": "pt-pt", "tld": "pt"},
        "🇺🇸 Inglês (EUA)": {"code": "en", "tld": "com"},
        "🇬🇧 Inglês (UK)": {"code": "en", "tld": "co.uk"},
        "🇦🇺 Inglês (Austrália)": {"code": "en", "tld": "com.au"},
        "🇪🇸 Espanhol (Espanha)": {"code": "es", "tld": "es"},
        "🇲🇽 Espanhol (México)": {"code": "es", "tld": "com.mx"},
        "🇫🇷 Francês": {"code": "fr", "tld": "fr"},
        "🇩🇪 Alemão": {"code": "de", "tld": "de"},
        "🇮🇹 Italiano": {"code": "it", "tld": "it"},
        "🇷🇺 Russo": {"code": "ru", "tld": "ru"},
        "🇨🇳 Chinês (Simplificado)": {"code": "zh-cn", "tld": "com"},
        "🇯🇵 Japonês": {"code": "ja", "tld": "co.jp"},
        "🇰🇷 Coreano": {"code": "ko", "tld": "co.kr"},
        "🇸🇦 Árabe": {"code": "ar", "tld": "com"},
        "🇮🇳 Hindi": {"code": "hi", "tld": "co.in"},
    }

# CSS Customizado
CUSTOM_CSS = """
<style>
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.3rem;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .audio-card {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .success-box {
        background: #d4edda;
        border: 2px solid #c3e6cb;
        color: #155724;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #1976d2;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 2px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        border: none;
        padding: 1rem;
        border-radius: 10px;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .feature-box {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #e0e0e0;
        transition: all 0.3s;
    }
    .feature-box:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
</style>
"""

# ============================================
# FUNÇÕES UTILITÁRIAS
# ============================================

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos do nome do arquivo."""
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename[:100] if filename else "audio"

def validate_text(text: str, max_length: int = 10000):
    """Valida o texto de entrada."""
    if not text or not text.strip():
        return False, "⚠️ O texto não pode estar vazio"
    if len(text) > max_length:
        return False, f"⚠️ Texto muito longo. Máximo: {max_length:,} caracteres"
    return True, "✅ Texto válido"

def estimate_audio_duration(text: str, words_per_minute: int = 150) -> float:
    """Estima a duração do áudio."""
    words = len(text.split())
    minutes = words / words_per_minute
    return minutes * 60

def format_duration(seconds: float) -> str:
    """Formata duração para exibição."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m {remaining_seconds}s"

def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo."""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB"

def count_words(text: str) -> int:
    """Conta palavras no texto."""
    return len(text.split())

def count_characters(text: str) -> int:
    """Conta caracteres no texto."""
    return len(text)

def calculate_text_hash(text: str) -> str:
    """Calcula hash do texto para cache."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def split_long_text(text: str, max_length: int = 500) -> List[str]:
    """Divide texto longo em partes menores."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(word) + 1
        if current_length > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# ============================================
# GERADOR DE ÁUDIO
# ============================================

def generate_audio(text: str, lang_code: str, tld: str = 'com') -> Dict[str, Any]:
    """Gera áudio a partir do texto."""
    try:
        start_time = time.time()
        
        # Gerar áudio
        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_data = audio_buffer.read()
        
        generation_time = time.time() - start_time
        
        return {
            'success': True,
            'audio_data': audio_data,
            'size': len(audio_data),
            'generation_time': generation_time
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================
# INICIALIZAÇÃO
# ============================================

def init_session_state():
    """Inicializa variáveis de sessão."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'total_audios' not in st.session_state:
        st.session_state.total_audios = 0
    if 'total_characters' not in st.session_state:
        st.session_state.total_characters = 0
    if 'show_stats' not in st.session_state:
        st.session_state.show_stats = True

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title=VoicifyConfig.APP_TITLE,
    page_icon=VoicifyConfig.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Inicializar sessão
init_session_state()

# ============================================
# CABEÇALHO
# ============================================

st.markdown(f"""
    <h1 class='main-title'>{VoicifyConfig.APP_ICON} Voicify</h1>
    <p class='subtitle'>Gerador de Voz Multilíngue com IA - Versão {VoicifyConfig.VERSION}</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# INTERFACE PRINCIPAL
# ============================================

# Layout em colunas
col_main, col_settings = st.columns([2, 1])

with col_main:
    st.markdown("### 📝 Configuração do Áudio")
    
    # Nome do áudio
    audio_name = st.text_input(
        "Nome do arquivo:",
        value=f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Nome que será usado para salvar o arquivo de áudio"
    )
    
    # Área de texto com contador
    text_input = st.text_area(
        "Digite o texto para converter em áudio:",
        height=250,
        placeholder="Digite ou cole seu texto aqui...\n\nDica: Textos longos serão processados automaticamente!",
        help=f"Máximo: {VoicifyConfig.MAX_TEXT_LENGTH:,} caracteres"
    )
    
    # Estatísticas do texto em tempo real
    if text_input:
        words = count_words(text_input)
        chars = count_characters(text_input)
        estimated_duration = estimate_audio_duration(text_input)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{chars:,}</div>
                    <div class='stat-label'>Caracteres</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{words:,}</div>
                    <div class='stat-label'>Palavras</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class='stat-card'>
                    <div class='stat-value'>{format_duration(estimated_duration)}</div>
                    <div class='stat-label'>Duração Est.</div>
                </div>
            """, unsafe_allow_html=True)
        with col4:
            progress = min(chars / VoicifyConfig.MAX_TEXT_LENGTH, 1.0)
            color = "#4caf50" if progress < 0.8 else "#ff9800" if progress < 0.95 else "#f44336"
            st.markdown(f"""
                <div class='stat-card' style='background: {color};'>
                    <div class='stat-value'>{progress*100:.0f}%</div>
                    <div class='stat-label'>Limite</div>
                </div>
            """, unsafe_allow_html=True)

with col_settings:
    st.markdown("### ⚙️ Configurações")
    
    # Seleção de idioma
    selected_language = st.selectbox(
        "Idioma e Sotaque:",
        list(LanguageConfig.LANGUAGES.keys()),
        index=0,
        help="Escolha o idioma e a variante regional"
    )
    
    lang_info = LanguageConfig.LANGUAGES[selected_language]
    
    # Opções avançadas
    with st.expander("🎛️ Opções Avançadas", expanded=False):
        # Velocidade (simulada - gTTS não suporta nativamente)
        st.info("⚠️ Ajuste de velocidade requer pydub (pip install pydub)")
        
        # Dividir texto longo
        auto_split = st.checkbox(
            "Dividir texto longo automaticamente",
            value=False,
            help="Divide textos muito longos em múltiplos áudios"
        )
        
        # Qualidade
        quality = st.select_slider(
            "Qualidade de Áudio:",
            options=["Baixa", "Média", "Alta"],
            value="Média",
            help="Qualidade do áudio gerado (em desenvolvimento)"
        )

# ============================================
# GERAÇÃO DE ÁUDIO
# ============================================

st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    generate_button = st.button("🎙️ Gerar Áudio", type="primary", use_container_width=True)

with col_btn2:
    if st.button("🗑️ Limpar Texto", use_container_width=True):
        st.rerun()

with col_btn3:
    if st.button("📊 Ver Histórico", use_container_width=True):
        st.session_state.show_stats = not st.session_state.show_stats

if generate_button:
    # Validações
    is_valid, message = validate_text(text_input, VoicifyConfig.MAX_TEXT_LENGTH)
    
    if not audio_name:
        st.error("⚠️ Por favor, forneça um nome para o áudio")
    elif not is_valid:
        st.error(message)
    else:
        # Processar geração
        with st.spinner("🎵 Gerando áudio..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simular progresso
            for i in range(30):
                time.sleep(0.03)
                progress_bar.progress(i / 100)
                status_text.text(f"Preparando... {i}%")
            
            # Gerar áudio
            result = generate_audio(
                text_input,
                lang_info['code'],
                lang_info['tld']
            )
            
            progress_bar.progress(100)
            
            if result['success']:
                # Sucesso!
                audio_data = result['audio_data']
                file_size = result['size']
                gen_time = result['generation_time']
                
                # Atualizar estatísticas
                st.session_state.total_audios += 1
                st.session_state.total_characters += len(text_input)
                
                # Adicionar ao histórico
                st.session_state.history.append({
                    'name': audio_name,
                    'language': selected_language,
                    'size': file_size,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'chars': len(text_input)
                })
                
                progress_bar.empty()
                status_text.empty()
                
                # Exibir resultado
                st.markdown(f"""
                    <div class='success-box'>
                        <h3>✅ Áudio Gerado com Sucesso!</h3>
                        <p><strong>Nome:</strong> {audio_name}.mp3</p>
                        <p><strong>Tamanho:</strong> {format_file_size(file_size)}</p>
                        <p><strong>Tempo de geração:</strong> {gen_time:.2f}s</p>
                        <p><strong>Idioma:</strong> {selected_language}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Player de áudio
                st.audio(audio_data, format='audio/mp3')
                
                # Botões de ação
                col_download, col_new = st.columns(2)
                
                with col_download:
                    st.download_button(
                        label="📥 Baixar Áudio MP3",
                        data=audio_data,
                        file_name=f"{sanitize_filename(audio_name)}.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                
                with col_new:
                    if st.button("🔄 Gerar Novo Áudio", use_container_width=True):
                        st.rerun()
                
            else:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Erro ao gerar áudio: {result['error']}")

# ============================================
# HISTÓRICO E ESTATÍSTICAS
# ============================================

if st.session_state.show_stats and st.session_state.history:
    st.markdown("---")
    st.markdown("### 📊 Estatísticas e Histórico")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{st.session_state.total_audios}</div>
                <div class='stat-label'>Áudios Gerados</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{st.session_state.total_characters:,}</div>
                <div class='stat-label'>Caracteres Processados</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        avg_chars = st.session_state.total_characters // max(st.session_state.total_audios, 1)
        st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{avg_chars:,}</div>
                <div class='stat-label'>Média por Áudio</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Histórico recente
    st.markdown("#### 🕒 Histórico Recente")
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(f"""
            <div class='audio-card'>
                <strong>🎵 {item['name']}</strong><br>
                <small>
                📅 {item['timestamp']} | 
                🌍 {item['language']} | 
                📊 {format_file_size(item['size'])} | 
                📝 {item['chars']} caracteres
                </small>
            </div>
        """, unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #667eea; font-size: 2.5rem;'>{VoicifyConfig.APP_ICON}</h1>
            <h2 style='color: #667eea;'>Voicify</h2>
            <p style='color: #666;'>v{VoicifyConfig.VERSION}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📖 Como Usar")
    st.markdown("""
        <div class='feature-box'>
            <strong>1️⃣ Nomeie seu áudio</strong><br>
            <small>Dê um nome descritivo para o arquivo</small>
        </div>
        <div class='feature-box'>
            <strong>2️⃣ Digite o texto</strong><br>
            <small>Cole ou digite o conteúdo</small>
        </div>
        <div class='feature-box'>
            <strong>3️⃣ Escolha o idioma</strong><br>
            <small>Selecione idioma e sotaque</small>
        </div>
        <div class='feature-box'>
            <strong>4️⃣ Gere o áudio</strong><br>
            <small>Clique no botão e aguarde</small>
        </div>
        <div class='feature-box'>
            <strong>5️⃣ Baixe ou ouça</strong><br>
            <small>Player integrado ou download MP3</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ✨ Recursos")
    st.markdown("""
    - 🌍 **16 idiomas** com variantes
    - 📊 **Estatísticas** em tempo real
    - 💾 **Download MP3** direto
    - 🎵 **Player integrado** para preview
    - 📈 **Contador de palavras** automático
    - ⏱️ **Estimativa de duração**
    - 📜 **Histórico** de gerações
    - 🎨 **Interface moderna** e intuitiva
    """)
    
    st.markdown("---")
    
    st.markdown("### 🛠️ Suporte")
    st.info("""
    **Idiomas Suportados:**
    - Português (BR/PT)
    - Inglês (US/UK/AU)
    - Espanhol (ES/MX)
    - E mais 10 idiomas!
    
    **Limites:**
    - Máx: 10.000 caracteres
    - Formato: MP3
    - Qualidade: Alta
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Limpar Histórico", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_audios = 0
        st.session_state.total_characters = 0
        st.success("✅ Histórico limpo!")
        st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p style='font-size: 1.1rem;'>
            <strong>Voicify</strong> - Desenvolvido com ❤️ usando 
            <a href='https://streamlit.io' target='_blank' style='color: #667eea;'>Streamlit</a> e 
            <a href='https://github.com/pndurette/gTTS' target='_blank' style='color: #667eea;'>gTTS</a>
        </p>
        <p style='font-size: 0.9rem;'>
            © 2024 Voicify. Geração de voz multilíngue com inteligência artificial.
        </p>
    </div>
""", unsafe_allow_html=True)
