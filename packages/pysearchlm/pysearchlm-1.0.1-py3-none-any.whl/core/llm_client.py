"""
Gemini-2.5-pro LLM Client modülü
URL Context özelliği ile PDF analizi
"""
import google.generativeai as genai
from typing import Dict, Any, Optional
from utils.config import Config


class GeminiClient:
    """Gemini-2.5-pro API client sınıfı"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini client'ını başlat
        
        Args:
            api_key: Gemini API anahtarı
        """
        self.api_key = Config.validate_api_key(api_key)
        
        # Gemini'yi yapılandır
        genai.configure(api_key=self.api_key)
        
        # Model'i başlat
        self.model = genai.GenerativeModel(
            model_name=Config.GEMINI_MODEL,
            generation_config={
                "temperature": Config.TEMPERATURE,
                "max_output_tokens": Config.MAX_TOKENS,
                "top_p": 0.8,
                "top_k": 40
            }
        )
    
    def generate_academic_summary_prompt(self, language: str = "tr") -> str:
        """
        Akademik makale özeti için güçlü prompt 
        
        Args:
            language: Hedef dil ("tr","en","fr","de","es","it","nl","pt","ru")
            
        Returns:
            Prompt metni
        """
        lang_name = Config.get_language_name(language)
        
        prompt = f"""Sen çok deneyimli bir akademik araştırma uzmanısın. Verilen PDF teknik makalesini kapsamlı şekilde analiz edip LaTeX formatında detaylı akademik özet oluşturacaksın.

DİL: Tüm çıktını {lang_name} dilinde oluştur.

YAKLAŞIM: Makalenin içeriğine ve kapsamına göre uygun uzunlukta, ama her durumda KAPSAMLI ve DETAYLI bir özet oluştur. Makalede mevcut olan tüm önemli bilgileri çıkar.

GÖREV:
PDF'deki akademik makaleyi tamamen oku, analiz et ve aşağıdaki kriterlere göre {lang_name} LaTeX formatında kapsamlı bir teknik özet hazırla:

DETAYLI ANALIZ KRİTERLERİ:
1. **Araştırma Problemi**: Hangi teknik sorunu çözmeye odaklanıyor? Problemin literatürdeki yeri nedir? Neden önemli?
2. **Literatür Özeti**: Hangi önceki çalışmalardan bahsediyor? Bu çalışmanın literatürdeki konumu?
3. **Metodoloji**: Hangi yaklaşımları, algoritmaları, teknikleri kullanıyor? Nasıl çalışıyor? Adım adım açıkla.
4. **Teknik İnovasyon**: Tamamen yeni olan nedir? Hangi teknik buluşları var?
5. **Matematiksel Formülasyon**: Tüm önemli formülleri, denklemleri, matematiksel ifadeleri detayıyla açıkla.
6. **Mimari/Algoritma Detayları**: Sistem mimarisi, algoritma adımları (Bu kısıma önem verebilirsin).
7. **Deneysel Kurulum**: Hangi veri setleri, nasıl deneyler, hangi metrikler, karşılaştırmalı analizler?
8. **Performans Analizi**: Sonuçlar, başarı oranları, karşılaştırmalar, avantajlar, dezavantajlar.
9. **Teknik Zorluklar**: Hangi problemlerle karşılaşılmış, nasıl çözülmüş?
10. **Gelecek Çalışmalar**: Limitasyonlar, açık problemler, gelecekteki araştırma yönleri.

LATEX ÇIKTI FORMATI:
- Tam LaTeX dokümanı oluştur (\\documentclass'tan \\end{{document}}'a kadar)

ZORUNLU PAKETLER:
- \\usepackage[utf8]{{inputenc}}
- \\usepackage[T1]{{fontenc}} 
- \\usepackage[turkish/english]{{babel}} (dile göre)
- \\usepackage{{amsmath,amsfonts,amssymb}} (matematik)
- \\usepackage{{graphicx}} (resimler)
- \\usepackage{{hyperref}} (linkler)

TABLO VE FORMAT PAKETLERİ (tablo varsa MUTLAKA kullan):
- \\usepackage{{booktabs}} (profesyonel tablolar)
- \\usepackage{{array}} (tablo düzenleme)
- \\usepackage{{tabularx}} (otomatik genişlik)
- \\usepackage{{longtable}} (uzun tablolar)
- \\usepackage{{adjustbox}} (tablo boyut ayarlama)
- \\usepackage[table]{{xcolor}} (tablo renkleri)

DİĞER YARLI PAKETLER:
- \\usepackage{{geometry}} (sayfa düzeni)
- \\usepackage{{caption}} (başlık formatı)
- \\usepackage{{subcaption}} (alt başlıklar)  
- \\usepackage{{algorithm,algorithmic}} (algoritmalar için)
- \\usepackage{{listings}} (kod örnekleri için)
- \\usepackage{{url}} (URL formatı)
- \\usepackage{{microtype}} (mikro tipografi)

KRİTİK TALİMATLAR:
- Makalenin içeriğine göre uygun düzeyde detay sağla
- Var olan tüm önemli bilgileri çıkar ve açıkla
- Matematiksel formülleri LaTeX notasyonu ile yaz: $formül$, $$formül$$, \\begin{{equation}}
- Listeleri, tabloları, algoritmaları uygun yerlerde kullan
- Akademik, bilimsel dil kullan
- Objektif ve eleştirel yaklaşım sergile
- Görsel veya fotoğraf eklemeye çalışma, gerek yok.
- SADECE LaTeX kodunu döndür, başka hiçbir açıklama yapma
- Geniş ama akıllı özet oluştur - gereksiz uzatma yapma
- Her bölümü makalede var olan bilgilere göre doldur"""

        return prompt
    
    def analyze_pdf_from_url(self, url: str, language: str = "tr") -> Dict[str, Any]:
        """
        PDF URL'sini Gemini ile analiz et
        
        Args:
            url: PDF URL'si
            language: Hedef dil ("tr" veya "en")
            
        Returns:
            Analiz sonucu
        """
        try:
            print(f"Gemini ile PDF analizi başlıyor: {url}")
            
            # Prompt'u hazırla
            system_prompt = self.generate_academic_summary_prompt(language)
            
            # URL Context ile prompt oluştur
            user_prompt = f"""
Lütfen şu URL'deki PDF akademik makalesini analiz et: {url}

Bu teknik makaleyi derinlemesine oku ve analiz et. Özellikle aşağıdaki noktalara dikkat et:
- Araştırma metodolojisi ve teknik yaklaşım
- Algoritmalar ve matematiksel formüller  
- Kullanılan sistem mimarisi ve yapısı
- Kullanılan kaynak, veri seti, veri kümesi gibi detaylar
- Ana katkılar ve yenilikler
- Çalışmanın amacı ve sonuçları

Sadece LaTeX formatında kapsamlı özet döndür.
"""
            
            # Gemini'ye gönder
            response = self.model.generate_content([
                system_prompt,
                user_prompt
            ])
            
            if not response or not response.text:
                raise Exception("Gemini'den boş yanıt geldi")
            
            result = {
                'latex_summary': response.text,
                'language': language,
                'source_url': url,
                'model_used': Config.GEMINI_MODEL,
                'success': True,
                'token_count': len(response.text.split()) if response.text else 0
            }
            
            print(f"Analiz tamamlandı. Token sayısı: {result['token_count']}")
            return result
            
        except Exception as e:
            error_result = {
                'latex_summary': None,
                'language': language,
                'source_url': url,
                'model_used': Config.GEMINI_MODEL,
                'success': False,
                'error': str(e),
                'token_count': 0
            }
            
            print(f"Gemini analiz hatası: {str(e)}")
            return error_result
    
    def test_api_connection(self) -> bool:
        """
        Gemini API bağlantısını test et
        
        Returns:
            API çalışıyor mu?
        """
        try:
            # Basit bir test sorgusu
            response = self.model.generate_content("Merhaba, API testi.")
            return bool(response and response.text)
        except Exception as e:
            print(f"API bağlantı testi başarısız: {e}")
            return False
