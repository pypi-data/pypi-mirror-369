# pysearchlm

LLM-powered library that analyses academic PDF papers via Google Gemini URL Context and produces a comprehensive LaTeX technical summary.

## Features
- 🧠 **Gemini 2.5-pro** integration (URL Context, no downloading)
- 📝 **LaTeX** output with academic package suggestions
- 🌍 **Multi-language** summaries (tr, en, fr, de, es, it, nl, pt, ru)
- ⚙️ Modular codebase (`core/`, `utils/`)
- 🚀 Minimal usage examples (`examples/`)

## Installation
```bash
pip install -r requirements.txt
```
Set your API key:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="YOUR_API_KEY"

# macOS / Linux
export GEMINI_API_KEY="YOUR_API_KEY"

# or via .env
echo "GEMINI_API_KEY=YOUR_API_KEY" > .env
```

## Basic Usage
```python
from pysearchlm import PDFAnalyzer

url = "https://arxiv.org/pdf/1706.03762.pdf"
ana = PDFAnalyzer()
res = ana.analyze_pdf(url, language="en")
print(res["latex_file"]["path"]) if res["success"] else print(res["error"])
```

## Batch Analysis
```python
urls = [
    "https://arxiv.org/pdf/1706.03762.pdf",
    "https://arxiv.org/pdf/1810.04805.pdf"
]
ana = PDFAnalyzer()
results = ana.analyze_multiple_pdfs(urls, language="en")
print("Success", results["successful"], "/", results["total_pdfs"])
```

## Structure
```
core/   # Gemini client, PDF URL handler, LaTeX generator
utils/  # Config & helpers
examples/  # Minimal demos
pysearchlm.py  # Main API class
```

## Notes
- PDF is **not downloaded**; Gemini reads it directly via URL.
- LaTeX files are stored in `output/`.
- Make sure `GEMINI_API_KEY` is defined, otherwise the analyzer raises an error at startup.

## License
MIT. See [LICENSE](LICENSE).
