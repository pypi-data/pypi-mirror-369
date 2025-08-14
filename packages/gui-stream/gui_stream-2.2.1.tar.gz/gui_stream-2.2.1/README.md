# document-convert

Este projeto é contém uma interface gráfica em Python Tk para minipular e editar documentos.

- Ler, filtrar e exportar dados em planilhas Excel/CSV
- Combinar arquivos PDFs (Unir e dividir)
- Converter imagem em PDF(s)
- Extrair textos de imagens
- Converter coordenadas UTM em latitude longitude.

# Dependência externa - Tesseract para extrair texto das imagens 
    https://github.com/tesseract-ocr/tesseract

# Módulos python externos
    PyPDF2      - (para manipulação de arquivos/bytes em PDF)
    PyMuPDF     - (para manipulação de arquivos/bytes em PDF)
    reportlab   - (para manipulação de arquivos/bytes em PDF)
    openpyxl    - (para manipulação de planilhas Excel)
    pandas      - (para manipulação de planilhas Excel/CSV)
    Pillow      - (para manipulação de imagens)
    pytesseract - (para manipulação reconhecimento de texto em imagem com o tesseract)
    opencv-python - (para manipulação de imagens)
    pyinstaller   - OPCIONAL (para exportar um binário executável do projeto Linux/Windows/Mac)

# Instalação dos módulos
    pip install PyPDF2 PyMuPDF reportlab openpyxl pandas Pillow pytesseract opencv-python pyinstaller
