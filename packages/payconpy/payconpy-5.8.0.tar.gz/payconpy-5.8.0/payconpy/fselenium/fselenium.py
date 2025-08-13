import json
import os
from base64 import b64decode
from subprocess import getoutput
from time import sleep
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from payconpy.fpython.fpython import *
from payconpy.fregex.fregex import extrair_email
from payconpy.utils.utils import *
import pickle

def url_atual(driver) -> str:
    """
    ### Função RETORNA a url atual

    Args:
        driver (WebDriver): Seu Webdriver (Chrome, Firefox, Opera...)

    Returns:
        (str): URL atual da janela atual
    """
    return driver.current_url


def atualiza_page_atual(driver) -> None:
    """
    ### Função atualiza a página atual da janela atual

    Args:
        driver (WebDriver): Seu Webdriver (Chrome, Firefox, Opera...)
        
    """
    driver.refresh()

        
def espera_e_clica_em_varios_elementos(wdw:WebDriverWait, locator: tuple, in_dom=False) -> None:
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.presence_of_all_elements_located(locator))
    elements = driver.find_elements(*locator)
    len_elements = len(elements)

    for i in range(len_elements):
        elements[i].click()
        sleep(0.5)


def espera_elemento_disponivel_e_clica(wdw:WebDriverWait, locator: tuple, in_dom:bool=False) -> None:
    """Espera o elemento ficar disponível para clicar e clica

    Args:
        wdw (WebDriverWait): WebDriverWait
        locator (tuple): localização do elemento -> (By.CSS_SELECTOR, '.b')
    """
    if in_dom:
        return wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator)).click()


def espera_elemento(wdw:WebDriverWait, locator: tuple, in_dom:bool=False) -> WebElement:
    """
    ### Função que espera pelo elemento enviado do locator

    Args:
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A localização do elemento no DOM (By.CSS_SELECTOR, '#IdButton')
        in_dom (bool): Vai verificar se o elemento está no DOM
        
    """
    if in_dom:
        return wdw.until(EC.presence_of_element_located(locator))
    else:        
        return wdw.until(EC.element_to_be_clickable(locator))


def set_zoom_page(driver, zoom: int):
    """Seta o zoom da página atual

    Args:
        driver (WebDriver): WebDriver
        zoom (int): O zoom para setar.
    """
    driver.execute_script(f"document.body.style.zoom='{zoom}%'")


def espera_2_elementos(wdw:WebDriverWait, locator1: tuple, locator2 : tuple) -> WebElement:
    """
    ### Função que espera pelo elemento enviado do locator

    Args:
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A localização do elemento no DOM (By.CSS_SELECTOR, '#IdButton')
        
    """
    try:
        wdw.until(EC.element_to_be_clickable(locator1))
    except Exception:
        wdw.until(EC.element_to_be_clickable(locator2))


def espera_elemento_e_envia_send_keys(wdw:WebDriverWait, string, locator: tuple, in_dom=False) -> None:
    """
    ### Função que espera pelo elemento enviado do locator e envia o send_keys no input ou textarea assim que possível

    Args:
        driver (WebDriver): Seu Webdriver (Chrome, Firefox, Opera)
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A localização do elemento no DOM (By.CSS_SELECTOR, '#IdButton')
        
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))

    driver.find_element(*locator).send_keys(string)


def set_zoom_page(driver, zoom: int) -> None:
    """Seta o zoom da página atual

    Args:
        driver (WebDriver): WebDriver
        zoom (int): O zoom para setar.
    """
    driver.execute_script(f"document.body.style.zoom='{zoom}%'")
    
    
def espera_e_retorna_lista_de_elementos(wdw:WebDriverWait, locator: tuple, in_dom=False) -> list[WebElement]:
    """
    ### Função espera e retorna uma lista de elementos indicados no locator

    Args:
        driver (Webdriver): Seu Webdriver (Chrome, Opera, Firefox)
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A tupla indicando a localização do elemento no DOM ("BY_SELECTOR", "#list_arms").

    Returns:
        list: Lista com os elementos com o formato de Objetos (lista de Objetos)
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
    return driver.find_elements(*locator)


