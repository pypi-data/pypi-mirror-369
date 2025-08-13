from pysearchlm import PDFAnalyzer

url = "https://arxiv.org/pdf/1706.03762.pdf"
analyzer = PDFAnalyzer()
generate = analyzer.analyze_pdf(url, api_key="GEMINI_API_KEY", language="en")


