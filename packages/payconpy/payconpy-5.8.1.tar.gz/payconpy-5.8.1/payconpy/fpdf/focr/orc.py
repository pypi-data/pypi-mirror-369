from payconpy.fpython.fpython import *
from tqdm import tqdm
from PIL import Image
import fitz, uuid, os, pytesseract, base64

def faz_ocr_em_pdf_offline(path_pdf: str, export_from_file_txt: str = False) -> str:
    """
    Converte pdf(s) em texto com fitz (PyMuPDF)
        
    Atenção, só funciona corretamente em PDF's que o texto é selecionável!
    
    Args:
        path_pdf (str): caminho do pdf
        export_from_file_txt (bool | str): passar um caminho de arquivo txt para o texto sair

    Returns:
        str: texto do PDF
    """
    
    text = []
    
    # Abre o arquivo PDF com fitz
    doc = fitz.open(path_pdf)
    
    # Itera por cada página do documento
    for page in doc:
        # Extrai o texto da página
        text.append(page.get_text())
        
    # Converte a lista de textos em uma única string
    text = "\n".join(text)
    
    # Se um caminho para um arquivo de texto for fornecido, salva o texto extraído nesse arquivo
    if export_from_file_txt:
        with open(export_from_file_txt, 'w', encoding='utf-8') as f:
            f.write(text)
    
    # Retorna o texto extraído
    return text

def ocr_google_vision(pdf, api_key, dpi=300, file_output=uuid.uuid4(), return_text=True, limit_pages=None, is_image=False):
    def detect_text(files_png: list[str], api_key) -> str:
        """Recupera o texto das imagens

        Args:
            files_png (list[str]): Lista de imagens do pdf

        Raises:
            Exception: != de 200 a response

        Returns:
            str: O texto do PDF
        """
        url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
        requests_json = []
        result = ''
        contador = len(files_png)
        while contador != 0:  # enquanto existir imagens...
            faz_log(f'Recuperando 16 imagens de {contador} imagens | Se tiver 16 de fato, senão pega o resto')
            files_png_temp = files_png[:16]
            for filepath in files_png_temp:  # faz uma lista de requests para o post
                with open(filepath, mode='rb') as file:
                    bytes_content = file.read()
                    requests_json.append(
                        {
                            "image": {
                                "content": base64.b64encode(bytes_content).decode("utf-8")
                            },
                            "features": [{"type": "TEXT_DETECTION"}]
                        }
                    )
            else:
                for i in files_png_temp:
                    files_png.remove(i)
                    

                r = requests.post(url=url, json={"requests": requests_json})
                requests_json = []  # limpa para os proximos 10
                if r.status_code == 200:
                    # faz_log(r.text)
                    r_json = r.json()
                    for resp in r_json['responses']:
                        try:
                            result = result + str(resp['textAnnotations'][0]['description']).strip()
                        except Exception as e:
                            faz_log(repr(e))
                            raise Exception(repr(e))
                    else:
                        contador = len(files_png)
                else:
                    raise Exception(r.json()['error']['message'])

        return remover_acentos(result.lower().strip())
    
    if is_image == False:
        with fitz.open(pdf) as pdf_fitz:
            cria_dir_no_dir_de_trabalho_atual('pages')
            limpa_diretorio('pages')
            faz_log(f'Convertendo PDF para páginas...')
            number_of_pages = len(pdf_fitz) if limit_pages is None else min(limit_pages, len(pdf_fitz))
            with tqdm(total=number_of_pages, desc='EXTRACT PAGES') as bar:
                for i, page in enumerate(pdf_fitz):
                    if i >= number_of_pages:
                        break
                    page = pdf_fitz.load_page(i)
                    mat = fitz.Matrix(dpi/72, dpi/72)  # Matriz de transformação usando DPI
                    pix = page.get_pixmap(matrix=mat)
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    image.save(f'pages/{i}.png')
                    bar.update(1)
            
        faz_log('Enviando para Google Vision...')
        files = list(arquivos_com_caminho_absoluto_do_arquivo('pages'))
        text_ocr = detect_text(files, api_key)
        limpa_diretorio('pages')
        if return_text:
            return text_ocr
        else:
            file_path = arquivo_com_caminho_absoluto('tempdir', f'{file_output}.txt')
            with open(file_path, 'w') as f:
                text_ocr.write(f)
            return file_path
    else:
        files = [pdf]
        text_ocr = detect_text(files, api_key)
        if return_text:
            return text_ocr
        else:
            file_path = arquivo_com_caminho_absoluto('tempdir', f'{file_output}.txt')
            with open(file_path, 'w') as f:
                text_ocr.write(f)
            return file_path
    
    
    
