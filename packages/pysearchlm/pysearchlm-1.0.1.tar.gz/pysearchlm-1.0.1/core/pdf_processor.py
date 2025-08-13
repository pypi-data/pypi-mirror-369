"""
PDF URL işleme modülü
Gemini-2.5-pro URL Context özelliği için PDF URL doğrulama ve hazırlama
"""
import requests
from typing import Dict, Any, Optional
from utils.config import Config
from utils.helpers import validate_url


class PDFURLHandler:
    """PDF URL doğrulama ve Gemini için hazırlama sınıfı"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def validate_pdf_url(self, url: str) -> Dict[str, Any]:
        """
        PDF URL'sini doğrula ve temel bilgileri topla
        
        Args:
            url: Doğrulanacak PDF URL'si
            
        Returns:
            URL bilgileri ve doğrulama durumu
        """
        result = {
            'url': url,
            'is_valid': False,
            'is_accessible': False,
            'is_pdf': False,
            'content_type': None,
            'size_mb': None,
            'status_code': None,
            'error': None
        }
        
        try:
            # URL format kontrolü
            if not validate_url(url):
                result['error'] = "Geçersiz URL formatı"
                return result
            
            result['is_valid'] = True
            
            # HEAD request ile dosya bilgilerini kontrol et
            response = self.session.head(
                url, 
                timeout=Config.PDF_TIMEOUT_SECONDS,
                allow_redirects=True
            )
            
            result['status_code'] = response.status_code
            
            if response.status_code == 200:
                result['is_accessible'] = True
                
                # Content-Type kontrolü
                content_type = response.headers.get('content-type', '').lower()
                result['content_type'] = content_type
                
                # PDF kontrolü (content-type veya URL uzantısı)
                if 'pdf' in content_type or url.lower().endswith('.pdf'):
                    result['is_pdf'] = True
                
                # Dosya boyutu kontrolü
                content_length = response.headers.get('content-length')
                if content_length:
                    size_bytes = int(content_length)
                    size_mb = size_bytes / (1024 * 1024)
                    result['size_mb'] = round(size_mb, 2)
                    
                    if size_mb > Config.MAX_PDF_SIZE_MB:
                        result['error'] = f"PDF dosyası çok büyük: {size_mb:.1f}MB (max: {Config.MAX_PDF_SIZE_MB}MB)"
                        result['is_pdf'] = False
            else:
                result['error'] = f"HTTP {response.status_code}: Dosyaya erişilemedi"
                
        except requests.RequestException as e:
            result['error'] = f"Bağlantı hatası: {str(e)}"
        except Exception as e:
            result['error'] = f"Beklenmeyen hata: {str(e)}"
        
        return result
    
    def prepare_url_for_gemini(self, url: str) -> Dict[str, Any]:
        """
        URL'yi Gemini URL Context özelliği için hazırla
        
        Args:
            url: PDF URL'si
            
        Returns:
            Gemini için hazırlanmış URL bilgileri
        """
        # URL'yi doğrula
        validation_result = self.validate_pdf_url(url)
        
        if not validation_result['is_valid']:
            raise ValueError(f"Geçersiz URL: {validation_result['error']}")
        
        if not validation_result['is_accessible']:
            raise ValueError(f"URL'ye erişilemedi: {validation_result['error']}")
        
        if not validation_result['is_pdf']:
            # PDF olmayabilir ama devam et, Gemini'nin kendisi halledebilir
            print(f"Uyarı: Dosya PDF olmayabilir. Content-Type: {validation_result['content_type']}")
        
        # Gemini için URL bilgilerini hazırla
        gemini_url_context = {
            'url': url,
            'validated': True,
            'content_type': validation_result['content_type'],
            'size_mb': validation_result['size_mb'],
            'ready_for_processing': True
        }
        
        return gemini_url_context
    
    def check_url_accessibility(self, url: str) -> bool:
        """
        Hızlı URL erişilebilirlik kontrolü
        
        Args:
            url: Kontrol edilecek URL
            
        Returns:
            URL erişilebilir mi?
        """
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False