def download_de_arquivo_em_sharepoint(headless, pasta_de_download_e_print, url_file, email, passwd):
    """de uma forma bem grotesca fazendo um download de um arquivo compartilhado
    pode ser utilizado para arquivos que tem que ter o navegador aberto para fazer o download

    Args:
        headless (bool): executar como headless
        pasta_de_download_e_print (str): local de download
        pasta_de_download_e_print (url): url para dar get
        pasta_de_download_e_print (int|float): tempo para esperar na Thread atual
    """
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.wait import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
    import json
    import shutil
    
    # pasta de download como relativa, pois cria no dir de trabalho atual
    # --- CHROME OPTIONS --- #
    options = ChromeOptions()

    # --- PATH BASE DIR --- #
    if os.path.exists(pasta_de_download_e_print):
        shutil.rmtree(pasta_de_download_e_print)
        sleep(1)
        DOWNLOAD_DIR = cria_dir_no_dir_de_trabalho_atual(dir=pasta_de_download_e_print, print_value=False, criar_diretorio=True)
    else:        
        DOWNLOAD_DIR = cria_dir_no_dir_de_trabalho_atual(dir=pasta_de_download_e_print, print_value=False, criar_diretorio=True)

    SETTINGS_SAVE_AS_PDF = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local",
                "account": ""
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
    }

    PROFILE = {'printing.print_preview_sticky_settings.appState': json.dumps(SETTINGS_SAVE_AS_PDF),
                "savefile.default_directory":  f"{DOWNLOAD_DIR}",
                "download.default_directory":  f"{DOWNLOAD_DIR}",
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True}

    options.add_experimental_option('prefs', PROFILE)

    options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])
    if headless:
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-webgl")
        options.add_argument('--disable-gpu')
    options.add_argument('--kiosk-printing')
    options.add_argument("--start-maximized")

    service = Service(executable_path=ChromeDriverManager().install())

    DRIVER = Chrome(service=service, options=options)
    DRIVER.maximize_window()
    WDW = WebDriverWait(DRIVER, 5)
    try:
        DRIVER.get(url_file)
        
        faz_log(f'Enviando Usuário...')
        try:
            espera_elemento_e_envia_send_keys(DRIVER, WDW, email, (By.CSS_SELECTOR, '#i0116'))
        except TimeoutException:
            try:
                espera_elemento_e_envia_send_keys(DRIVER, WDW, email, (By.CSS_SELECTOR, 'input[data-report-event*="Signin_Email"]'))
            except TimeoutException:
                espera_elemento_e_envia_send_keys(DRIVER, WDW, email, (By.CSS_SELECTOR, 'input[name*="loginfmt"]'))

        # clica em Avançar
        try:
            espera_elemento_disponivel_e_clica(WDW, (By.CSS_SELECTOR, '#idSIButton9'))
        except TimeoutException:
            espera_elemento_disponivel_e_clica(WDW, (By.CSS_SELECTOR, 'input[data-report-event*="Submit"]'))

        # Envia _SENHA
        faz_log(f'Enviando Senha Elaw...')
        try:
            espera_elemento_disponivel_e_clica(WDW, (By.CSS_SELECTOR, 'div[role="button"]'))
        except TimeoutException:
            ...
        try:
            espera_elemento_e_envia_send_keys(DRIVER, WDW, passwd, (By.CSS_SELECTOR, '#i0118'))
        except TimeoutException:
            try:
                espera_elemento_e_envia_send_keys(DRIVER, WDW, passwd, (By.CSS_SELECTOR, 'input[type="password"]'))
            except TimeoutException:
                espera_elemento_e_envia_send_keys(DRIVER, WDW, passwd, (By.CSS_SELECTOR, 'input[data-bind*="password"]'))
        except StaleElementReferenceException:
            espera_elemento_e_envia_send_keys(DRIVER, WDW, passwd, (By.CSS_SELECTOR, '#i0118'))

        # clica em Entrar
        faz_log(f'Clicando em "Entrar"...')
        try:
            espera_elemento_disponivel_e_clica(WDW, (By.CSS_SELECTOR, '#idSIButton9'))
        except TimeoutException:
            espera_elemento_disponivel_e_clica(WDW, (By.CSS_SELECTOR, 'input[data-report-event*="Submit"]'))

        # clica em Sim
        faz_log(f'Clicando em "Sim"...')
        try:
            espera_elemento_disponivel_e_clica(WebDriverWait(DRIVER, 10), (By.CSS_SELECTOR, '#idSIButton9'))
        except TimeoutException:
            espera_elemento_disponivel_e_clica(WebDriverWait(DRIVER, 10), (By.CSS_SELECTOR, 'input[data-report-event*="Submit"]'))
            
        baixou = False
        while baixou == False:
            list_dir = os.listdir(pasta_de_download_e_print)
            if len(list_dir) >= 1:
                list_dir = os.listdir(pasta_de_download_e_print)
                for i in list_dir:
                    if '.crdownload' in i:
                        list_dir = os.listdir(pasta_de_download_e_print)
                        baixou = False
                    else:
                        list_dir = os.listdir(pasta_de_download_e_print)
                        baixou = True
            else:
                list_dir = os.listdir(pasta_de_download_e_print)
                baixou = False
    except TimeoutException:
        DRIVER.quit()
        download_de_arquivo_em_sharepoint(headless, pasta_de_download_e_print, url_file, email, passwd)
            

def download_de_arquivo_com_link_sem_ext_pdf(link: str, driver, back_to_page: bool=False):
    """Faz download do pdf com o link do href, ele entrará no pdf e dará print_page

    Args:
        link (str): link do arquivo que deseja baixar
        driver (WebDriver): Driver
        back_to_page (bool): Se deseja voltar para a page anterior. Optional, default is False

    Use:
        >>> link = espera_e_retorna_conteudo_do_atributo_do_elemento_text(DRIVER, WDW3, 'href', (By.CSS_SELECTOR, 'div>a'))
        >>> download_de_arquivo_com_link_sem_ext_pdf(link, mywebdriver, False)
    
    """
    driver.get(link)
    sleep(3)
    driver.print_page()
    if back_to_page:
        driver.back()
        driver.refresh()


