#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações básicas para o reconhecimento de texto em imagens:

+ INSTALAR O TESSERACT (ou usar uma versão portável para Windows)
    1 - instalar o idioma pt-br para melhorar a detecção dos textos.
        Linux   -> sudo apt-get install tesseract-ocr-por
        Windows -> Baixe o arquivo por.traineddata (https://github.com/tesseract-ocr/tessdata)
                    salvar o arquivo no diretório tessdata (Na raiz da pasta tesseract)
                    
        - Defina o diretório onde os arquivos de linguagem estão localizados 
            os.environ['TESSDATA_PREFIX'] = r'C:\\caminho\\para\\o\\diretorio\\das\\linguagens'

    2 - Defina o Caminho para o Executável do Tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        (Alterar o caminho se necessário)
        
    3 - Extraia o texto da imagem usando o idioma pt-BR 
            texto = pytesseract.image_to_string(imagem, lang='por')
            (já implementado no módulo OCR)    
        
    - Download do arquivo LANG em ptbr oficial.
        https://github.com/tesseract-ocr/tessdata/blob/main/por.traineddata

"""

from gui_stream import version
from gui_stream.launch import run_app
from convert_stream import print_title

appname: str = 'Conversor de Documentos'


def main():
    print_title(f' {appname} Versão: {version} ')
    print()
    run_app(appname)


if __name__ == '__main__':
    main()