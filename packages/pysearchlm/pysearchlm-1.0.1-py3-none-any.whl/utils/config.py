"""
Konfigürasyon yönetimi modülü
"""
import os
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

class Config:
    """Sistem konfigürasyon ayarları"""
    
    # Gemini API ayarları
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = "gemini-2.5-pro"  
    
    # PDF işleme ayarları
    MAX_PDF_SIZE_MB = 50
    PDF_TIMEOUT_SECONDS = 30
    
    # Dil ayarları
    SUPPORTED_LANGUAGES = {
        'tr': 'türkçe',
        'en': 'english',
        'fr': 'français',
        'de': 'deutsch',
        'es': 'español',
        'it': 'italiano',
        'nl': 'nederlands',
        'pt': 'português',
        'ru': 'русский',
    }
    
    # LaTeX ayarları
    OUTPUT_FORMAT = '.tex'
    DEFAULT_LANGUAGE = 'tr'
    
    # Prompt ayarları
    MAX_TOKENS = 32768
    TEMPERATURE = 0.1  # Akademik metinler için düşük sıcaklık
    
    @classmethod
    def validate_api_key(cls, api_key: str = None) -> str:
        """API anahtarı doğrulaması"""
        key = api_key or cls.GEMINI_API_KEY
        if not key:
            raise ValueError("Gemini API anahtarı gerekli! GEMINI_API_KEY çevre değişkenini ayarlayın.")
        return key
    
    @classmethod
    def get_language_name(cls, lang_code: str) -> str:
        """Dil kodundan dil adını döndür"""
        return cls.SUPPORTED_LANGUAGES.get(lang_code, cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE])