def espera_e_retorna_lista_de_elementos_text_from_id(wdw:WebDriverWait, locator: tuple, in_dom=False) -> list[str]:
    """
    ### Função espera e retorna uma lista de elementos com id
    

    Args:
        driver (WebDriver): Seu Webdriver (Chrome, Firefox, Opera)
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A tupla indicando a localização do elemento no DOM ("BY_SELECTOR", "#list_arms").

    Returns:
        list: Lista de textos dos elementos com id -> [adv 1, adv 2, adv 3, adv 4, adv 5]
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))

    webelements = driver.find_elements(*locator)
    id = 1
    elementos_com_id = []
    for element in webelements:
        if element.text == ' ':
            elementos_com_id.append(element.text)
        else:
            elementos_com_id.append(f'{element.text} {id}')
        id += 1
    else:
        return elementos_com_id


def espera_e_retorna_lista_de_elementos_text(wdw:WebDriverWait, locator: tuple, in_dom=False, upper_mode :bool=False, strip_mode :bool=False) -> list[str]:
    """
    ### Função espera e retorna uma lista com os textos dos elementos

    Args:
        driver (Webdriver): Seu Webdriver (Chrome, Firefox, Opera)
        wdw (WebDriverWait): Seu WebDriverWait
        locator (tuple): A tupla indicando a localização do elemento no DOM ("BY_SELECTOR", "#list_arms").

    Returns:
        list: Lista dos textos dos elementos
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
    elements = driver.find_elements(*locator)
    if upper_mode:
        elements_not_upper = [element.text for element in elements]
        return [element.upper() for element in elements_not_upper]
    if strip_mode:
        elements_not_strip = [element.text for element in elements]
        return [element.strip() for element in elements_not_strip]
    return [element.text for element in driver.find_elements(*locator)]


def espera_elemento_ficar_visivel(wdw:WebDriverWait, locator: tuple) -> WebElement|None:
    """Espera elemento ficar visivel na tela

    Args:
        driver (WebDriver): Webdriver
        wdw (WebDriverWait): WDW
        locator (tuple): Locator

    Returns:
        WebElement|None: WebElement or None
    """
    driver = wdw._driver
    element = driver.find_element(*locator)
    return wdw.until(EC.visibility_of(element))


def baixa_pdf_via_base64_headless_only(wdw: WebDriver, file_pdf_with_extension: str='MyPDF.pdf', locator: tuple=(By.CSS_SELECTOR, 'html'), in_dom=False):
    """
    ## Funciona somente com headless!
    é necessário que o driver já esteja aberto, passando somente o locator que deseja converter para pdf
    
        creditos
        https://stackoverflow.com/questions/66682962/headless-chrome-webdriver-issue-after-printing-the-web-page
    Args:
        file_pdf_with_extension (str, optional): _description_. Defaults to 'MyPDF.pdf'.
        locator (tuple, optional): _description_. Defaults to (By.CSS_SELECTOR, 'html').

    Raises:
        ValueError: _description_
    """
    FILE_PDF = os.path.abspath(file_pdf_with_extension)
    driver = wdw._driver
    if in_dom:
        element = wdw.until(EC.presence_of_element_located(locator))
    else:
        element = driver.find_element(*locator)

    ActionChains(driver).click(element).click_and_hold().move_by_offset(0, 0).perform()

    element = driver.execute_cdp_cmd("Page.printToPDF", {"path": 'html-page.pdf', "format": 'A4'})
    # Importar apenas a função b64decode do módulo base64

    # Defina a string Base64 do arquivo PDF
    b64 = element['data']

    # Decode the Base64 string, making sure that it contains only valid characters
    bytes = b64decode(b64, validate=True)

    # Execute uma validação básica para garantir que o resultado seja um arquivo PDF válido
    # Estar ciente! O número mágico (assinatura do arquivo) não é uma solução 100% confiável para validar arquivos PDF
    #Além disso, se você obtiver Base64 de uma fonte não confiável, deverá higienizar o conteúdo do PDF
    if bytes[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')

    # Write the PDF contents to a local file
    try:
        with open(FILE_PDF, 'wb') as f:
            f.write(bytes)
    except FileNotFoundError:
        cria_o_ultimo_diretorio_do_arquivo(FILE_PDF)
        with open(FILE_PDF, 'wb') as f:
            f.write(bytes)


def verifica_conexao_vpn(ping_host :str):
    """O método verificará por ping se está conectado no ip da VPN"""
    PING_HOST = ping_host

    faz_log('Verificando se VPN está ativa pelo IP enviado no config.ini')
    
    output = getoutput(f'ping {PING_HOST} -n 1')  # -n 1 limita a saída
    if 'Esgotado o tempo' in output or 'time out' in output:
        faz_log('VPN NÃO CONECTADA!', 'w')
    else:
        faz_log("VPN conectada com sucesso!")


def espera_elemento_ficar_visivel_ativo_e_clicavel(wdw:WebDriverWait, locator: tuple, in_dom=False) -> WebElement|None:
    """Espera Elemento ficar visivel, ativo e clicavel

    Args:
        driver (Webdriver): Webdriver
        wdw (WDW): WDW
        locator (tuple): Locator Selenium

    Returns:
        WebElement|None: _description_
    """
    driver = wdw._driver
    element = driver.find_element(*locator)
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
    return wdw.until(EC.visibility_of(element))


def espera_e_retorna_conteudo_do_atributo_do_elemento_text(wdw:WebDriverWait, atributo, locator: tuple, in_dom=False) -> str:
    """
    ### Função que espera pelo elemento e retorna o texto do atributo do elemento escolhido

    Args:
        driver (Webdriver): Seu Webdriver (Chrome, Firefox)
        wdw (WebDriverWait): Seu WebDriverWait
        atributo (str): O atributo que deseja recuperar, como um href, id, class, entre outros
        locator (tuple): A localização do elemento no DOM ("By.CSS_SELECTOR", "body > div > a").

    Returns:
        str: retorna uma string com o valor do atributo do elemento
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
        
    return driver.find_element(*locator).get_attribute(atributo)


def espera_e_retorna_conteudo_dos_atributos_dos_elementos_text(wdw:WebDriverWait, atributo, locator: tuple, in_dom=False) -> list:
    """
    ### Função espera e retorna o valor dos atributos de vários elementos

    Args:
        driver (Webdriver): Seu Webdriver (Chrome, Firefox)
        wdw (WebDriverWait): Seu WebDriverWait
        atributo (str): Atributo (esse deve existir em todos os elementos)
        locator (tuple): Posição dos elementos no DOM.("By.CSS_SELECTOR", "#list_works").

    Returns:
        list: Lista com os atributos de todos os elementos (é necessário que o atibuto enviado exista em todos os elementos como um href)
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))

    atributos = driver.find_elements(*locator)
    elementos_atributos = [atributo_selen.get_attribute(atributo) for atributo_selen in atributos]
    return elementos_atributos
        

