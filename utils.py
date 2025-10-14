"""
Funções utilitárias para o Voicify
"""
import re
import os
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres inválidos.
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        str: Nome sanitizado
    """
    # Remove caracteres especiais
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Remove espaços múltiplos
    filename = re.sub(r'\s+', '_', filename)
    # Limita tamanho
    filename = filename[:100]
    
    return filename if filename else "audio"


def validate_text(text: str, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Valida texto de entrada.
    
    Args:
        text: Texto para validar
        max_length: Tamanho máximo permitido
        
    Returns:
        tuple: (válido, mensagem)
    """
    if not text or not text.strip():
        return False, "O texto não pode estar vazio"
    
    if len(text) > max_length:
        return False, f"Texto muito longo. Máximo: {max_length} caracteres"
    
    return True, "Texto válido"


def calculate_text_hash(text: str) -> str:
    """
    Calcula hash do texto para cache.
    
    Args:
        text: Texto
        
    Returns:
        str: Hash MD5
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def estimate_audio_duration(text: str, words_per_minute: int = 150) -> float:
    """
    Estima duração do áudio em segundos.
    
    Args:
        text: Texto
        words_per_minute: Palavras por minuto
        
    Returns:
        float: Duração em segundos
    """
    words = len(text.split())
    minutes = words / words_per_minute
    return minutes * 60


def format_duration(seconds: float) -> str:
    """
    Formata duração em formato legível.
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        str: Duração formatada
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        str: Tamanho formatado
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def count_words(text: str) -> int:
    """Conta palavras no texto."""
    return len(text.split())


def count_characters(text: str) -> int:
    """Conta caracteres no texto."""
    return len(text)


def split_text_into_chunks(text: str, max_chunk_size: int = 500) -> list:
    """
    Divide texto em chunks menores.
    
    Args:
        text: Texto para dividir
        max_chunk_size: Tamanho máximo do chunk em palavras
        
    Returns:
        list: Lista de chunks
    """
    sentences = re.split(r'[.!?]+', text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        words = sentence.split()
        sentence_size = len(words)
        
        if current_size + sentence_size > max_chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk) + '.')
            current_chunk = words
            current_size = sentence_size
        else:
            current_chunk.extend(words)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk) + '.')
    
    return chunks


def setup_logging():
    """Configura sistema de logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voicify.log', encoding='utf-8')
        ]
    )


def get_timestamp() -> str:
    """Retorna timestamp formatado."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