def ocr_tesseract_v2(pdf, dpi=300, file_output=uuid.uuid4(), return_text=True, config_tesseract='', limit_pages=None, lang='por', timeout=120, path_tesseract='bin/Tesseract-OCR/tesseract.exe', path_pages='pages', tempdir='tempdir'):
    """Realiza OCR em um arquivo PDF usando Tesseract, com opções de customização avançadas.

    Esta função avançada permite a personalização de diversos parâmetros do OCR, como DPI, linguagem, limitação de páginas e timeout. Caso os binários do Tesseract não estejam presentes, ela executa uma única requisição para o GitHub da organização Paycon para baixar os binários necessários. Esta requisição é crucial para a funcionalidade da função mas levanta questões importantes sobre segurança de dados.

    Importância da Segurança dos Dados na Requisição:
        - Embora o arquivo ZIP do Tesseract seja público e hospedado em um repositório confiável, é fundamental validar a fonte antes do download para evitar a execução de software malicioso.
        - Durante o desenvolvimento, é aconselhável ter o Tesseract pré-instalado no projeto, eliminando a necessidade do download e reduzindo a superfície de ataque.
        - Para ambientes de produção, deve-se considerar a implementação de verificações de integridade, como a validação de checksum, para garantir a autenticidade dos binários baixados.

    Args:
        pdf (str): Caminho do arquivo PDF para realizar o OCR.
        dpi (int, optional): Resolução DPI para a conversão de páginas PDF em imagens. Padrão é 300.
        file_output (str, optional): Nome do arquivo de saída onde o texto OCR será salvo. Gera um UUID por padrão.
        return_text (bool, optional): Se True, retorna o texto extraído; se False, retorna o caminho para o arquivo de texto. 
            Padrão é True.
        config_tesseract (str, optional): Configurações adicionais para o Tesseract. Padrão é ''.
        limit_pages (int, optional): Limita o número de páginas do PDF a serem processadas. Padrão é None.
        lang (str, optional): Código de idioma usado pelo Tesseract para o OCR. Padrão é 'por' (português).
        timeout (int, optional): Timeout em segundos para o processamento OCR de cada página. Padrão é 120.

    Retorna:
        str|bool: Retorna o texto extraído ou o caminho para o arquivo de texto se `return_text` for False. 
            Retorna False em caso de falha no processamento OCR.

    Nota:
        - A função tenta baixar os binários do Tesseract apenas se estes não estiverem presentes, para evitar downloads desnecessários e mitigar riscos de segurança.
        - A segurança dos dados e a integridade do software são primordiais, especialmente ao realizar downloads de fontes externas.
        
    Raises:
        Exception: Pode lançar uma exceção se ocorrer um erro durante o download dos binários, o processamento OCR ou se a integridade do arquivo baixado for questionável.
    """
    path_tesseract = os.path.abspath(path_tesseract)

    if not os.path.exists(path_tesseract):
        while not os.path.exists(path_tesseract):
            faz_log('*** COLOQUE OS BINÁRIOS DO TESSERACT NA PASTA BIN (O NOME DA PASTA DOS BINÁRIOS DEVE SER "Tesseract-OCR") ***')
            sleep(10)
        else:
            pass
    pytesseract.pytesseract.tesseract_cmd = path_tesseract

    with fitz.open(pdf) as pdf_fitz:
        try:
            os.makedirs(path_pages)
        except FileExistsError:
            pass
        limpa_diretorio(path_pages, timeout_for_clear=1, max_tentativas=3)
        faz_log(f'Convertendo PDF para páginas...')
        number_of_pages = len(pdf_fitz) if limit_pages is None else min(limit_pages, len(pdf_fitz))
        with tqdm(total=number_of_pages, desc='EXTRACT PAGES') as bar:
            for i, page in enumerate(pdf_fitz):
                if i >= number_of_pages:
                    break
                page = pdf_fitz.load_page(i)
                mat = fitz.Matrix(dpi/72, dpi/72)  # Matriz de transformação usando DPI
                pix = page.get_pixmap(matrix=mat)
                pix.save(arquivo_com_caminho_absoluto(path_pages, f'{i}.png'))
                bar.update(1)
        

        files = arquivos_com_caminho_absoluto_do_arquivo(path_pages)
        with tqdm(total=len(files), desc='OCR') as bar:
            for i, image in enumerate(files):
                try:
                    text = pytesseract.image_to_string(image, config=config_tesseract, lang=lang, timeout=timeout)
                except Exception as e:
                    return False
                with open(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'), 'a', encoding='utf-8') as f:
                    f.write(text)
                bar.update(1)
            else:
                limpa_diretorio(path_pages, timeout_for_clear=1, max_tentativas=3)
                if return_text:
                    text_all = ''
                    with open(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'), 'r', encoding='utf-8') as f:
                        text_all = f.read()
                    os.remove(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'))
                    return text_all
                else:
                    return os.path.abspath(arquivo_com_caminho_absoluto(tempdir, f'{file_output}.txt'))