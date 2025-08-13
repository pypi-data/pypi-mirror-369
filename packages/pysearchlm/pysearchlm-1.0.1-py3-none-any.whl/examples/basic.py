from pysearchlm import PDFAnalyzer
from dotenv import load_dotenv

load_dotenv()

url = "https://arxiv.org/pdf/1706.03762.pdf"
analyzer = PDFAnalyzer()
generate = analyzer.analyze_pdf(url)


