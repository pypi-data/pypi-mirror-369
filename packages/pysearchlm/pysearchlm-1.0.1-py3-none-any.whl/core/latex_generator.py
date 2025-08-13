"""
LaTeX çıktı işleme ve dosya oluşturma modülü
"""
import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from utils.helpers import sanitize_filename, format_latex_text


class LaTeXGenerator:
    """LaTeX dosya oluşturma ve düzenleme sınıfı"""
    
    def __init__(self, output_dir: str = "output"):
        """
        LaTeX generator'ı başlat
        
        Args:
            output_dir: Çıktı klasörü
        """
        self.output_dir = output_dir
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Çıktı klasörünün var olduğundan emin ol"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def clean_latex_content(self, latex_content: str) -> str:
        """
        Gemini'den gelen LaTeX içeriğini temizle ve düzenle
        
        Args:
            latex_content: Ham LaTeX içeriği
            
        Returns:
            Temizlenmiş LaTeX içeriği
        """
        if not latex_content:
            return ""
        
        # Markdown code block'larını kaldır
        latex_content = re.sub(r'```latex\s*', '', latex_content)
        latex_content = re.sub(r'```\s*$', '', latex_content, flags=re.MULTILINE)
        latex_content = re.sub(r'^```.*$', '', latex_content, flags=re.MULTILINE)
        
        # Fazla boşlukları temizle
        latex_content = re.sub(r'\n\s*\n\s*\n', '\n\n', latex_content)
        
        # Türkçe karakterler için inputenc kontrolü
        if 'inputenc' not in latex_content and any(ord(c) > 127 for c in latex_content):
            latex_content = latex_content.replace(
                '\\usepackage[utf8]{inputenc}',
                '\\usepackage[utf8]{inputenc}\n\\usepackage[T1]{fontenc}'
            )
        
        # Eksik paketleri kontrol et ve ekle
        required_packages = [
            '\\usepackage{amsmath}',
            '\\usepackage{amsfonts}', 
            '\\usepackage{amssymb}',
            '\\usepackage{graphicx}',
            '\\usepackage{hyperref}'
        ]
        
        for package in required_packages:
            if package not in latex_content and '\\begin{document}' in latex_content:
                # documentclass'tan sonra ekle
                latex_content = latex_content.replace(
                    '\\begin{document}',
                    f'{package}\n\\begin{{document}}'
                )
        
        return latex_content.strip()
    
    def extract_title_from_latex(self, latex_content: str) -> Optional[str]:
        """
        LaTeX içeriğinden başlığı çıkar
        
        Args:
            latex_content: LaTeX içeriği
            
        Returns:
            Başlık metni
        """
        # \\title{...} pattern'ini ara
        title_match = re.search(r'\\title\{([^}]+)\}', latex_content)
        if title_match:
            title = title_match.group(1)
            # LaTeX komutlarını temizle
            title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)
            title = re.sub(r'\\[a-zA-Z]+', '', title)
            return title.strip()
        
        return None
    
    def generate_filename(self, title: Optional[str] = None, language: str = "tr") -> str:
        """
        LaTeX dosyası için uygun dosya adı oluştur
        
        Args:
            title: Makale başlığı
            language: Dil kodu
            
        Returns:
            Dosya adı (.tex uzantısı ile)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if title:
            # Başlığı dosya adı için uygun hale getir
            clean_title = sanitize_filename(title)
            # Maksimum 50 karakter
            if len(clean_title) > 50:
                clean_title = clean_title[:50]
            filename = f"{clean_title}_{language}_{timestamp}"
        else:
            filename = f"academic_summary_{language}_{timestamp}"
        
        return f"{filename}.tex"
    
    def add_metadata_comments(self, latex_content: str, metadata: Dict[str, Any]) -> str:
        """
        LaTeX dosyasına metadata yorumları ekle
        
        Args:
            latex_content: LaTeX içeriği
            metadata: Metadata bilgileri
            
        Returns:
            Metadata yorumları eklenmiş LaTeX içeriği
        """
        comments = []
        comments.append("% ============================================")
        comments.append("% Otomatik oluşturulan akademik makale özeti")
        comments.append("% PySearchLM kütüphanesi ile üretilmiştir")
        comments.append("% ============================================")
        
        if metadata.get('source_url'):
            comments.append(f"% Kaynak URL: {metadata['source_url']}")
        
        if metadata.get('model_used'):
            comments.append(f"% Kullanılan Model: {metadata['model_used']}")
        
        if metadata.get('language'):
            comments.append(f"% Dil: {metadata['language']}")
        
        if metadata.get('token_count'):
            comments.append(f"% Token Sayısı: {metadata['token_count']}")
        
        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comments.append(f"% Oluşturulma Zamanı: {generation_time}")
        comments.append("% ============================================")
        comments.append("")
        
        # Başına ekle
        return "\n".join(comments) + "\n" + latex_content
    
    def save_latex_file(self, 
                       latex_content: str, 
                       metadata: Dict[str, Any],
                       custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        LaTeX içeriğini dosyaya kaydet
        
        Args:
            latex_content: LaTeX içeriği
            metadata: Dosya metadata'sı
            custom_filename: Özel dosya adı
            
        Returns:
            Kaydetme sonucu bilgileri
        """
        try:
            # LaTeX içeriğini temizle
            clean_content = self.clean_latex_content(latex_content)
            
            if not clean_content:
                raise ValueError("Boş LaTeX içeriği")
            
            # Başlığı çıkar
            title = self.extract_title_from_latex(clean_content)
            
            # Dosya adını oluştur
            if custom_filename:
                filename = custom_filename if custom_filename.endswith('.tex') else f"{custom_filename}.tex"
            else:
                filename = self.generate_filename(title, metadata.get('language', 'tr'))
            
            # Tam dosya yolu
            file_path = os.path.join(self.output_dir, filename)
            
            # Metadata yorumlarını ekle
            final_content = self.add_metadata_comments(clean_content, metadata)
            
            # Dosyayı kaydet
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # Dosya bilgilerini döndür
            file_info = {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'title': title,
                'size_bytes': len(final_content.encode('utf-8')),
                'line_count': len(final_content.split('\n')),
                'language': metadata.get('language', 'tr'),
                'created_at': datetime.now().isoformat()
            }
            
            print(f"LaTeX dosyası kaydedildi: {file_path}")
            return file_info
            
        except Exception as e:
            error_info = {
                'success': False,
                'error': str(e),
                'file_path': None,
                'filename': None
            }
            
            print(f"LaTeX dosya kaydetme hatası: {str(e)}")
            # Debug için hata detayı
            import traceback
            print("Hata detayı:")
            traceback.print_exc()
            return error_info
    
    def validate_latex_syntax(self, latex_content: str) -> Dict[str, Any]:
        """
        Temel LaTeX syntax kontrolü
        
        Args:
            latex_content: Kontrol edilecek LaTeX içeriği
            
        Returns:
            Doğrulama sonucu
        """
        errors = []
        warnings = []
        
        # Temel yapı kontrolü
        if '\\documentclass' not in latex_content:
            errors.append("\\documentclass eksik")
        
        if '\\begin{document}' not in latex_content:
            errors.append("\\begin{document} eksik")
        
        if '\\end{document}' not in latex_content:
            errors.append("\\end{document} eksik")
        
        # Brace kontrolü
        open_braces = latex_content.count('{')
        close_braces = latex_content.count('}')
        if open_braces != close_braces:
            errors.append(f"Süslü parantez uyumsuzluğu: {open_braces} açık, {close_braces} kapalı")
        
        # Environment kontrolü
        begin_envs = re.findall(r'\\begin\{([^}]+)\}', latex_content)
        end_envs = re.findall(r'\\end\{([^}]+)\}', latex_content)
        
        for env in begin_envs:
            if env not in end_envs:
                errors.append(f"Environment '{env}' kapatılmamış")
        
        # Türkçe karakter kontrolü
        if any(ord(c) > 127 for c in latex_content):
            if 'inputenc' not in latex_content:
                warnings.append("Türkçe karakter kullanılıyor ama inputenc paketi eksik")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }
