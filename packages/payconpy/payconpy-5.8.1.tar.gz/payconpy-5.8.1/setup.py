import os
from setuptools import setup

version = '5.8.1'

with open("README.md", "r", encoding='utf-8') as fh:
    readme = fh.read()
    setup(
        name='payconpy',
        version=version,
        url='https://github.com/Paycon-Automacoes/payconpy',
        license='MIT License',
        author='Paycon Automações',
        long_description=readme,
        long_description_content_type="text/markdown",
        author_email='gabriel.souza@paycon.com.br',
        keywords='Funções Para Melhorar Desenvolvimento de Robôs com Selenium',
        description=u'Funções Para Melhorar Desenvolvimento de Robôs com Selenium',
        
        packages= [
            os.path.join('payconpy', 'femails'),
            os.path.join('payconpy', 'fexceptions'),
            os.path.join('payconpy', 'fpdf'),
            os.path.join('payconpy', 'fpdf', 'focr'),
            os.path.join('payconpy', 'fpdf', 'compress'),
            os.path.join('payconpy', 'fpdf', 'pdfutils'),
            os.path.join('payconpy', 'ffreesimplegui'),
            os.path.join('payconpy', 'fpython'),
            os.path.join('payconpy', 'fregex'),
            os.path.join('payconpy', 'fselenium'),
            os.path.join('payconpy', 'utils'),
            os.path.join('payconpy', 'openai'),
            os.path.join('payconpy', 'openai', 'assistants'),
            os.path.join('payconpy', 'openai', 'apis'),
            os.path.join('payconpy', 'odoo'),
        ],
        
        install_requires= [
            'selenium',
            'bs4',
            'requests',
            'html5lib',
            'webdriver-manager',
            'pretty-html-table',
            'xlsxwriter',
            'pandas',
            'openpyxl',
            'sqlalchemy',
            'rich',
            'pyinstaller',
            'filetype',
            'mywebdriver',
            # for ocr
            'pytesseract',
            'tqdm',
            'pillow',
            'PyMuPDF',
            'holidays',
            'FreeSimpleGui',
        ],
        extras_require={
            'openai': [ # for chatpdf
                'openai',
            ],
            'compress_pdf': [ # for compresser pdf
                'kepdf>=5.0.0',
            ]
    },
)
