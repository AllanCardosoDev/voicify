"""
Configurações do Voicify
"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class VoicifyConfig:
    """Configurações gerais da aplicação."""
    APP_TITLE = "Voicify - TTS Multilíngue Avançado"
    APP_ICON = "🎤"
    VERSION = "2.0"
    
    # Limites
    MAX_TEXT_LENGTH = 10000  # caracteres
    MAX_BATCH_SIZE = 10  # textos
    
    # Configurações de áudio
    DEFAULT_SPEED = 1.0
    MIN_SPEED = 0.5
    MAX_SPEED = 2.0
    
    # Cache
    ENABLE_CACHE = True
    CACHE_DIR = ".audio_cache"
    MAX_CACHE_SIZE_MB = 100


@dataclass
class LanguageConfig:
    """Configurações de idiomas e variantes."""
    
    LANGUAGES = {
        "Português (Brasil)": {"code": "pt-br", "flag": "🇧🇷", "tld": "com.br"},
        "Português (Portugal)": {"code": "pt-pt", "flag": "🇵🇹", "tld": "pt"},
        "Inglês (EUA)": {"code": "en-us", "flag": "🇺🇸", "tld": "com"},
        "Inglês (UK)": {"code": "en-gb", "flag": "🇬🇧", "tld": "co.uk"},
        "Inglês (Austrália)": {"code": "en-au", "flag": "🇦🇺", "tld": "com.au"},
        "Espanhol (Espanha)": {"code": "es-es", "flag": "🇪🇸", "tld": "es"},
        "Espanhol (México)": {"code": "es-mx", "flag": "🇲🇽", "tld": "com.mx"},
        "Francês": {"code": "fr", "flag": "🇫🇷", "tld": "fr"},
        "Alemão": {"code": "de", "flag": "🇩🇪", "tld": "de"},
        "Italiano": {"code": "it", "flag": "🇮🇹", "tld": "it"},
        "Russo": {"code": "ru", "flag": "🇷🇺", "tld": "ru"},
        "Chinês (Simplificado)": {"code": "zh-cn", "flag": "🇨🇳", "tld": "com"},
        "Japonês": {"code": "ja", "flag": "🇯🇵", "tld": "co.jp"},
        "Coreano": {"code": "ko", "flag": "🇰🇷", "tld": "co.kr"},
        "Árabe": {"code": "ar", "flag": "🇸🇦", "tld": "com"},
        "Hindi": {"code": "hi", "flag": "🇮🇳", "tld": "co.in"},
    }
    
    @classmethod
    def get_language_list(cls) -> List[str]:
        """Retorna lista de idiomas."""
        return list(cls.LANGUAGES.keys())
    
    @classmethod
    def get_language_info(cls, language_name: str) -> Dict:
        """Retorna informações do idioma."""
        return cls.LANGUAGES.get(language_name, {})


# Estilos CSS customizados
CUSTOM_CSS = """
<style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-top: 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .audio-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
</style>
"""
