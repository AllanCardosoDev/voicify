"""
Gerador de áudio avançado com cache e otimizações
"""
import os
import io
import logging
from typing import Optional, Dict, Any
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import streamlit as st

from config import VoicifyConfig
from utils import calculate_text_hash, split_text_into_chunks

logger = logging.getLogger(__name__)


class AudioGenerator:
    """Classe para gerar áudio a partir de texto."""
    
    def __init__(self, enable_cache: bool = True):
        """
        Inicializa o gerador de áudio.
        
        Args:
            enable_cache: Se deve usar cache
        """
        self.config = VoicifyConfig()
        self.enable_cache = enable_cache
        
        if self.enable_cache:
            self._init_cache()
    
    def _init_cache(self):
        """Inicializa o diretório de cache."""
        if not os.path.exists(self.config.CACHE_DIR):
            os.makedirs(self.config.CACHE_DIR)
    
    def _get_cache_path(self, text: str, lang: str, speed: float) -> str:
        """
        Gera caminho do arquivo no cache.
        
        Args:
            text: Texto
            lang: Idioma
            speed: Velocidade
            
        Returns:
            str: Caminho do arquivo
        """
        text_hash = calculate_text_hash(f"{text}_{lang}_{speed}")
        return os.path.join(self.config.CACHE_DIR, f"{text_hash}.mp3")
    
    def _check_cache(self, text: str, lang: str, speed: float) -> Optional[bytes]:
        """
        Verifica se áudio está no cache.
        
        Args:
            text: Texto
            lang: Idioma
            speed: Velocidade
            
        Returns:
            bytes: Dados do áudio ou None
        """
        if not self.enable_cache:
            return None
        
        cache_path = self._get_cache_path(text, lang, speed)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    logger.info(f"Áudio recuperado do cache: {cache_path}")
                    return f.read()
            except Exception as e:
                logger.error(f"Erro ao ler cache: {e}")
        
        return None
    
    def _save_to_cache(self, audio_data: bytes, text: str, lang: str, speed: float):
        """
        Salva áudio no cache.
        
        Args:
            audio_data: Dados do áudio
            text: Texto
            lang: Idioma
            speed: Velocidade
        """
        if not self.enable_cache:
            return
        
        cache_path = self._get_cache_path(text, lang, speed)
        
        try:
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"Áudio salvo no cache: {cache_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def generate_audio(
        self,
        text: str,
        lang: str,
        speed: float = 1.0,
        tld: str = 'com'
    ) -> Dict[str, Any]:
        """
        Gera áudio a partir de texto.
        
        Args:
            text: Texto para converter
            lang: Código do idioma
            speed: Velocidade da fala (0.5 a 2.0)
            tld: Top-level domain para variante
            
        Returns:
            dict: Informações do áudio gerado
        """
        try:
            # Verificar cache
            cached_audio = self._check_cache(text, lang, speed)
            if cached_audio:
                return {
                    'success': True,
                    'audio_data': cached_audio,
                    'from_cache': True,
                    'size': len(cached_audio)
                }
            
            # Gerar áudio
            logger.info(f"Gerando áudio - Idioma: {lang}, Velocidade: {speed}")
            
            tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            # Ajustar velocidade se necessário
            if speed != 1.0:
                audio_data = self._adjust_speed(audio_data, speed)
            
            # Salvar no cache
            self._save_to_cache(audio_data, text, lang, speed)
            
            return {
                'success': True,
                'audio_data': audio_data,
                'from_cache': False,
                'size': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _adjust_speed(self, audio_data: bytes, speed: float) -> bytes:
        """
        Ajusta velocidade do áudio.
        
        Args:
            audio_data: Dados do áudio
            speed: Fator de velocidade
            
        Returns:
            bytes: Áudio com velocidade ajustada
        """
        try:
            # Converter para AudioSegment
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Ajustar velocidade
            if speed > 1.0:
                audio = speedup(audio, playback_speed=speed)
            elif speed < 1.0:
                # Para desacelerar, usar sample rate
                new_sample_rate = int(audio.frame_rate * speed)
                audio = audio._spawn(audio.raw_data, overrides={
                    'frame_rate': new_sample_rate
                }).set_frame_rate(audio.frame_rate)
            
            # Converter de volta para bytes
            output_buffer = io.BytesIO()
            audio.export(output_buffer, format='mp3')
            output_buffer.seek(0)
            
            return output_buffer.read()
            
        except Exception as e:
            logger.warning(f"Erro ao ajustar velocidade: {e}")
            return audio_data  # Retornar original em caso de erro
    
    def generate_batch(
        self,
        texts: list,
        lang: str,
        speed: float = 1.0,
        tld: str = 'com'
    ) -> list:
        """
        Gera múltiplos áudios.
        
        Args:
            texts: Lista de textos
            lang: Idioma
            speed: Velocidade
            tld: Top-level domain
            
        Returns:
            list: Lista de resultados
        """
        results = []
        
        for i, text in enumerate(texts):
            result = self.generate_audio(text, lang, speed, tld)
            result['index'] = i
            result['text'] = text[:100] + "..." if len(text) > 100 else text
            results.append(result)
        
        return results
