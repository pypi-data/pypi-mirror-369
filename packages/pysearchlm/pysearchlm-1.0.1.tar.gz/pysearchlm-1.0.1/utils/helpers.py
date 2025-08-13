"""
Yardımcı fonksiyonlar modülü
"""
import re
import urllib.parse
from typing import Optional


def validate_url(url: str) -> bool:
    """URL geçerliliğini kontrol et"""
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """Metni temizle ve normalize et"""
    if not text:
        return ""
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    
    # Satır başı ve sonundaki boşlukları temizle
    text = text.strip()
    
    # Özel karakterleri normalize et
    text = text.replace('\x00', '')  # Null karakterleri kaldır
    text = text.replace('\ufeff', '')  # BOM karakterini kaldır
    
    return text


def extract_title_from_text(text: str) -> Optional[str]:
    """Metinden başlık çıkar"""
    if not text:
        return None
    
    lines = text.split('\n')
    for line in lines[:10]:  # İlk 10 satırı kontrol et
        line = line.strip()
        if line and len(line) > 10 and len(line) < 200:
            # Başlık olabilecek satırları bul
            if not line.lower().startswith(('abstract', 'introduction', 'keywords')):
                return line
    
    return None


def sanitize_filename(filename: str) -> str:
    """Dosya adını temizle"""
    # Geçersiz karakterleri kaldır
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Fazla boşlukları temizle
    filename = re.sub(r'\s+', '_', filename)
    
    # Maksimum uzunluk
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename.strip('_')


def format_latex_text(text: str) -> str:
    """Metni LaTeX formatı için hazırla"""
    if not text:
        return ""
    
    # LaTeX özel karakterlerini escape et
    latex_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\textasciicircum{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}'
    }
    
    for char, replacement in latex_chars.items():
        text = text.replace(char, replacement)
    
    return text


def estimate_reading_time(text: str) -> int:
    """Metni okuma süresini tahmin et (dakika)"""
    if not text:
        return 0
    
    # Ortalama okuma hızı: 200 kelime/dakika
    word_count = len(text.split())
    reading_time = max(1, word_count // 200)
    
    return reading_time