def espera_e_retorna_elemento_text(wdw:WebDriverWait, locator: tuple, in_dom=False) -> str:
    """Função espera o elemento e retorna o seu texto

    Args:
        driver (Webdriver): Webdriver (Chrome, Firefox)
        wdw (WebDriverWait): WebDriverWait
        locator (tuple): Localização do elemento no DOM. ("By.CSS_SELECTOR", "#name")

    Returns:
        str: Retorna a string de um elemento
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
    return driver.find_element(*locator).text
    
    
def vai_para_a_primeira_janela(driver) -> None:
    """Vai para a primeira janela, geralmente a primeira que é iniciada

    Args:
        driver (WebDriver): WebDriver
    """
    window_ids = driver.window_handles # ids de todas as janelas
    driver.switch_to.window(window_ids[0])
    
    
def espera_abrir_n_de_janelas_e_muda_para_a_ultima_janela(wdw:WebDriverWait, num_de_janelas: int=2) -> None:
    """Função espera abrir o numero de janelas enviada por ti, e quando percebe que abriu, muda para a última janela aberta

    Args:
        driver (Webdriver): Webdriver (Chrome, Firefox)
        wdw (WebDriverWait): WebDriver
        num_de_janelas (int): Quantidade de janelas esperadas para abrie. O padrão é 2.
    """
    driver = wdw._driver
    try:
        wdw.until(EC.number_of_windows_to_be(num_de_janelas))
        return True
    except TimeoutException:
        return False
    
    
def procura_pela_janela_que_contenha_no_titulo(driver, title_contain_switch : str) -> None: # quero que pelo menos um pedaco do titulo que seja str
    """
    ### Essa função muda de janela quando o título tiver pelo menos algo igual ao parametro enviado
    #### Ex -> Minha janela = janela
    
    Args:
        driver (Webdriver): Webdriver (Chrome, Firefox)
        title_contain_switch (str) : Pelo menos um pedaco do titulo exista para mudar para a página 
    """
    window_ids = driver.window_handles # ids de todas as janelas

    for window in window_ids:
        driver.switch_to_window(window)  
        if title_contain_switch in driver.title:
            break
    else:
        print(f'Janela não encontrada!\n'
            f'Verifique o valor enviado {title_contain_switch}')
    
    
def fecha_janela_atual(driver) -> None:
    """
    ### Função que fecha a janela atual

    Args:
        driver (WebDriver): Seu WebDriver (Chrome, Firefox)
    """
    driver.close()


def fecha_ultima_janela(driver) -> None:
    qtd_de_windows = driver.window_handles
    while len(qtd_de_windows) !=2:
        qtd_de_windows = driver.window_handles
    else:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])


def espera_enquanto_nao_tem_resposta_do_site(wdw:WebDriverWait, locator : tuple) -> None:
    """
    ### Função que espera enquanto o site não tem resposta
    
    #### ESSA FUNÇÃO SÓ DEVE SER USADA CASO VOCÊ TENHA CERTEZA QUE O SITE POSSA VIR A CAIR

    Args:
        driver (WebDriver): Seu WebDriver (Chrome, Firefox)
        wdw (WebDriverWait): WebDriverWait
        locator (tuple): Localização do elemento no DOM. ("By.CSS_SELECTOR", "#ElementQueSempreEstaPresente")
    """
    driver = wdw._driver
    try:
        element = wdw.until(EC.element_to_be_clickable(locator))
        if element:
            return element
    except TimeoutException:
        print('Talvez a página tenha dado algum erro, vou atualiza-lá')
        sleep(2)
        try:
            driver.refresh()
            element = wdw.until(EC.element_to_be_clickable(locator))
            if element:
                print('Voltou!')
                return element
        except TimeoutException:
            print('A página ainda não voltou, vou atualiza-lá')
            sleep(2)
            try:
                driver.refresh()
                element = wdw.until(EC.element_to_be_clickable(locator))
                if element:
                    print('Voltou!')
                    return element
            except TimeoutException:
                print('Poxa, essa será a última vez que vou atualizar a página...')
                sleep(2)
                try:
                    driver.refresh()
                    element = wdw.until(EC.element_to_be_clickable(locator))
                    if element:
                        print('Voltou!')
                        return element
                except TimeoutException:
                    print("Olha, não foi possível. A página provavelmente caiu feio :(")
                    print("Infelizmente o programa vai ser finalizado...")
                    driver.quit()


def volta_paginas(driver, qtd_pages_para_voltar : int=1, espera_ao_mudar=0) -> None:
    """
    ### Essa função volta (back) quantas páginas você desejar

    Args:
        driver (WebDriver): Seu webdriver
        qtd_pages_para_voltar (int): Quantidade de páginas que serão voltadas. O padrão é uma página (1).
        espera_ao_mudar (int or float, optional): Se você quer esperar um tempo para voltar uma página. O padrão é 0.
        
    Uso:
        volta_paginas(driver=chrome, qtd_pages_para_voltar=3, espera_ao_mudar=1)
    """
    if espera_ao_mudar == 0:
        for back in range(qtd_pages_para_voltar):
            driver.back()
            driver.refresh()
    else:
        for back in range(qtd_pages_para_voltar):
            sleep(espera_ao_mudar)
            driver.back()
            driver.refresh()


def cria_user_agent() -> str:
    """Cria um user-agent automaticamente com a biblio fake_useragent

    Returns:
        str: user_agent
    """
    from random import choice
    user_agent = choice(USER_AGENTS)
    return user_agent


def espera_input_limpa_e_envia_send_keys_preessiona_esc(wdw:WebDriverWait, keys : str, locator : tuple, in_dom=False) -> None:
    from selenium.common.exceptions import StaleElementReferenceException
    from selenium.webdriver.common.keys import Keys

    """
    ### Função espera pelo input ou textarea indicado pelo locator, limpa ele e envia os dados

    Args:
        driver (WebDriver): Seu webdriver
        wdw (WebDriverWait): WebDriverWait criado em seu código
        keys (str): Sua string para enviar no input ou textarea
        locator (tuple): Tupla que contém a forma e o caminho do elemento (By.CSS_SELECTOR, '#myelementid')
    """
    driver = wdw._driver
    try:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
        driver.find_element(*locator).click()
        driver.find_element(*locator).send_keys(Keys.ESCAPE)
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)
    except StaleElementReferenceException:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
        driver.find_element(*locator).click()
        driver.find_element(*locator).send_keys(Keys.ESCAPE)
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)

    
def espera_input_limpa_e_envia_send_keys(wdw:WebDriverWait, keys : str, locator : tuple, click: bool=True, in_dom=False) -> None:
    from selenium.common.exceptions import StaleElementReferenceException
    """
    ### Função espera pelo input ou textarea indicado pelo locator, limpa ele e envia os dados

    Args:
        driver (WebDriver): Seu webdriver
        wdw (WebDriverWait): WebDriverWait criado em seu código
        keys (str): Sua string para enviar no input ou textarea
        locator (tuple): Tupla que contém a forma e o caminho do elemento (By.CSS_SELECTOR, '#myelementid')
        click (bool): Clica ou não no elemento
    """
    driver = wdw._driver
    try:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
        if click:
            driver.find_element(*locator).click()
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)
    except StaleElementReferenceException:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
        if click:
            driver.find_element(*locator).click()
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)

        
def espera_elemento_sair_do_dom(wdw:WebDriverWait, locator) -> WebElement:
    return wdw.until_not(EC.presence_of_element_located(locator))


def espera_elemento_ficar_ativo_e_clica(wdw:WebDriverWait, locator : tuple, in_dom=False) -> None:
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until_not(EC.element_to_be_selected(driver.find_element(*locator)))

    driver.find_element(*locator).click()
        
        
def espera_elemento_nao_estar_mais_visivel(wdw:WebDriverWait, locator) -> WebElement:
    return wdw.until_not(EC.visibility_of(*locator))


def espera_elemento_estar_visivel(wdw:WebDriverWait, locator, with_visibility_of: bool=True):
    driver = wdw._driver
    if with_visibility_of:
        element = driver.find_element(*locator)
        return wdw.until(EC.visibility_of(element))
    else:
        element = driver.find_element(*locator)
        return wdw.until(EC.element_to_be_clickable(locator))
        

def find_window_to_title_contain(driver, title_contain_switch: str) -> None: # quero que pelo menos um pedaco do titulo que seja str
    """
    ### Essa função muda de janela quando o título tiver pelo menos algo igual ao parametro enviado
    #### Ex -> Minha janela = janela
    
    para cada janela em ids das janelas
    muda para a janela
    se a janela for ao menos de um pedaço do titulo que passei
        em title_contain_switch
    para de executar
    """
    window_ids = driver.window_handles # ids de todas as janelas

    for window in window_ids:
        driver.switch_to_window(window)  
        if title_contain_switch in driver.title:
            break
    else:
        print(f'Janela não encontrada!\n'
              f'Verifique o valor enviado {title_contain_switch}')
    
    
def find_window_to_url(driver, url_switch: str) -> None: # quero uma url que seja str
    """
    ### Essa função muda de janela quando a url for igual ao parametro enviado
    #### Ex -> https://google.com.br  = https://google.com.br
    
    para cada janela em ids das janelas
    muda para a janela
    se a janela for do titulo que passei
        em title_switch
    para de executar
    """
    window_ids = driver.window_handles # ids de todas as janelas

    for window in window_ids:
        driver.switch_to_window(window)
        if driver.current_url == url_switch:
            break
        else:
            print(f'Janela não encontrada!\n'
                f'Verifique o valor enviado "{url_switch}"')
    

def find_window_to_url_contain(driver, contain_url_switch: str) -> None: # quero uma url que seja str
    """
    ### Essa função muda de janela quando a url conter no parametro enviado
    #### Ex -> https://google.com.br  = google
    
    para cada janela em ids das janelas
    muda para a janela
    se a janela for do titulo que passei
        em title_switch
    para de executar
    """
    window_ids = driver.window_handles # ids de todas as janelas

    for window in window_ids:
        driver.switch_to.window(window)
        if contain_url_switch in driver.current_url:
            break
        else:
            print(f'Janela não encontrada!\n'
                f'Verifique o valor enviado "{contain_url_switch}"')

        
def pega_codigo_fonte_de_elemento(wdw:WebDriverWait, locator: tuple, in_dom=False) -> str:
    """Retorna todo o código fonte do locator

    Args:
        driver (WebDriver): Webdriver
        wdw (WebDriverWait): WebDriverWait
        locator (tuple): localização do elemento no modo locator -> (By.ID, '.b')

    Returns:
        str: Código fonte do WebElement
    """
    driver = wdw._driver
    if in_dom:
        wdw.until(EC.presence_of_element_located(locator))
    else:
        wdw.until(EC.element_to_be_clickable(locator))
    element = driver.find_element(*locator)
    return element.get_attribute("outerHTML")


def verifica_se_diminuiu_qtd_de_janelas(driver, qtd_de_w) -> None:
    if len(driver.window_handles) == qtd_de_w:
        while len(driver.window_handles) >= qtd_de_w:
            ...
        else:
            window_ids = driver.window_handles # ids de todas as janelas
            driver.switch_to.window(window_ids[1])  # vai para a ultima window
            driver.close()
    else:
        verifica_se_diminuiu_qtd_de_janelas(driver, qtd_de_w)


def find_window_to_url_contain_and_close_window(driver, contain_url_to_switch: str) -> None: # quero uma url que seja str
    """
    ### Essa função muda de janela quando a url conter no parametro enviado
    #### Ex -> https://google.com.br  = google
    
    para cada janela em ids das janelas
    muda para a janela
    se a janela for do titulo que passei
        em title_switch
    para de executar
    """
    window_ids = driver.window_handles # ids de todas as janelas

    for window in window_ids:
        driver.switch_to.window(window)
        if contain_url_to_switch in driver.current_url:
            driver.close()
            break


def espera_input_limpa_e_envia_send_keys_preessiona_esc_tmb_no_final(wdw:WebDriverWait, keys : str, locator : tuple):
    """
    ### Função espera pelo input ou textarea indicado pelo locator, limpa ele e envia os dados

    Args:
        driver (Webdriver): Seu webdriver
        wdw (WebDriverWait): WebDriverWait criado em seu código
        keys (str): Sua string para enviar no input ou textarea
        locator (tuple): Tupla que contém a forma e o caminho do elemento (By.CSS_SELECTOR, '#myelementid')
    """
    driver = wdw._driver
    try:
        wdw.until(EC.element_to_be_clickable(locator))
        driver.find_element(*locator).click()
        driver.find_element(*locator).send_keys(Keys.ESCAPE)
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)
        driver.find_element(*locator).send_keys(Keys.ESCAPE)
    except StaleElementReferenceException:
        wdw.until(EC.element_to_be_clickable(locator))
        driver.find_element(*locator).click()
        driver.find_element(*locator).send_keys(Keys.ESCAPE)
        driver.find_element(*locator).clear()
        driver.find_element(*locator).send_keys(keys)
        driver.find_element(*locator).send_keys(Keys.ESCAPE)


def recupera_text_de_todo_um_site(url:str, tag_name:str='body', no_escape_sequence:bool=True, sleep_request:int=0) -> str:
    """Recupera o texto de um site, a partir da tag_name enviada
    
    Args:
        url (str): url
        tag_name (str, optional): tag_name. Defaults to 'body'.
        no_escape_sequence (bool, optional): remove ou não \\n da página. Defaults to True.

    Returns:
        str: texto do site ou do elemento
    """
    from bs4 import BeautifulSoup
    import requests
    r = requests.get(url)
    sleep(sleep_request)
    soup = BeautifulSoup(r.content, 'html5lib')
    if no_escape_sequence:
        return soup.find(tag_name).text.replace('\n', '').replace(u'\xa0', u' ')
    else:
        return soup.find(tag_name).text.replace(u'\xa0', u' ')

def espera_input_limpa_e_envia_send_keys_action_chains(wdw:WebDriverWait, keys : str, locator : tuple, in_dom=False) -> None:
    from selenium.common.exceptions import StaleElementReferenceException
    """
    ### Função espera pelo input ou textarea indicado pelo locator, limpa ele e envia os dados

    Args:
        driver (WebDriver): Seu webdriver
        wdw (WebDriverWait): WebDriverWait criado em seu código
        keys (str): Sua string para enviar no input ou textarea
        locator (tuple): Tupla que contém a forma e o caminho do elemento (By.CSS_SELECTOR, '#myelementid')
        click (bool): Clica ou não no elemento
    """
    driver = wdw._driver
    try:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
            
        element = driver.find_element(*locator)
        ActionChains(driver).click(element).perform()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        for char in keys:
            element.send_keys(char)
    except StaleElementReferenceException:
        if in_dom:
            wdw.until(EC.presence_of_element_located(locator))
        else:
            wdw.until(EC.element_to_be_clickable(locator))
        ActionChains(driver).click(element).perform()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        for char in keys:
            element.send_keys(char)


def imprime_iframe(driver):
    """
    Imprime o ID e o nome do iframe atual, se houver, utilizando o driver Selenium.

    ### Args:
    - driver: O objeto do Selenium WebDriver que está sendo utilizado para interagir com a página.

    ### Retorna:
    Nenhum valor é retornado.

    ### Exemplo de uso:
    ```python
    from selenium import webdriver

    driver = webdriver.Chrome()
    driver.get("https://exemplo.com")
    imprime_iframe(driver)
    ```
    """
    iframe_id = driver.execute_script("return window.frameElement ? window.frameElement.id : '';")
    iframe_name = driver.execute_script("return window.frameElement ? window.frameElement.name : '';")

    faz_log(f"ID do iframe atual: {iframe_id}")
    faz_log(f"Nome do iframe atual: {iframe_name}")
    return


def verifica_se_baixou_o_arquivo(diretorio_de_download: str, palavra_chave: str, sleep_time: int = 0, return_file: bool = False, verify_big_file: bool = False, timeout: int = 30, verify_if_element_exists: bool|dict = False) -> bool|str:
    """
    Verifica se um arquivo com uma palavra-chave foi baixado para um diretório especificado e retorna o último arquivo baixado. 
    Além disso, pode verificar se um elemento desapareceu do DOM antes de iniciar a verificação de download.

    Args:
        diretorio_de_download (str): O caminho para o diretório de download.
        palavra_chave (str): A palavra-chave a ser procurada nos nomes dos arquivos baixados (usa-se regex), ".pdf|.jpg".
        sleep_time (int, opcional): O tempo a ser aguardado antes de verificar novamente o diretório de download. Padrão é 0.
        return_file (bool, opcional): Se deve ou não retornar o caminho do arquivo baixado. Padrão é False.
        verify_big_file (bool, opcional): Se deve ou não verificar arquivos com nomes longos. Padrão é False.
        timeout (int, opcional): O tempo máximo para esperar o arquivo ser baixado, em segundos. Padrão é 30.
        verify_if_element_exists (bool|dict, opcional): Se deve ou não verificar se um elemento específico desapareceu do DOM
            antes de iniciar a verificação do arquivo. Se for um dicionário, deve conter:
            - 'WDW' (WebDriverWait): A instância de espera explícita.
            - 'SELECTOR' (tuple): Seletores do elemento a ser aguardado no DOM (por exemplo, (By.CSS_SELECTOR, '#Elemento')).
            Padrão é False, que significa que não verifica se o elemento desapareceu.

    Returns:
        bool|str: Retorna True se o arquivo for baixado com sucesso, False caso contrário. Se return_file for True,
                    retorna o caminho absoluto do último arquivo baixado.
    """
    
    if verify_if_element_exists:
        espera_elemento_sair_do_dom(verify_if_element_exists['WDW'], verify_if_element_exists['SELECTOR'])

    _LOCAL_DE_DOWNLOAD = os.path.abspath(diretorio_de_download)
    baixou = False
    start_time = time.time()
    ultimo_arquivo = None
    while not baixou:
        current_time = time.time()
        if current_time - start_time > timeout:
            return False
        lista_arquivos = os.listdir(_LOCAL_DE_DOWNLOAD)
        if verify_big_file:
            lista_arquivos = [suporte_para_paths_grandes(x).lower() for x in lista_arquivos]
        else:
            lista_arquivos = [x.lower() for x in lista_arquivos]
        
        if len(lista_arquivos) == 0:
            sleep(sleep_time)
            baixou = False
        else:
            for i in lista_arquivos:
                if 'crdownload' in i.lower():
                    sleep(sleep_time)
                    baixou = False
                    continue
                if re.search(palavra_chave, i) is not None:
                    ultimo_arquivo = i
                    baixou = True
                    print('Download concluído!')
                    break
            
            if baixou:
                if return_file:
                    return os.path.join(_LOCAL_DE_DOWNLOAD, ultimo_arquivo)
                else:
                    return True
            else:
                sleep(sleep_time)
                
                
def retorna_lista_de_elementos_independente_da_quantidade_de_iframes(WDW: WebDriverWait, locator: tuple) -> list:
    """
    Retorna uma lista de WebElements, independentemente do número de iframes no DOM. A função busca os elementos
    no contexto principal e dentro de todos os iframes presentes na página.

    Args:
        WDW (WebDriverWait): A instância de WebDriverWait para controle de tempo de espera explícito.
        locator (tuple): Um localizador Selenium (por exemplo, (By.CSS_SELECTOR, '#meu_elemento')).

    Returns:
        list: Uma lista de WebElements encontrados. Se nenhum elemento for encontrado, retorna uma lista vazia.

    Usage:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait

        driver = webdriver.Chrome()
        driver.get('URL_DO_SEU_SITE')

        wait = WebDriverWait(driver, 10)
        locator = (By.CSS_SELECTOR, 'SELETOR_DO_SEU_ELEMENTO')

        elements = retorna_webelements_independente_da_quantidade_de_iframes(wait, locator)
        for element in elements:
            print(element.text)

        driver.quit()
    """

    def find_elements_in_iframes(driver, locator):
        elements = []
        try:
            elements = driver.find_elements(*locator)
            if elements:
                return elements
        except NoSuchElementException:
            pass
        
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            elements = find_elements_in_iframes(driver, locator)
            if elements:
                return elements
            driver.switch_to.default_content()
        
        return elements

    driver = WDW._driver
    try:
        elements = find_elements_in_iframes(driver, locator)
        if not elements:
            WDW.until(EC.presence_of_element_located(locator))
            elements = driver.find_elements(*locator)
        return elements
    except TimeoutException:
        return []


def salvar_cookies(driver, arquivo_cookies: str = 'cookies.pkl') -> str:
    """
    Salva os cookies do navegador em um arquivo para reutilização futura.

    Args:
        driver (WebDriver): Instância do WebDriver que contém os cookies a serem salvos.
        arquivo_cookies (str, opcional): O nome do arquivo onde os cookies serão salvos. O padrão é 'cookies.pkl'.

    Returns:
        str: Retorna o nome do arquivo onde os cookies foram salvos.

    Usage:
        from selenium import webdriver

        driver = webdriver.Chrome()
        driver.get('https://www.seusite.com')  ## O driver deve ter navegado para o site antes de salvar os cookies
        
        # Após login ou navegação
        salvar_cookies(driver, 'meus_cookies.pkl')
    """
    with open(arquivo_cookies, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)
    return arquivo_cookies


def carregar_cookies(driver, arquivo_cookies: str = 'cookies.pkl') -> bool:
    """
    Carrega os cookies de um arquivo e os adiciona ao WebDriver.

    Args:
        driver (WebDriver): Instância do WebDriver para o qual os cookies serão carregados.
        arquivo_cookies (str, opcional): O nome do arquivo de onde os cookies serão carregados. O padrão é 'cookies.pkl'.

    Returns:
        bool: Retorna True se os cookies foram carregados com sucesso, False se o arquivo de cookies não foi encontrado.

    Usage:
        from selenium import webdriver

        driver = webdriver.Chrome()
        driver.get('https://www.seusite.com')  ## O driver deve ter navegado para o site antes de carregar os cookies
        
        if carregar_cookies(driver, 'meus_cookies.pkl'):
            driver.refresh()  # Recarrega a página com os cookies carregados
        else:
            print("Necessário fazer login manualmente.")
    """
    try:
        with open(arquivo_cookies, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("Cookies carregados com sucesso.")
        return True
    except FileNotFoundError:
        print("Arquivo de cookies não encontrado. Será necessário fazer login manualmente.")
        return False
