import pandas as pd
import requests
from payconpy.fpython.fpython import faz_log, cria_dir_no_dir_de_trabalho_atual, arquivo_com_caminho_absoluto
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def download_document(link, filename):
    """Download de arquivos que vem pelo link por exemplo:
    https://atacadoinformacaojudicial.com.br/documentos_iniciais_novo/123121231231/12312123123132123.pdf

    ### Especifique a extensão do arquivo que deseja baixar

    Args:
        link (str): Link do documento
        filename (str): Nome do arquivo (incluindo a extensão)
        
    Usage:
    >>>    link = 'https://atacadoinformacaojudicial.com.br/documentos_iniciais_novo/123121231231/12312123123132123.pdf'
    >>>    download_document(link, '12312123123132123.pdf')
    >>>    download_document(link, 'output/12312123123132123.pdf')
    """
    try:
        response = requests.get(link, verify=False)
        with open(os.path.abspath(filename), 'wb') as file:
            file.write(response.content)
        faz_log(f'Arquivo salvo com sucesso.')
    except requests.exceptions.RequestException as e:
        faz_log(f'Falha ao baixar o arquivo {filename}: {e}')


def exportar_tabela_para_usuario(path_db, dir_result='Resultado', table_name='table', dict_rename_columns={}, remove_columns=['id'], filename='Resultado'):
    """Exporta uma tabela de um banco de dados para um arquivo Excel.

    A função se conecta a um banco de dados, lê uma tabela específica e exporta 
    essa tabela para um arquivo Excel, excluindo a coluna 'id' e renomeando 
    outras colunas conforme especificado. Se a exportação falhar (por exemplo, 
    se o arquivo Excel estiver aberto), um log de erro será criado.

    Use:
        >>> export_table_for_user(path_db='sqlite:///mydb.db', dir_result='Resultado', table_name='minha_tabela', dict_rename_columns={'old_name': 'new_name'}, remove_columns=['id', 'other_column'])
        Tenta exportar a tabela 'minha_tabela' do banco de dados 'mydb.db' para um arquivo Excel,
        renomeando colunas conforme o dicionário fornecido.

    Args:
        path_db (str): O caminho do banco de dados a ser conectado.
        dir_result (str, optional): O nome do diretório onde o arquivo Excel será salvo. 
            Padrão é 'Resultado'.
        table_name (str, optional): O nome da tabela no banco de dados que será exportada. 
            Padrão é 'table'.
        dict_rename_columns (dict, optional): Um dicionário para renomear colunas, onde as chaves 
            são os nomes originais das colunas e os valores são os novos nomes. Padrão é um dicionário vazio.
        remove_columns (list, optional): Uma lista para remover colunas. Padrão é uma lista apenas com 'id'.
        filename (str, optional): Nome do arquivo que quer salvar. Padrão é 'Resultado'.

    Returns:
        None: A função não retorna nenhum valor. O resultado é um arquivo Excel exportado ou 
            um log de erro se a exportação falhar.

    Raises:
        Exception: Se ocorrer um erro durante a exportação, o erro será logado e a execução 
            da função será interrompida.
    """

    faz_log('Fazendo tabela resultado...')
    engine = create_engine(path_db)  # cria a conexão
    engine.connect() # conecta com o banco de dados
    df = pd.read_sql_table(table_name, engine.connect()) # cria o dataframe
    cria_dir_no_dir_de_trabalho_atual(dir_result)

    for col in remove_columns:
        try:
            del df[col]
        except Exception as e:
            pass
    df.rename(columns=dict_rename_columns, inplace=True)

    try:
        # Remove qualquer caractere inválido --------------------------------------------------------|
        df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in df.items() ]))                         #|
        cria_dir_no_dir_de_trabalho_atual(dir_result)                                              #|
        df.to_excel(f'{dir_result}\\{filename}.xlsx', 'Saída', index=False, engine='xlsxwriter')         #|
        faz_log('Exportada com sucesso!', color='green')
    except Exception as e:
        faz_log(repr(e), 'c*')
        faz_log('Muito provavelmente a tabela está aberta, tentaremos novamente na próxima execução', color='red')


def return_dataframe_from_column(file_, coluna, range_lines=10, sheet_name=0, dtype=None) -> pd.DataFrame:
    """Retorna um DataFrame baseado em uma coluna específica de um arquivo Excel.

    Esta função lê um arquivo Excel e tenta encontrar uma coluna específica 
    dentro de um determinado intervalo de linhas. Se a coluna for encontrada, 
    ela retorna o DataFrame completo com o cabeçalho definido para a linha 
    onde a coluna foi encontrada. Caso contrário, ele registra um erro e 
    retorna False.

    Use:
        >>> return_dataframe_from_column('example.xlsx', 'Nome da Coluna', range_lines=10)
        Se a coluna for encontrada dentro do intervalo de linhas especificado, retorna o DataFrame;
        caso contrário, retorna False.
    
    Args:
        file_ (str): O caminho do arquivo Excel.
        coluna (str): O nome da coluna a ser procurada no arquivo Excel.
        range_lines (int, optional): O número de linhas para procurar a coluna desejada.
            Padrão é 10.
        sheet_name (int, str, optional): Nome ou índice da planilha a ser lida. Padrão é 0.
        
    Returns:
        pd.DataFrame: Retorna um DataFrame se a coluna for encontrada dentro do 
            range_lines especificado. 
        False: Retorna False se a coluna não for encontrada dentro do range_lines 
            especificado ou se algum erro ocorrer durante a leitura do arquivo.

    Raises:
        Exception: Se ocorrer um erro durante a leitura do arquivo Excel, exceto
            se o cabeçalho não for encontrado dentro do range_lines especificado.
    """

    file_ = os.path.abspath(file_)
    linha = 0
    df = pd.read_excel(file_, header=linha, sheet_name=sheet_name, dtype=dtype)
    while True:
        if linha > range_lines:
            faz_log('Não foi possível encontrar a coluna, tente com um range_lines maior, ou verifique o nome da coluna enviado')
            return False
        colunas = df.columns.to_list()
        if not coluna in colunas:
            print(f'Não foi encontrada a coluna na linha {linha}')
            try:
                df = pd.read_excel(file_, header=linha, sheet_name=sheet_name, dtype=dtype)
            except:
                pass
            linha += 1
        else:
            print('Foi encontrado a coluna...')
            return df

def cria_diretorios_para_novo_projeto_python(create_base_dir:bool=True, packages:str='payconpy'):
    """
    # ATENÇÃO, UTILIZAR SOMENTE UMA VEZ NO MOMENTO DA CRIAÇÃO DO NOVO PROJETO!
    
    ## A 
    
    create_base_dir: cria o diretorio para o user colocar a base
    packages: instala pacotes necessários
    """
    faz_log('Criando pasta e arquivo de logs com esse log...')
    # cria diretório src
    cria_dir_no_dir_de_trabalho_atual('src')
    APP_PATH = arquivo_com_caminho_absoluto(['src', 'app'], 'app.py')
    BASE_PATH = arquivo_com_caminho_absoluto(['src', 'base'], 'base.py')
    DATABASE_PATH = arquivo_com_caminho_absoluto(['src', 'database'], 'database.py')
    EXCEPTIONS_PATH = arquivo_com_caminho_absoluto(['src', 'exceptions'], 'exceptioins.py')
    CONFIG_PATH = arquivo_com_caminho_absoluto(['bin'], 'config.json')
    UTILS_PATH = arquivo_com_caminho_absoluto(['src', 'utils'], 'utils.py')
    TESTS_PATH = arquivo_com_caminho_absoluto(['src', 'tests'], 'tests.py')
    GITIGNORE_PATH = '.gitignore'
    # cria subdiretorios do src

        # CRIA ARQUIVO PYTHON EM SRC\\APP
    with open(APP_PATH, 'w', encoding='utf-8') as f:
        f.write("""from src.base.base import *
class RobotClass(Bot):
    def __init__(self) -> None:
        self.configs = read_json(CONFIG_PATH)  # get configs from bin/config.json
        self.HEADLESS = self.configs['BOT']['HEADLESS']  # default is False
        self.DOWNLOAD_FILES = False  # Not add chromeoption (--kiosk-printing) for download files
        super().__init__(self.HEADLESS, self.DOWNLOAD_FILES, rotate_user_agent=False)  # inherit from Bot class

    def run(self):
        self.DRIVER.get("https://google.com.br")  # here, use selenium for get
        
    """)


    # CRIA ARQUIVO PYTHON EM base
    with open(BASE_PATH, 'w', encoding='utf-8') as f:
        f.write("""from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from mywebdriver.chrome.chromedriver import ChromeDriverDownloader
from payconpy.fpython.fpython import *
from payconpy.fselenium.fselenium import *
from payconpy.fregex.fregex import *
import pandas as pd
import json
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# -- GLOBAL -- #
URL_SUPORTE = f'https://api.whatsapp.com/send?phone=5511985640273'
CONFIG_PATH = arquivo_com_caminho_absoluto('bin', 'config.json')
BASE = os.path.abspath('base')
DOWNLOAD_DIR =  cria_dir_no_dir_de_trabalho_atual(dir='downloads', print_value=False, criar_diretorio=True)
try:
    limpa_diretorio(DOWNLOAD_DIR)
except:
    pass
# -- GLOBAL -- #

class Bot:    
    def __init__(self, headless, download_files, rotate_user_agent=False) -> None:
        # --- CHROME OPTIONS --- #
        self._options = ChromeOptions()
        
        if download_files:
            # --- PATH BASE DIR --- #
            self._SETTINGS_SAVE_AS_PDF = {
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


            self._PROFILE = {
                        'printing.print_preview_sticky_settings.appState': json.dumps(self._SETTINGS_SAVE_AS_PDF),
                        "savefile.default_directory":  f"{DOWNLOAD_DIR}",
                        "download.default_directory":  f"{DOWNLOAD_DIR}",
                        "download.prompt_for_download": False,
                        "download.directory_upgrade": True,
                        # "profile.managed_default_content_settings.images": 2,
                        "safebrowsing.enabled": True,
                        "credentials_enable_service": False,
                        "profile.password_manager_enabled": False,
                    }
                
            self._options.add_experimental_option('prefs', self._PROFILE)
            self._options.add_argument('--kiosk-printing')  # activate for download files
        
        if headless == True:
            self._options.add_argument('--headless')
            self._options.add_argument('--disable-gpu')
            self._options.add_argument("--no-sandbox")
        
        self._options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
        self._options.add_experimental_option('useAutomationExtension', False)
        if rotate_user_agent:
            self.user_agent = cria_user_agent()
            self._options.add_argument(f"--user-agent={self.user_agent}")
        self._options.add_argument("--disable-web-security")
        self._options.add_argument("--allow-running-insecure-content")
        self._options.add_argument("--disable-extensions")
        self._options.add_argument("--start-maximized")
        self._options.add_argument("--disable-setuid-sandbox")
        self._options.add_argument("--disable-infobars")
        self._options.add_argument("--disable-webgl")
        self._options.add_argument("--disable-popup-blocking")
        self._options.add_argument('--disable-software-rasterizer')
        self._options.add_argument('--no-proxy-server')
        self._options.add_argument("--proxy-server='direct://'")
        self._options.add_argument('--proxy-bypass-list=*')
        self._options.add_argument('--disable-dev-shm-usage')
        self._options.add_argument('--block-new-web-contents')
        self._options.add_argument('-–disable-notifications')
        self._options.add_argument("--window-size=1920,1080")

        try:
            self.__service = Service(executable_path=os.path.abspath('bin/chromedriver.exe'))
            self.DRIVER = Chrome(service=self.__service, options=self._options)
        except Exception as e:
            try:
                self.__service = Service(executable_path=ChromeDriverManager().install())
                self.DRIVER = Chrome(service=self.__service, options=self._options)
            except Exception as e:
                self.__service = Service(executable_path=ChromeDriverDownloader(allways_download=True).download_chromedriver())
                self.DRIVER = Chrome(service=self.__service, options=self._options)
        
        
        def enable_download_in_headless_chrome(driver, download_dir):
            '''
            This code adds headless Chrome browser support to Selenium WebDriver to allow automatic downloading of files to a specified directory.
            More specifically, the code adds a missing "send_command" command to the driver's command executor and then executes a "Page.setDownloadBehavior" command to allow automatic downloading of files to the specified directory.
            The first step is necessary because support for the "send_command" command is not included in Selenium WebDriver by default. The second step uses the Chrome DevTools Protocol "Page.setDownloadBehavior" command to allow automatic downloading of files to a specified directory.
            In short, the code adds support for automatically downloading files to a specified directory in GUI-less Chrome using Selenium WebDriver.
            '''
            driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
            command_result = driver.execute("send_command", params)
        enable_download_in_headless_chrome(self.DRIVER, DOWNLOAD_DIR)
        
        
        self.WDW2 = WebDriverWait(self.DRIVER, timeout=2)
        self.WDW4 = WebDriverWait(self.DRIVER, timeout=4)
        self.WDW6 = WebDriverWait(self.DRIVER, timeout=6)
        self.WDW8 = WebDriverWait(self.DRIVER, timeout=8)
        self.WDW10 = WebDriverWait(self.DRIVER, timeout=10)
        self.WDW20 = WebDriverWait(self.DRIVER, timeout=20)
        self.WDW25 = WebDriverWait(self.DRIVER, timeout=25)
        self.WDW30 = WebDriverWait(self.DRIVER, timeout=30)
        self.WDW35 = WebDriverWait(self.DRIVER, timeout=35)
        self.WDW40 = WebDriverWait(self.DRIVER, timeout=40)
        self.WDW45 = WebDriverWait(self.DRIVER, timeout=45)
        self.WDW = self.WDW6

        self.DRIVER.maximize_window()
        return self.DRIVER
""")
    
    # CRIA ARQUIVO PYTHON EM database
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        f.write("""
'''
SE ESTIVER COM DÚVIDAS EM QUAL UTILIZAR, LEIA COM ATENÇÃO:
Benefícos ao utilizar o banco de dados ao invés de uma planilha Excel
    1. Assegura dados consistentes com regras de validação e restrições do banco.
    2. Lida com grandes volumes de dados sem problemas de desempenho.
    3. Suporte a transações garante segurança e consistência com múltiplos usuários executando consultas na tabela.
    4. Consultas SQL complexas para filtragem e agregação de dados.
    5. Facilidade para modificar esquemas e adicionar novos campos.
    6. Integração com APIs, aplicações web e serviços.
    7. Bancos de dados mantêm registros para auditoria e rastreamento.
    8. Permite automatização de processos e operações em grande escala.

Meleficios de usar:
    1. Configurar e gerenciar ORMs é mais complexo que planilhas Excel.
    2. Uso de ORMs pode exigir habilidades em SQL e programação.
    3. Bancos de dados necessitam de recursos adicionais para operação.
    4. Planilhas são melhores para visualizar dados de forma amigável.
    5. Excel é mais eficiente para tarefas simples ou análises rápidas.
    6. Planilhas permitem colaboração em tempo real com maior facilidade.
    7. Depurar erros em ORMs pode ser mais desafiador que em planilhas.
    8. Bancos de dados requerem atualizações frequentes e manutenção contínua.

Para alcançar ambos os gostos, também deixei um código para usar uma planilha Excel, como se fosse um banco de dados.
'''
from payconpy.fpython.functions_for_py import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
import pandas as pd
import os

engine = create_engine('sqlite:///bin/database.db', pool_size=15, max_overflow=20)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class TABLE(Base):
    __tablename__ = 'table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
    nome = Column(String)
    
Base.metadata.create_all(engine)  # cria a tabela no banco de dados

    
class DBManager:
    def __init__(self):
        # Inicializa uma nova sessão com o banco de dados.
        
        self.session = Session()

    def create_item(self, status, name):
        # Cria um novo registro na tabela.

        new_item = TABLE(status=status, name=name)
        self.session.add(new_item)
        self.session.commit()

    def get_item(self, id):
        # Retorna o registro com o ID fornecido
        return self.session.query(TABLE).filter_by(id=id).first()
    

    def delete_item(self, id):
        # Exclui o registro com o ID fornecido da tabela

        delete_item_from_db = self.get_item(id)
        self.session.delete(delete_item_from_db)
        self.session.commit()
        
    def delete_all(self):
        # Exclui todos os registros da tabela.

        self.session.query(TABLE).delete()
        self.session.commit()

    def get_item(self, id):
        # Retorna o registro com o ID fornecido da tabela. Se nenhum registro for encontrado, retorna None.
        return self.session.query(TABLE).filter_by(id=id).first()
    

    def get_column_status(self):
        # Retorna o registro de status com o ID fornecido da tabela. Se nenhum registro for encontrado, retorna None.
        return self.session.query(TABLE.status).all()
    
class ExcelDBManager:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        # Cria uma planilha se ela não existir
        if not os.path.exists(self.excel_file):
            df = pd.DataFrame(columns=['id', 'status', 'nome'])
            df.to_excel(self.excel_file, index=False)

    def create_item(self, status, name):
        # Lê a planilha, encontra o próximo ID e adiciona o item
        df = pd.read_excel(self.excel_file)
        next_id = df['id'].max() + 1 if not df['id'].empty else 1
        new_item = {'id': next_id, 'status': status, 'nome': name}
        df = df.append(new_item, ignore_index=True)
        df.to_excel(self.excel_file, index=False)

    def get_item(self, item_id):
        # Retorna o item com o ID especificado
        df = pd.read_excel(self.excel_file)
        item = df[df['id'] == item_id]
        return item if not item.empty else None

    def delete_item(self, item_id):
        # Exclui o item com o ID especificado
        df = pd.read_excel(self.excel_file)
        df = df[df['id'] != item_id]
        df.to_excel(self.excel_file, index=False)

    def delete_all(self):
        # Exclui todos os itens
        df = pd.DataFrame(columns=['id', 'status', 'nome'])
        df.to_excel(self.excel_file, index=False)

    def get_column_status(self):
        # Retorna todos os status
        df = pd.read_excel(self.excel_file)
        return df['status'].tolist()

""")
    
    # CRIA ARQUIVO PYTHON EM exceptions
    with open(EXCEPTIONS_PATH, 'w', encoding='utf-8') as f:
        f.write("""from payconpy.fexceptions.exceptions import *
""")
    
    # cria arquivo json
    with open(CONFIG_PATH, 'w', encoding='utf-8') as fjson:
        fjson.write("""{
    "BOT": {
        "USER": "USER",
        "PASSWORD": "PASSWORD",
        "HEADLESS": false
        }
}""")
        
    # cria arquivo utils
    with open(UTILS_PATH, 'w', encoding='utf-8') as fjson:
        fjson.write("""""")

    # cria arquivo de tests
    with open(TESTS_PATH, 'w', encoding='utf-8') as fjson:
        fjson.write("""from payconpy.fpdf.focr.orc import *
from payconpy.fpdf.fcompress.compress import *
from payconpy.fpdf.fimgpdf.img_to_pdf import *
from payconpy.fpysimplegui.functions_for_sg import *
from payconpy.fpython.functions_for_py import *
from payconpy.fregex.functions_re import *
from payconpy.fselenium.functions_selenium import *
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# SEMPRE COLOQUE O QUE A FUNÇÃO TEM QUE FAZER EXPLICITAMENTE
""")

    # cria arquivo .gitignore
    with open(GITIGNORE_PATH, 'w', encoding='utf-8') as fjson:
        fjson.write("""# File created using '.gitignore Generator' for Visual Studio Code: https://bit.ly/vscode-gig
# Created by https://www.toptal.com/developers/gitignore/api/windows,visualstudiocode,git,jupyternotebooks,pycharm,pycharm+all,pycharm+iml,pydev,python,pythonvanilla
# Edit at https://www.toptal.com/developers/gitignore?templates=windows,visualstudiocode,git,jupyternotebooks,pycharm,pycharm+all,pycharm+iml,pydev,python,pythonvanilla

### Git ###
# Created by git for backups. To disable backups in Git:
# $ git config --global mergetool.keepBackup false
*.orig

# Created by git when using merge tools for conflicts
*.BACKUP.*
*.BASE.*
*.LOCAL.*
*.REMOTE.*
*_BACKUP_*.txt
*_BASE_*.txt
*_LOCAL_*.txt
*_REMOTE_*.txt

### JupyterNotebooks ###
# gitignore template for Jupyter Notebooks
# website: http://jupyter.org/

.ipynb_checkpoints
*/.ipynb_checkpoints/*

# IPython
profile_default/
ipython_config.py

# Remove previous ipynb_checkpoints
#   git rm -r .ipynb_checkpoints/

### PyCharm ###
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff
.idea/**/workspace.xml
.idea/**/tasks.xml
.idea/**/usage.statistics.xml
.idea/**/dictionaries
.idea/**/shelf

# AWS User-specific
.idea/**/aws.xml

# Generated files
.idea/**/contentModel.xml

# Sensitive or high-churn files
.idea/**/dataSources/
.idea/**/dataSources.ids
.idea/**/dataSources.local.xml
.idea/**/sqlDataSources.xml
.idea/**/dynamic.xml
.idea/**/uiDesigner.xml
.idea/**/dbnavigator.xml

# Gradle
.idea/**/gradle.xml
.idea/**/libraries

# Gradle and Maven with auto-import
# When using Gradle or Maven with auto-import, you should exclude module files,
# since they will be recreated, and may cause churn.  Uncomment if using
# auto-import.
# .idea/artifacts
# .idea/compiler.xml
# .idea/jarRepositories.xml
# .idea/modules.xml
# .idea/*.iml
# .idea/modules
# *.iml
# *.ipr

# CMake
cmake-build-*/

# Mongo Explorer plugin
.idea/**/mongoSettings.xml

# File-based project format
*.iws

# IntelliJ
out/

# mpeltonen/sbt-idea plugin
.idea_modules/

# JIRA plugin
atlassian-ide-plugin.xml

# Cursive Clojure plugin
.idea/replstate.xml

# SonarLint plugin
.idea/sonarlint/

# Crashlytics plugin (for Android Studio and IntelliJ)
com_crashlytics_export_strings.xml
crashlytics.properties
crashlytics-build.properties
fabric.properties

# Editor-based Rest Client
.idea/httpRequests

# Android studio 3.1+ serialized cache file
.idea/caches/build_file_checksums.ser

### PyCharm Patch ###
# Comment Reason: https://github.com/joeblau/gitignore.io/issues/186#issuecomment-215987721

# *.iml
# modules.xml
# .idea/misc.xml
# *.ipr

# Sonarlint plugin
# https://plugins.jetbrains.com/plugin/7973-sonarlint
.idea/**/sonarlint/

# SonarQube Plugin
# https://plugins.jetbrains.com/plugin/7238-sonarqube-community-plugin
.idea/**/sonarIssues.xml

# Markdown Navigator plugin
# https://plugins.jetbrains.com/plugin/7896-markdown-navigator-enhanced
.idea/**/markdown-navigator.xml
.idea/**/markdown-navigator-enh.xml
.idea/**/markdown-navigator/

# Cache file creation bug
# See https://youtrack.jetbrains.com/issue/JBR-2257
.idea/$CACHE_FILE$

# CodeStream plugin
# https://plugins.jetbrains.com/plugin/12206-codestream
.idea/codestream.xml

# Azure Toolkit for IntelliJ plugin
# https://plugins.jetbrains.com/plugin/8053-azure-toolkit-for-intellij
.idea/**/azureSettings.xml

### PyCharm+all ###
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff

# AWS User-specific

# Generated files

# Sensitive or high-churn files

# Gradle

# Gradle and Maven with auto-import
# When using Gradle or Maven with auto-import, you should exclude module files,
# since they will be recreated, and may cause churn.  Uncomment if using
# auto-import.
# .idea/artifacts
# .idea/compiler.xml
# .idea/jarRepositories.xml
# .idea/modules.xml
# .idea/*.iml
# .idea/modules
# *.iml
# *.ipr

# CMake

# Mongo Explorer plugin

# File-based project format

# IntelliJ

# mpeltonen/sbt-idea plugin

# JIRA plugin

# Cursive Clojure plugin

# SonarLint plugin

# Crashlytics plugin (for Android Studio and IntelliJ)

# Editor-based Rest Client

# Android studio 3.1+ serialized cache file

### PyCharm+all Patch ###
# Ignore everything but code style settings and run configurations
# that are supposed to be shared within teams.

.idea/*

!.idea/codeStyles
!.idea/runConfigurations

### PyCharm+iml ###
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio, WebStorm and Rider
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff

# AWS User-specific

# Generated files

# Sensitive or high-churn files

# Gradle

# Gradle and Maven with auto-import
# When using Gradle or Maven with auto-import, you should exclude module files,
# since they will be recreated, and may cause churn.  Uncomment if using
# auto-import.
# .idea/artifacts
# .idea/compiler.xml
# .idea/jarRepositories.xml
# .idea/modules.xml
# .idea/*.iml
# .idea/modules
# *.iml
# *.ipr

# CMake

# Mongo Explorer plugin

# File-based project format

# IntelliJ

# mpeltonen/sbt-idea plugin

# JIRA plugin

# Cursive Clojure plugin

# SonarLint plugin

# Crashlytics plugin (for Android Studio and IntelliJ)

# Editor-based Rest Client

# Android studio 3.1+ serialized cache file

### PyCharm+iml Patch ###
# Reason: https://github.com/joeblau/gitignore.io/issues/186#issuecomment-249601023

*.iml
modules.xml
.idea/misc.xml
*.ipr

### pydev ###
.pydevproject

### Python ###
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook

# IPython

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

### Python Patch ###
# Poetry local configuration file - https://python-poetry.org/docs/configuration/#local-configuration
poetry.toml

# ruff
.ruff_cache/

# LSP config files
pyrightconfig.json

### PythonVanilla ###
# Byte-compiled / optimized / DLL files

# C extensions

# Distribution / packaging

# Installer logs

# Unit test / coverage reports

# Translations

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.

# PEP 582; used by e.g. github.com/David-OConnor/pyflow


### VisualStudioCode ###
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
!.vscode/*.code-snippets

# Local History for Visual Studio Code
.history/

# Built Visual Studio Code Extensions
*.vsix

### VisualStudioCode Patch ###
# Ignore all local history of files
.history
.ionide

### Windows ###
# Windows thumbnail cache files
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db

# Dump file
*.stackdump

# Folder config file
[Dd]esktop.ini

# Recycle Bin used on file shares
$RECYCLE.BIN/

# Windows Installer files
*.cab
*.msi
*.msix
*.msm
*.msp

# Windows shortcuts
*.lnk

# End of https://www.toptal.com/developers/gitignore/api/windows,visualstudiocode,git,jupyternotebooks,pycharm,pycharm+all,pycharm+iml,pydev,python,pythonvanilla

# Custom rules (everything added below won't be overriden by 'Generate .gitignore File' if you use 'Update' option)

*test*
*logs*
bin\Tesseract-OCR
bin/Tesseract-OCR
*Resultado*
*xls*
database.db
bin/database.db
""")

    # cria diretório base
    if create_base_dir:
        cria_dir_no_dir_de_trabalho_atual('base')

    print('Criando Ambiente Virtual')
    os.system('python -m venv venv')
    print('Criado!')
    print('Baixando pacotes')
    os.system(f'.\\venv\\Scripts\\pip.exe install {packages}')
    faz_log('LEMBRE-SE DE ATIVAR O AMBIENTE VIRTUAL CRIADO PARA NÃO USAR BIBLIOTECAS GLOBAIS PARA QUE O EXECUTÁVEL VENHA A FICAR PESADO POSTERIORMENTE', color='yellow')


def download_file_from_github(url, save_path):
    """
    Baixa um arquivo do GitHub garantindo que o stream seja tratado corretamente,
    o que é crucial para arquivos grandes.
    
    Args:
        url (str): URL do arquivo no GitHub.
        save_path (str): Caminho local onde o arquivo será salvo.
    """
    with requests.get(url, stream=True) as response:
        # Verifica se a requisição foi bem sucedida
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            # Escreve o conteúdo do arquivo em chunks para não sobrecarregar a memória
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)



USER_AGENTS = [
'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG-SM-G928A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Lenovo P2a42 Build/QQ2A.200405.005)',
'Dalvik/2.1.0 (Linux; U; Android 10; M2010J19SL MIUI/V12.0.10.0.QJQMIXM)',
'Mozilla/5.0 (Linux; Android 9; Redmi 7A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.3; C5503 Build/10.4.B.0.569)',
'Mozilla/5.0 (X11; Linux aarch64; rv:79.0) Gecko/20100101 Firefox/79.0',
'Dalvik/2.1.0 (Linux; U; Android 9; Redmi Note 7 MIUI/V10.3.21.0.PFGMXTC)',
'Mozilla/5.0 (Linux; Android 10; moto g(8) plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-J610G) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.1.2; V865M Build/JZO54K)',
'Mozilla/5.0 (Linux; Android 6.0.1; vivo 1606) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A315G) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/11.2 Chrome/75.0.3770.143 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; JSN-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.9 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Cortana 1.13.1.18362; 10.0.0.0.18362.1256) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
'Mozilla/5.0 (Linux; Android 7.1.2; LM-X410.F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; CPH2005 Build/QKQ1.200216.002)',
'Guzzle/3.9.3 curl/7.29.0 PHP/7.2.34',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-T580) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.22',
'Dalvik/2.1.0 (Linux; U; Android 9; moto e6s Build/POES29.288-60-6-1-1)',
'Mozilla/5.0 (Linux; Android 10; LM-K300) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9.0; Redmi Note 8T MIUI/20.3.26)',
'Mozilla/5.0 (Linux; Android 8.1.0; LML713DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; Prime 1 Build/LMY47I)',
'Mozilla/5.0 (Linux; Android 10; moto g(7) Build/QPUS30.52-23-13-4; en-us) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36 Puffin/9.4.1.51004AP',
'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.100 Safari/537.36 UCBrowser/13.0.0.1288',
'Mozilla/5.0 (Linux; Android 10; SM-G988N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; Lenovo TB-X304F Build/NMF26F; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.166 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MI MAX 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; moto e5 play Build/OPGS28.54-53-8-19)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/96.0.4664.53 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 10; SM-G973W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A305F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; HLK-AL00 Build/HONORHLK-AL00)',
'Mozilla/5.0 (Linux; Android 9.0; TAB910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-A516U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; LM-V409N Build/PKQ1.190202.001)',
'Mozilla/5.0 (Linux; Android 7.0; i7_Plus Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.99 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; GN5001S Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 9; CPH1923) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.2.172 Yowser/2.5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A115M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-V350) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ASUS_X00TDB) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; PCLM50 Build/QKQ1.200216.002)',
'Mozilla/5.0 (Linux; Android 10; vivo 1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36 OPR/60.3.3004.55692',
'Mozilla/5.0 (Linux; Android 9; SM-A205W Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 3.1 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-J710F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Pixel 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A705W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; SM-J737S Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.143 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
'Mozilla/5.0 (Linux; Android 9; moto z3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Infinix X680D Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; U; Android 9; tr-tr; Redmi Note 8 Pro Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g',
'Mozilla/5.0 (Linux; Android 9; A5_Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LIO-L29; HMSCore 5.0.5.300) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 HuaweiBrowser/11.0.3.304 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.09.4.5083',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36/CToIDhJz-37',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; BLN-AL40 Build/HONORBLN-AL40)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 kIBFnB75-24 kIBFnB75-24 Firefox/77.0',
'Mozilla/5.0 (Linux; U; Android 8.1.0; CPH1803 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36 OPR/50.0.2254.149182',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-T3777 Build/LMY47X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.111 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; 502SO Build/39.2.D.0.269)',
'Mozilla/5.0 (Linux; Android 7.1.1; Pacific) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/9.2.0.2.122.217074189 SamsungBrowser/4.0 Chrome/81.0.4044.117 Mobile VR Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G988B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Lava Be_U Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G955U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.120 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; PMT3437_4G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 8T Build/QKQ1.200114.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; A3300 Build/KTU84Q)',
'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.58 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.107 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G955F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-P205) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G970W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; CLT-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; JKM-LX1 Build/HUAWEIJKM-LX1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.116 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; Rover) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; moto g stylus 5G Build/RRES31.Q2-11-61-3)',
'Dalvik/2.1.0 (Linux; U; Android 11; M2012K11G Build/RKQ1.201112.002)',
'Mozilla/5.0 (Linux; Android 5.0; SM-N9005) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.101 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YaBrowser/19.5.2.38.10 YaApp_iOS/31.00 YaApp_iOS_Browser/31.00 Safari/604.1',
'Dalvik/2.1.0 (Linux; U; Android 7.0; LAVAA1 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J530F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Primo EM2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; P021) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) WKWebView/BitrixMobile/Version=33',
'Mozilla/5.0 (Linux; Android 7.1.2; SM-T331) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; RMX2151) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; 5002H_EEA Build/QKQ1.200623.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4285.0 Safari/537.36 Edg/88.0.670.0',
'Mozilla/5.0 (Linux; Android 11; Mi MIX 3 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; HUAWEI SCL-L01 Build/HuaweiSCL-L01)',
'Dalvik/2.1.0 (Linux; U; Android 10; 2040 Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; Android 11; SM-A405FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; GM1917 MIUI/21.1.6)',
'Mozilla/5.0 (Linux; Android 11; vivo 1906) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; LML211BL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; J9210) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N976N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 OPR/58.2.2878.53403',
'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.05.4.5025',
'Dalvik/2.1.0 (Linux; U; Android 6.0; I7D Build/MRA58K)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; CPH2083) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; GM1901) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/85.0.4183.109 Mobile/15E148 Safari/604.1',
'Dalvik/2.1.0 (Linux; U; Android 7.0; NB754 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 5 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; Bonvi Pro Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 7.1.1; GT-I9082 Build/JDQ39)',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-P600) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Mi A1 Build/PKQ1.180917.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36 Viber/12.9.5.2',
'Mozilla/5.0 (Linux; Android 10; SM-J600F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; BRQ-AL00 Build/HUAWEIBRQ-AL00)',
'Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 7 Build/RQ2A.210405.005)',
'Mozilla/5.0 (X11; U; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.123 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; LG-D100 Build/KOT49I)',
'Mozilla/5.0 (Linux; Android 8.0.0; SAMSUNG SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; YAL-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 9S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Mobile Safari/537.36 PTST/201104.221132',
'Mozilla/5.0 (Linux; Android 10; CPH1823) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI SCL-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; zh-tw; MI 8 Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/79.0.3945.147 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.9.3-gn,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 10; MI 9 Transparent Edition) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; G3223) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-LS998) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; OPPO R9m Build/LMY47I)',
'com.google.GoogleMobile/109.0 iPhone/13.5.1 hw/iPhone8_1',
'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36 YaApp_Android/10.10 YaSearchBrowser/10.10',
'Dalvik/2.1.0 (Linux; U; Android 9; Moto Z3 Play Build/PPWS29.183-29-1-19)',
'Mozilla/5.0 (Linux; Android 10; SM-A805F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; Pluri_Q8 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 5.1; InFocus M560) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.5.63.00 SA/1 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; SM-T380 Build/M1AJQ)',
'Mozilla/5.0 (Linux; Android 10; moto z4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; vivo 1724 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/6.4.0.2',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; NP-852 Build/O11019)',
'Mozilla/5.0 (Linux; Android 10; BLA-L29 Build/HUAWEIBLA-L29S; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36 OcIdWebView ({"os":"Android","osVersion":"29","app":"com.google.android.gms","appVersion":"218","style":2,"isDarkTheme":true})',
'Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2965.67 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MED-LX9; HMSCore 5.0.1.313) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 HuaweiBrowser/10.1.3.321 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; itel S11X Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; Mi 9 SE Build/RKQ1.200826.002)',
'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'WordPress/5.4.2; https://trending30.cloudaccess.host',
'Mozilla/5.0 (Linux; Android 10; V2029; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/7.9.0.0',
'Mozilla/5.0 (Linux; Android 8.1.0; vivo 1820) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; SAMSUNG-SM-G890A Build/LRX22G)',
'Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-T520 Build/NJH47F)',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; C6902 Build/14.5.A.0.242)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.57',
'Mozilla/5.0 (Linux; Android 10; POCO X2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; moto z3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-N980F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G903M Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/85.0.4183.81 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YJApp-IOS jp.co.yahoo.ipn.appli/4.25.0',
'Dalvik/2.1.0 (Linux; U; Android 9; SCM-AL09 Build/HUAWEISCM-AL09)',
'Mozilla/5.0 (Linux; Android 10; SM-S205DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; TECNO BB4k) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 4.2.2; ru-RU; GT-P3113 Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.10.0.1163 UCTurbo/1.9.8.900 Mobile Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 8 Build/QKQ1.200114.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-Q730) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.142 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 10; Nokia 7.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; SM-G530M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; M2010J19CI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; KS605 Build/OPM2.171019.012)',
'Mozilla/5.0 (Linux; Android 10; motorola one) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; HUAWEI TAG-L22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Redmi 6A MIUI/V10.2.5.0.OCBMIXM)',
'Dalvik/2.1.0 (Linux; U; Android 9; A30 Build/PPR1.180610.011)',
'Mozilla/5.0 (Linux; Android 11; Pixel 2 Build/RP1A.201005.004.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.86 Mobile Safari/537.36 BingSapphire/21.0.390204302',
'Mozilla/5.0 (Linux; Android 9; SM-J810M Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36 UCURSOS/v1.5.4_227-android',
'Mozilla/5.0 (Linux; Android 7.0; CPN-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.50 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Opal 4S Build/OPM2.171019.012)',
'Dalvik/2.1.0 (Linux; U; Android 9; X96mini_RP Build/PPR1.180610.011)',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi 7A MIUI/V12.0.2.0.QCMINXM)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24',
'Dalvik/2.1.0 (Linux; U; Android 11; V2042 Build/RP1A.200720.012)',
'Mozilla/5.0 (Linux; U; Android 5.1.1; en-US; A37f Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.12.6.1221 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 7.1.2; Swift 2 X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.90.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; Swift 2 X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.131 Mobile Safari/537.36',
'Mozilla/5.0 (X11; Ubuntu; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2858.31 Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; SAMSUNG SM-G850F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.1 Chrome/79.0.3945.136 Mobile Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; moto e(7i) power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; RMX2027) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 4.4.2; es-mx; 9002A Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
'Dalvik/2.1.0 (Linux; U; Android 7.0; QMobile Evok Power Lite Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 5.0; RCT6773W22B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; dandelion MIUI/V12.0.2.0.QCDIDXM)',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G988U1) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; 2014818) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510FN Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36 GSA/11.11.10.21.arm',
'Mozilla/5.0 (Linux; Android 6.0; tv001 on rtd289x Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; LGM-V300S Build/PKQ1.190414.001)',
'Mozilla/5.0 (Linux; Android 8.0.0; Mi A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36,gzip(gfe)',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N750S Build/LMY47X)',
'Mozilla/5.0 (Linux; Android 7.0; Moto G (4) Build/NPJS25.93-14-18; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; moto g(6) play Build/PPPS29.118-57-11)',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J710F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2010J19CG MIUI/V12.0.10.0.QJFRUXM)',
'Mozilla/5.0 (Linux; Android 6.0.1; HUAWEI RIO-L01 Build/HuaweiRIO-L01; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G981N/KSU1EUH1) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A530F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Smart 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; X96mini) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-A125U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 4.2.2; FreeTAB 1017 IPS2 X4+ Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.59 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1; OPPO A33) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; JAT-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.67 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; Microsoft Outlook 15.0.4420; Microsoft Outlook 15.0.4420; ms-office; MSOffice 15)',
'Mozilla/5.0 (Linux; U; Android 10; id-id; Mi 10T Pro Build/QKQ1.200419.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.8.3-gn',
'Mozilla/5.0 (Linux; U; Android 10; zh-tw; MI 8 Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.7.4-gn,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 9; 5006D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; CPH1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.72 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 9; ZTE Blade A3 2019RU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.90.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ZTE Blade V1000RU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Mi 10 MIUI/V11.0.7.0.QJBINXM)',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi 7A MIUI/V12.0.3.0.QCMMIXM)',
'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.09.4.5079',
'Mozilla/5.0 (Linux; Android 10; Mi A2 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ALP-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-N950U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/46.02.4.5147',
'Dalvik/1.6.0 (Linux; U; Android 4.2.2; C2005 Build/15.2.A.2.5)',
'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; LG-SP200) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; i55D Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; SHV40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Armor 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-T560NU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; vivo 1902) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 11; SM-M215F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; HK1 Max Build/PQ2A.190205.003)',
'Mozilla/5.0 (Linux; Android 6.0; TECNO-C9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G800F Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 YaBrowser/19.6.0.158 (lite) Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; vivo 1915) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36 OPR/59.1.2926.54067',
'Mozilla/5.0 (Linux; Android 6.0; XT1572) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; 506SH) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 9; Redmi Note 5 Build/PKQ1.180904.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.111 Mobile Safari/537.36 OPR/44.1.2254.143214',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-A720F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.111 Mobile Safari/537.36 YaApp_Android/8.70 YaSearchBrowser/8.70',
'Mozilla/5.0 (iPad; CPU OS 14_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
'Mozilla/5.0 (Linux; arm_64; Android 6.0; K6000 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.4.76.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-S111DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; A1601) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 8 MIUI/V12.0.2.0.QCOCNXM)',
'Mozilla/5.0 (Linux; Android 8.0.0; RNE-L21 Build/HUAWEIRNE-L21; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.111 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2006C3MG MIUI/V12.0.2.0.QCRTRXM)',
'Mozilla/5.0 (Linux; Android 7.1.1; Moto G Play Build/NPI26.48-43; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 10; MI 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaApp_Android/21.113.1 YaSearchBrowser/21.113.1 BroPP/1.0 SA/3 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; HTC Desire 625) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; Lenovo K8 Note) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; TECNO KE5j) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; RMX1911) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36 OPR/59.1.2926.54067',
'Mozilla/5.0 (Linux; Android 9; POT-LX1A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.166 Mobile Safari/537.36 OPR/65.2.3381.61420',
'Mozilla/5.0 (Linux; Android 8.1.0; Plume L3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; JMM-AL00 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 7.0; SM-J530F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J500F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; REVVL 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; XP8800 Build/8A.0.5-10-8.1.0-11.20.00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G532M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; KFMUWI Build/PS7321)',
'Mozilla/5.0 (Linux; Android 10; HRY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile DuckDuckGo/5 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Redmi Note 3 MIUI/V8.0.5.0.MHRMIDG)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148',
'Mozilla/5.0 (Linux; Android 11; SM-G986U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.107 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Redmi 5 MIUI/V10.1.1.0.NDACNFI)',
'Mozilla/5.0 (Linux; Android 11; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; SM-T530NU Build/LRX22G; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; Sparkle V Build/LMY47O)',
'Mozilla/5.0 (Linux; Android 5; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045223 Mobile Safari/537.36 MMWEBID/2540 MicroMessenger/7.0.14.1660(0x27000E37) Process/tools NetType/WIFI Language/zh_CN ABI/arm64 WeChat/arm64 wechatdevtools',
'Mozilla/5.0 (Linux; U; Android 6.0; en-us; 5045T Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3034.43 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; Grand2 Build/LMY47D)',
'Dalvik/1.6.0 (Linux; U; Android 4.2.2; TAB-970DC Build/JDQ39)',
'Mozilla/5.0 (Linux; U; Android 5.1; en-gb; A1601 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/15.5.1.1',
'Mozilla/5.0 (Linux; Android 8.1.0; AX1077+) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A715F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; CPH1933) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; vivo 1609) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J250F Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 YaBrowser/19.1.0.130 (lite) Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; BL5000 Build/NRD90M)',
'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11 CoolNovo/2.0.2.26',
'Mozilla/5.0 (Linux; Android 10; SM-N986B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.11.4.5104',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J710MN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.120 Mobile Safari/537.36',
'Apache-HttpClient/4.5.2 (Java/1.8.0_202)',
'Mozilla/5.0 (Linux; Android 9; SM-N960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G977N) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; WAS-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.114 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0; HUAWEI GRA-L09 Build/HUAWEIGRA-L09)',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-A700FD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36 OPR/54.2.2672.49907',
'Mozilla/5.0 (Linux; Android 10; Lava Z66) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Transpeed_6K Build/PPR1.181005.003)',
'Mozilla/5.0 (Linux; Android 10; MI 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J250G Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.137 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J410F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G973U1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; LG-D405 Build/LRX22G.A1442306864)',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Lenovo K8 Note Build/NMB26.54-74)',
'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01KD Build/PPR1.180610.009)',
'Mozilla/5.0 (Linux; Android 10; M2004J7AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Lenovo TB-7504X Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.111 Mobile Safari/537.36 YaApp_Android/10.51 YaSearchBrowser/10.51',
'Mozilla/5.0 (Linux; Android 9; SM-G611MT) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; TIT-L01) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; IN2020 Build/RKQ1.200826.002)',
'Mozilla/5.0 (Linux; U; Android 7.1.1; MI MAX 2 Build/NMF26F; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 OPR/50.0.2254.149182',
'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-G930R4 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; SKR-H0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A015M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 6.0; Lenovo S1a40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 YaBrowser/20.2.5.140.00 Mobile SA/1 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; I4213) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 YaBrowser/19.6.0.612.00 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A105FN Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; Vivo XL3 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; Redmi Note 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; TIT-L01 Build/HONORTIT-L01) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36 YaApp_Android/9.40 YaSearchBrowser/9.40',
'Mozilla/5.0 (Linux; Android 7.0; KOB-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-X430 Build/QKQ1.200730.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; SM-J250Y Build/NMF26X)',
'Mozilla/5.0 (Linux; Android 5.1; HTC Desire 728 dual sim) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 7.0; SM-A510F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.4.76.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; POT-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-Q910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/86.0.4240.93 Mobile/15E148 Safari/604.1',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Leader L3 Build/LMY47I)',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; LS-5016 Build/MMB29M)',
'Mozilla/5.0 (Linux; Android 8.1.0; Destiny) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
'com.tinyspeck.chatlyio/20.06.10 (iPhone; iOS 13.6; Scale/3.00)',
'Mozilla/5.0 (Linux; Android 5.1.1; AEOBP) AppleWebKit/537.36 (KHTML, like Gecko) Silk/81.2.9 like Chrome/81.0.4044.138 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; Aquaris M10 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; STV100-3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-A125U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 6A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36 OPR/74.0.3911.218',
'Mozilla/5.0 (Linux; Android 10; SM-A205W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; GT-I9195I Build/QQ3A.200605.002.A1)',
'Mozilla/5.0 (Linux; Android 10; RMX1927) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 3.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; OPPO R7sm Build/LMY47V)',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; K93 Build/KVT49L)',
'Mozilla/5.0 (Linux; Android 9; vivo 1906) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; CPH1931 Build/PKQ1.190714.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1906) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A7050) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Moto Z2 Play) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; 5099D_RU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; M2101K9AG Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; CLT-L29 Build/HUAWEICLT-L29; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; XT1023 Build/KXC21.5-53)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 OPT/3.2.4',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 9 Pro MIUI/V12.0.4.0.QJZEUXM)',
'Mozilla/5.0 (Linux; Android 10; SM-T860 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 7.1; F88 Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 10; SM-G986U1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.08.4.5072',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; SM-A600F Build/R16NW)',
'Mozilla/5.0 (Linux; Android 10; MAR-LX1M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.12.4.5121',
'Mozilla/5.0 (Linux; Android 9; moto g(8) play) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36,gzip(gfe),gzip(gfe)',
'Mozilla/5.0 (Linux; Android 9; Redmi 7A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X; Tesseract/1.0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G930U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4322.2 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; SM-T377V Build/NMF26X)',
'Dalvik/2.1.0 (Linux; U; Android 11; moto g 5G Build/RZK31.Q3-25-15)',
'Mozilla/5.0 (Linux; Android 8.1.0; Alcatel T 5033T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; T671H Build/RKQ1.201112.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; BAH2-W19) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; ar-eg; SM-J400F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36 PHX/5.7',
'Mozilla/5.0 (Linux; Android 8.1.0; System Product Name) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.99 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; H9436) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/30.0 Mobile/15E148 Safari/605.1.15',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; E716X Build/KVT49L)',
'Mozilla/5.0 (X11; CrOS aarch64 13020.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4157.0 Safari/537.36 Edg/85.0.531.1',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-N976N) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; Infinix X573B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 3a XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Primo NH Build/Primo_NH)',
'Mozilla/5.0 (Linux; Android 9; moto x4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36 OPR/59.1.2926.54067',
'Mozilla/5.0 (Linux; Android 5.1; S6 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/39.0.0.0 YaBrowser/19.6.0.158 (lite) Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:68.0) Gecko/20100101 Thunderbird/68.7.0 Lightning/68.7.0',
'Mozilla/5.0 (Linux; Android 10; CPH1931) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A217M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; A002OP Build/QKQ1.200209.002)',
'Mozilla/5.0 (Linux; Android 9; ZTE Blade A3 2020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 3.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1904) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; ru-ru; 5015D Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; SO-04J Build/45.0.B.2.95)',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi 8A MIUI/V12.0.1.0.QCPIDXM)',
'Mozilla/5.0 (Linux; Android 8.1.0; vivo 1802 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/6.3.0.4',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G930A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 8.0.0; BND-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 YaBrowser/20.3.4.98.00 SA/1 Mobile Safari/537.36',
'Opera%20Touch/64 CFNetwork/1209 Darwin/20.2.0',
'Mozilla/5.0 (Linux; Android 10; SM-M215F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 YaApp_Android/10.61 YaSearchBrowser/10.61',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; SM-J730F Build/M1AJQ)',
'Mozilla/5.0 (Linux; Android 9; LM-X420 Build/PKQ1.190522.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; MRD-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; RNE-L23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G930V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ONEPLUS A6003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; Z4 Premium Build/KOT49H)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; RAVOZ R8 Build/O11019)',
'Mozilla/5.0 (Linux; U; Android 6.0; en-US; Lenovo A7020a48 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.14.0.1221 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; Lenovo A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; KIWIBOX S1NEW Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 7.0; TRT-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Lenovo YT3-X50L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; KFSUWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/88.3.6 like Chrome/88.0.4324.152 Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; GTB7.5; InfoPath.2; Zoom 3.6.0)',
'Mozilla/5.0 (Linux; Android 9; Lenovo K10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; DM-01G Build/LRX22G)',
'Mozilla/5.0 (Linux; Android 9; SM-J530F Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5 Plus Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 Mobile Safari/537.36 Viber/13.2.0.8',
'Dalvik/2.1.0 (Linux; U; Android 6.0; LEX653 Build/KGXCNFN5902710271S)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; ZS9 Build/O11019)',
'Mozilla/5.0 (Linux; Android 9; SM-A600G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; AGS-L03) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-H831) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; G2 Build/MID_1089IPS; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-J700M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; E6653) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ELE-L04) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 11; SM-G988B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.166 YaApp_Android/21.82.1/apad YaSearchBrowser/21.82.1/apad BroPP/1.0 SA/3 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; 5024F_EEA Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; X1 Build/O11019)',
'Mozilla/5.0 (Linux; Android 6.0; M5s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; INE-LX1 Build/HUAWEIINE-LX1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.166 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J510F Build/LMY47X)',
'Mozilla/5.0 (Linux; Android 10; Mi 9T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 OPR/72.0.3815.207',
'Mozilla/5.0 (Linux; Android 7.0; AGS-W09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; ZL80 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; VOG-L29 Build/HUAWEIVOG-L29; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.86 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; MI 9T Build/QQ3A.200605.002.A1)',
'Dalvik/2.1.0 (Linux; U; Android 11; CPH1933 Build/RKQ1.200903.002)',
'Dalvik/2.1.0 (Linux; U; Android 7.0; SM-J327R6 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 8.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile DuckDuckGo/0 Lilo/0.9.9 Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 9; en-in; POCO F1 Build/PKQ1.180729.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g',
'Mozilla/5.0 (Linux; Android 9; LM-K500 Build/PKQ1.190522.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; C6903 Build/14.6.A.0.368) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Dalvik/2.1.0 (Linux; U; Android 10; moto g(8) power lite Build/QODS30.163-3-20)',
'Mozilla/5.0 (Linux; Android 10; moto z4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 7.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.07.4.5059',
'Mozilla/5.0 (Linux; Android 11; SM-M307FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; wbx 1.0.0; Zoom 3.6.0)',
'Mozilla/5.0 (Linux; Android 8.0.0; AGS2-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; LGLS450 Build/MXB48T)',
'Mozilla/5.0 (Linux; Android 9; CPH1937) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Neffos Y5 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 Viber/13.2.0.8',
'Dalvik/2.1.0 (Linux; U; Android 7.0; MARS NOTE Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-A520F Build/MMB29K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36 SamsungBrowser/CrossApp/0.1.89',
'Mozilla/5.0 (Linux; Android 11; IN2015) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/178.0.397166631 Mobile/15E148 Safari/604.1',
'Dalvik/2.1.0 (Linux; U; Android 9; M530 Build/P00610)',
'Mozilla/5.0 (Linux; Android 8.0.0; AUM-AL20) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 8.1.0; Power 2 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.96 YaBrowser/20.4.1.144.00 SA/1 TA/5.1 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Mi 9 Lite MIUI/V11.3.3.0.PFCEUXM)',
'Mozilla/5.0 (Linux; Android 8.1.0; MI PLAY Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36 YaApp_Android/10.44 YaSearchBrowser/10.44',
'Mozilla/5.0 (Linux; Android 10; CPH1917) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; H4213) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'okhttp/3.<Agent>.0',
'Mozilla/5.0 (Linux; Android 11; M2003J15SC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; U693CL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-T595 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Multilaser_E_Lite Build/V6_20200415)',
'Opera/9.80 (J2ME/MIDP; Opera Mini/4.3.24214/174.101; U; en) Presto/2.12.423 Version/12.16',
'Mozilla/5.0 (Linux; Android 10; GM1910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J610FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-S111DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; LG-US996) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; HIT Q500 3G HT5035PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-G361H Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Viber/13.0.0.4',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 YaBrowser/21.2.2.102 Yowser/2.5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Neffos X1 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; M2006C3LG Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; TECNO P701 Build/NRD90M)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Kova_PCB-T730 Build/OPM5.171019.019)',
'Mozilla/5.0 (Linux; Android 8.1.0; TECNO F1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-T725) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 OPR/59.1.2926.54067',
'Dalvik/2.1.0 (Linux; U; Android 9.0; c200_hy Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 4.2.1; T10A Build/JOP40D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.93 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Ixion X150 Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 9; Redmi 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Aquaris V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; moto e5 play) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 3a XL Build/RQ1A.210205.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; SmartTV Build/KTU84P)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Redmi 6A MIUI/9.6.20)',
'Dalvik/2.1.0 (Linux; U; Android 5.1; PSP3508DUO Build/LMY47D)',
'Dalvik/2.1.0 (Linux; U; Android 10; POCO F2 Pro MIUI/V12.0.3.0.QJKMIXM)',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 5 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Redmi 6 Pro MIUI/V11.0.6.0.PDICNXM)',
'Mozilla/5.0 (Linux; Android 10; SM-P200) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; moto g(7) optimo maxx(XT1955DL) Build/QPO30.85-18)',
'Mozilla/5.0 (Linux; Android 11; KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.50 Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/84.0.4147.122 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 9; SM-A107F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A205G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; Aquaris U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; S8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MAR-LX3A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Wieppo S6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2007J17G MIUI/V12.0.2.0.QJSEUXM)',
'Mozilla/5.0 (Linux; Android 10; VOG-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.16 Mobile Safari/537.36,gzip(gfe),gzip(gfe) (Chrome Image Compression Service)',
'Dalvik/2.1.0 (Linux; U; Android 9; moto e(6) plus Build/PTB29.401-25)',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; HPDTDFJS; H9P; Zoom 3.6.0; MSOffice 12)',
'Mozilla/5.0 (Linux; Android 10; W-K560-TVM Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36/drE6MSTv-30',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.43',
'Mozilla/5.0 (Linux; Android 8.1.0; vivo 1724 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/6.5.0.8',
'Dalvik/1.6.0 (Linux; U; Android 4.2.2; 2014011 MIUI/JHFC6NBC4.0)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; I4312 Build/54.0.A.6.66)',
'Mozilla/5.0 (Linux; Android 7.0; MBOX) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SM-J701MT) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G965U1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; INTEX AQUA 5.5 VR+ Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 10; SM-G977B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; moto g(8) power Build/QPES30.79-124-7)',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 9 Pro Max Build/QKQ1.191215.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-J600GT) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J260A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 10; Nokia 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 YaBrowser/19.7.0.117.00 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-P610) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4210.0 Safari/537.36 Edg/86.0.594.1',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-A310F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 OPR/55.2.2719.50740',
'Dalvik/2.1.0 (Linux; U; Android 9; P2000 Build/PPR1.180610.011)',
'Mozilla/5.0 (Linux; Android 10; SM-G9880) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-J600G Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; RMX2103 Build/QKQ1.200614.002)',
'Mozilla/5.0 (Linux; U; Android 6.0.1; id-id; Redmi 3X Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g',
'Mozilla/5.0 (Linux; Android 6.0; MYA-L22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 OPR/58.2.2878.53403',
'Mozilla/5.0 (Linux; Android 11; SM-A226B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; S60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; BLU STUDIO C 5+5 LTE Build/LMY47V)',
'Mozilla/5.0 (Linux; Android 10; HRY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; LG-H635 Build/MRA58K)',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; A74B Build/KOT49H)',
'Dalvik/2.1.0 (Linux; U; Android 5.0; SM-G900R7 Build/LRX21T)',
'Mozilla/5.0 (Linux; U; Android 4.4.2; 4027X Build/KOT49H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 OPR/33.0.2254.125672',
'Mozilla/5.0 (Linux; Android 10; SM-A217F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36 OPR/62.3.3146.57763',
'Mozilla/5.0 (Linux; Android 9; SM-A205F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ASUS_I001DA) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; CPH2239) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; V2061) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 2 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A505FN Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36 Flipboard/4.2.41/4870,4.2.41.4870',
'Mozilla/5.0 (Linux; Android 8.1.0; LUNA G60X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/84.0.4147.122 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 9; TECNO KC6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; RMX2195) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-N986B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-P350) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 11; in-id; CPH2209 Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 HeyTapBrowser/45.7.6.1',
'Dalvik/1.6.0 (Linux; U; Android 11.10; GT-I9301I Build/KOT49H)',
'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/94.0.4606.71 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; KB2007) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.114 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; Moto G (5S) Build/NPPS26.102-63-1)',
'Mozilla/5.0 (Linux; Android 9; LM-T600) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; E2306) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; CPN-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400',
'Mozilla/5.0 (Linux; Android 7.0; VisionBook P55 X2 LTE Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; ASUS_X00PD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-S102DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)',
'Dalvik/2.1.0 (Linux; U; Android 9; octopus Build/R88-13597.105.0)',
'Mozilla/5.0 (Linux; Android 10; SM-A507FN Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; MI A2 MIUI/8.12.6)',
'Mozilla/5.0 (Linux; Android 9; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Redmi Note 8 Pro Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36',
'VLC/3.0.9 LibVLC/3.0.9',
'Mozilla/5.0 (Linux; Android 6.0; Lenovo TB3-X70F Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; AGS2-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; EML-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A215U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1',
'Opera/9.80 (Android; Opera Mini/7.6.35766/174.101; U; uk) Presto/2.12.423 Version/12.16',
'okhttp/3.8.0',
'Mozilla/5.0 (Linux; Android 10; Infinix X682C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 10; Mi 9T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.143 YaBrowser/19.7.7.115.00 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2006C3LII MIUI/V12.0.19.0.QCDINXM)',
'Mozilla/5.0 (Linux; arm_64; Android 10; Mi 9T Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.4.76.00 SA/1 TA/7.1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; U693CL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J260F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MAR-LX3A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.1; NX907J Build/NMF26F)',
'Mozilla/5.0 (Linux; Android 9; K107) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.44',
'Mozilla/5.0 (Linux; Android 10; SM-M107F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Moto G (5) Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 4.1.2; SAMSUNG-SGH-I467 Build/JZO54K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.107 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; HiDPTAndroid Build/KOT49H)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Mattermost/4.2.3 Chrome/61.0.3163.100 Electron/2.0.12 Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 5.1.1; KFSUWI Build/LVY48F; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Safari/537.36 OPR/27.0.2254.118423',
'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.11.4.5116',
'Mozilla/5.0 (Linux; Android 10; SM-A013M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; TECNO KB7 Build/O11019)',
'Mozilla/5.0 (Linux; Android 5.1.1; KFSUWI) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; LM-X210APM) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N981U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.120 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; motorola one fusion) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; XQ-AT51 Build/58.1.A.5.55)',
'Dalvik/2.1.0 (Linux; U; Android 8.1; T28 Build/MRA58K)',
'Scrapy/2.4.1 (+https://scrapy.org)',
'Mozilla/5.0 (Linux; Android 6.0.1; ZUK Z2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; CPH1923 Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-N910C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Lenovo K33a48) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Aquaris U2 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G970F Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; MI CC 9 MIUI/V10.3.0.1.PFCMIXM)',
'Mozilla/5.0 (Linux; Android 9; Redmi 7A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; M2006C3MG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; vivo 1915) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0 SeaMonkey/2.53.4',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G600FY Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ONEPLUS A3000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-J500M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 4a (5G)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; MS50X Build/V11_20190306)',
'Mozilla/5.0 (Linux; arm; Android 9; SM-J530FM) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.96 YaBrowser/20.4.1.144.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Ixion ES950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Mi A2 MIUI/V11.0.2.0.PDCCNXM)',
'Mozilla/5.0 (Linux; Android 11; SM-G781B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'WordPress/5.6.1; https://dssdemowoo.000webhostapp.com',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; CT-88 Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 6.0.1; ASUS_Z00LD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Opera/9.80 (MAUI Runtime; Opera Mini/4.4.39016/174.101; U; ru) Presto/2.12.423 Version/12.16',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; MS9 Build/O11019)',
'Mozilla/5.0 (Linux; arm; Android 9; SM-A600FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.96 YaBrowser/20.4.1.144.00 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Joy 1+ Build/PKQ1.190414.001)',
'Mozilla/5.0 (Linux; arm_64; Android 9; Redmi Note 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.4.76.00 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Redmi 7 MIUI/V11.0.1.0.PFLTHAS)',
'Mozilla/5.0 (Linux; U; Android 8.1.0; in-id; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.80 Mobile Safari/537.36 HeyTapBrowser/15.7.6.1',
'Mozilla/5.0 (Linux; Android 10; SM-A750FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; moto g(6)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (iPad; CPU OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 10; SM-G975U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47',
'Mozilla/5.0 (Linux; Android 7.1.2) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1906 Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.66 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Lenovo TB-7305F Build/PPR1.180610.011)',
'Mozilla/5.0 (Linux; Android 9; Moto G4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; BV6800Pro_RU Build/O00623)',
'Mozilla/5.0 (Linux; Android 10; HRY-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 9.0; TS-M704A Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 10; SM-J810F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 8.1.0; en-US; CPH1809 Build/OPM1.171019.026) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/13.2.0.1296 (SpeedMode) U4/1.0 UCWEB/2.0 Mobile Safari/534.30',
'Mozilla/5.0 (Linux; Android 9; moto e6 Build/PCBS29.73-143-7-4; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/301.0.0.37.477;]',
'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.125 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; LDN-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SMART_TV Build/LMY47V)',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-A520F Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36 YaApp_Android/10.41 YaSearchBrowser/10.41',
'Mozilla/5.0 (Linux; Android 5.0.2; SM-A300F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; vivo 1920) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15,gzip(gfe)',
'Dalvik/2.1.0 (Linux; U; Android 9; CPH1825 Build/PPR1.180610.011)',
'Dalvik/2.1.0 (Linux; U; Android 6.0; ESP-01 Build/MRA58K)',
'Mozilla/5.0 (DirectFB; Linux armv7l) AppleWebKit/537.1+ (KHTML, like Gecko) Safari/537.1',
'Mozilla/5.0 (Linux; Android 7.0; SM-G950U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G965W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1; TX9 Build/NHG47L; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; itel S11Plus Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J260FU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; ALIGATOR S6000 Build/O11019)',
'Mozilla/5.0 (Linux; Android 10; CPH2239) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Lenovo P2a42) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; GM1917) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A530W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1819) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; 9025Q Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 8.1.0; DUB-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G9700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; ANE-LX2J) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.30 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Cortana 1.14.2.19041; 10.0.0.0.19043.1288) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19043',
'Mozilla/5.0 (Linux; Android 10; moto e(7) plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; G20 Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 11; SM-A725F Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Ugoos-AM3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-A500F Build/KTU84P)',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; LG-D686 Build/KOT49I.D68620b)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 DuckDuckGo/7 Safari/605.1.15',
'safarifetcherd/604.1 CFNetwork/1240.0.4 Darwin/20.6.0',
'Mozilla/5.0 (Linux; Android 10; SH-RM11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; CPH1907) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-N950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; BQ-5518G Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36 YaApp_Android/10.70 YaSearchBrowser/10.70',
'Mozilla/5.0 (Linux; Android 10; Live 4 Build/QKQ1.200428.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.90 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N920L Build/LMY47X)',
'Mozilla/5.0 (Linux; Android 10; moto e(7) power Build/QOL30.288-19; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-H930 Build/OPR1.170623.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J415F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 4.2.2; Worktab Q10 Build/JDQ39) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.111 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2010J19CG MIUI/V12.0.8.0.QJFIDXM)',
'Mozilla/5.0 (Linux; Android 8.0.0; ASUS_Z012DC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 OPR/58.2.2878.53403',
'Dalvik/2.1.0 (Linux; U; Android 5.1; P2M Build/LMY47I)',
'Mozilla/5.0 (Linux; Android 7.1.2; vivo 1719 Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/6.0.0.7',
'Dalvik/2.1.0 (Linux; U; Android 6.0; HAMMER_ENERGY Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 9; SM-A605G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; LM-X210(G)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-M205F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; GM1900 Build/QKQ1.190716.003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; arm_64; Android 7.0; U11_Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; T02 Build/LMY47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-N986U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.20 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J600FN Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-J600G Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/9.2 Chrome/67.0.3396.87 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-N976N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 6.0; cs-cz; 5044Y Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 8.0.0; SAMSUNG SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; HTC Desire 12s Build/OPM1.171019.011)',
'Mozilla/5.0 (Linux; Android 9; Redmi 7A Build/PKQ1.190319.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36 YaApp_Android/10.90 YaSearchBrowser/10.90',
'Mozilla/5.0 (Linux; Android 5.1; Lenovo P70-A otido2010 for 4pda Build/LMY47D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; M7sLite Build/V9_20200907)',
'&quot;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 146.0.0.21.122 (iPhone10,2; iOS 13_5_1; en_NZ; en-NZ; scale=2.61; 1080x1920; 220223664)&quot;',
'Mozilla/5.0 (Linux; Android 7.0; SM-G935F Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36 Viber/13.1.0.4',
'Mozilla/5.0 (Linux; Android 9; Redmi 6A Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; Android 7.0; SM-A310F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; HD1903 Build/QKQ1.190716.003)',
'Mozilla/5.0 (iPad; CPU OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/72.0.3626.101 Mobile/15E148 Safari/605.1',
'Mozilla/5.0 (Linux; Android 10; moto g(7) play) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; CPH1933) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J320F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36,gzip(gfe),gzip(gfe)',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Phantom P2 Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 10; SM-A300FU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0.1; LG-H342 Build/LRX21Y)',
'Dalvik/2.1.0 (Linux; U; Android 12; Mi 9T Pro Build/SP1A.210812.016)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 YaBrowser/21.9.1.684 Yowser/2.5 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.0; 9020A Build/LRX21M)',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.14; rv:75.1) Gecko/20100101 Firefox/75.1',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A215U1) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Mi Note 10 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SM-J701M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; CLT-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 9; uz-uz; Redmi 6 Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.5.2-go',
'Mozilla/5.0 (Linux; Android 10; moto g(7)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.165 (Edition utorrent)',
'Mozilla/5.0 (Linux; Android 9; cp3705AS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Redmi Y2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; HR6081 Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 9; SM-G950F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.110 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/294.0.0.39.118;]',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-C5000 Build/MMB29M)',
'Mozilla/5.0 (Linux; Android 10; H8416) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1878.0 Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 EdgiOS/45.11.1 Mobile/15E148 Safari/605.1.15',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.4.3991.125 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40',
'Mozilla/5.0 (Linux; Android 9; SM-T290 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/85.0.4183.127 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; Lenovo A6020l36 Build/LMY47V)',
'Mozilla/5.0 (Linux; Android 7.0; Infinix HOT 4 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J700F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-T585 Build/M1AJQ; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/73.0.3683.90 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G935F Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G570M Build/R16NW; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; moto g(7) optimo maxx(XT1955DL) Build/QPOS30.85-21-5)',
'Mozilla/5.0 (Linux; Android 7.1.1; ASUS_Z01BDA) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; A33w) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; fi-fi; Redmi 9 Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.6.6-gn',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.30018 Safari/537.36 Sparrow',
'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.0.0 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; CLT-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 4.4.2; EVERCOSS_A74D Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; meizu note8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Windows; U; Windows NT 6.1; sv-SE) Gecko/20100101 Firefox/12.0',
'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-A207M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Plus-9_C778) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 6.1; Q88 Build/KOT49H)',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; MI 8 Lite MIUI/V10.2.2.0.ODTMIXM)',
'Mozilla/5.0 (Linux; Android 7.0; Infinix S2 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; Redmi K20 Pro MIUI/20.6.17)',
'Mozilla/5.0 (Linux; Android 9; FLA-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Flare_A2 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1910) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G950F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.91 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Venus_R9 Build/MRA58K)',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.165 (Edition Campaign 76)',
'Mozilla/5.0 (Linux; Android 9; Mi A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J701F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-I9060 Build/JDQ39)',
'Mozilla/5.0 (Linux; Android 10; LM-V500N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia 2.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53',
'Mozilla/5.0 (Linux; Android 11; Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; KFTRWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/92.2.11 like Chrome/92.0.4515.159 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Moto Z (2)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.18 Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 9; es-us; Redmi Note 8 Build/PKQ1.190616.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.7.4-gn',
'Mozilla/5.0 (Linux; Android 11; AC2003 Build/RP1A.201005.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; B9502 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 4.4.2; LenovoA3300-HV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4130.0 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A105FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MAR-LX1B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 AVG/94.0.12328.73,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 10; Z30) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 10; SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaApp_Android/11.30 YaSearchBrowser/11.30 BroPP/1.0 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 6.0; Cosmos_V9 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36 PHX/4.9',
'Mozilla/5.0 (Linux; Android 10; AC2001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; A890 Build/Q00711; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.93 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; C5502 Build/10.5.1.A.0.283)',
'Mozilla/5.0 (Linux; Android 8.1.0; Lenovo L38041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; motorola one hyper Build/QPFS30.103-59-5)',
'Mozilla/5.0 (Linux; Android 5.1; T02) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SAMSUNG SM-A720F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.0 Chrome/79.0.3945.136 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; Vibe K5 Plus Build/OPM2.171019.029.B1)',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; DEXP Shell HV320WHB-N85 Build/KTU84P)',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G570F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; H96Max RK3318) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-M515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 11; Mi Note 10 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 YaBrowser/21.2.1.108.00 SA/3 TA/7.1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-X430 Build/QKQ1.200730.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; E7 Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 6.0.1; SAMSUNG SM-G610Y) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.1 Chrome/79.0.3945.136 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; W7413B Build/LMY47V)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 LightSpeed [FBAN/MessengerLiteForiOS;FBAV/268.1.0.62.114;FBBV/219555470;FBDV/iPhone6,2;FBMD/iPhone;FBSN/iOS;FBSV/12.4.7;FBSS/2;FBCR/;FBID/phone;FBLC/sk_SK;FBOP/0]',
'Dalvik/2.1.0 (Linux; U; Android 7.0; Moto G (5) Build/NPP25.137-76)',
'Mozilla/5.0 (Linux; Android 8.1.0; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.120 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; XT1021 Build/LPC23.13-34.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; PSP5530DUO Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36 YaApp_Android/9.05 YaSearchBrowser/9.05',
'Mozilla/5.0 (Linux; Android 10; SM-A105M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 7.0; MI MAX) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Nokia C2 Tennen) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4166.0 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; IN2013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; Infinix X509 Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 10; SM-A507FN) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/83.0.316 Mobile Chrome/77.0.3865.316 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A600FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; A70 Build/RP1A.201005.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N960W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; vivo 1901) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; moto g(6) plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SM-J530F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; moto e6s Build/POBS29.288-60-6-1-12; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; moto g(8) power lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; KFGIWI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/58.2.2878.53403',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2006C3LVG MIUI/V12.0.10.0.QCDEUXM)',
'Mozilla/5.0 (Linux; Android 11; Mi MIX 2S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 7.1.2; Redmi 4X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 YaBrowser/20.8.3.71.00 SA/1 TA/7.1 Mobile Safari/537.36',
'Instagram 143.0.0.20.122 (iPhone11,2; iOS 13_4_1; en_US; en-US; scale=3.00; 1125x2436; 216064945) AppleWebKit/420+',
'Mozilla/5.0 (Linux; Android 9; Infinix X627) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J260M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SHV45-u) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; V1930 Build/RP1A.200720.012)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36/3ksI6CtQ-58',
'Dalvik/2.1.0 (Linux; U; Android 10; Infinix X682C Build/QP1A.190711.020)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1; rv:78.0) Gecko/20100101 Firefox/78.0',
'Dalvik/2.1.0 (Linux; U; Android 7.0; Lenovo K33b36 Build/NRD90N)',
'Mozilla/5.0 (Linux; Android 10; ASUS_I01WD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; motorola one 5G UW Build/QPNS30.37-Q3-42-40-7-2)',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-US998) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.114 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; CPH1853) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; ANE-LX2 Build/HUAWEIANE-LX2)',
'Mozilla/5.0 (Linux; Android 8.0.0; F8131) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; STF-L09 Build/HUAWEISTF-L09; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; L590A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A505F Build/QP1A.190711.020; en-gb) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36 Puffin/8.3.1.41624AP',
'Mozilla/5.0 (Linux; arm_64; Android 9; Redmi 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 YaApp_Android/10.93 YaSearchBrowser/10.93 BroPP/1.0 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; A33w Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36',
'Opera/9.80 (J2ME/MIDP; Opera Mini/8.0.35626/176.145; U; ru) Presto/2.12.423 Version/12.16',
'Mozilla/5.0 (Linux; Android 11; SM-A505GN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Redmi Note 9S Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.115 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G930K Build/NMF26X)',
'Dalvik/2.1.0 (Linux; U; Android 5.0; BLU ENERGY X PLUS Build/LRX21M)',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; moto e5 supra Build/OCPS27.91-164-1)',
'Mozilla/5.0 (iPad; CPU OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; SM-G530H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; LG-D852) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-P610 Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; IN2023 Build/QQ3A.200805.001)',
'Dalvik/2.1.0 (Linux; U; Android 10; M2007J3SC MIUI/V12.0.5.0.QJDCNXM)',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; SM-G850K Build/LRX22G)',
'Mozilla/5.0 (Linux; Android 4.4.4; SM-J110L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SLA-L23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A102W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J701F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A805F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 9; id-id; Redmi Note 8 Pro Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g,gzip(gfe)',
'Mozilla/5.0 (Linux; Android 9; SM-J610FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; POT-LX1 Build/HUAWEIPOT-LX1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.83 Mobile Safari/537.36 hola_android',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; Tablet PC 2.0; Zoom 3.6.0; Microsoft Outlook 14.0.7248; ms-office; MSOffice 14)',
'RubyBrowser/45.9.18 (iPhone; iOS 13.7; Scale/2.00)',
'Mozilla/5.0 (Linux; Android 7.0; SM-N920G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 11; zh-cn; M2007J3SC Build/RKQ1.200826.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.116 Mobile Safari/537.36 XiaoMi/MiuiBrowser/15.3.4',
'Mozilla/5.0 (Linux; Android 10; SM-G960F Build/QP1A.190711.020; Cake) AppleWebKit/537.36 (KHTML, like Gecko) Version/6.0.27 Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android Marshmallow; AG-02 Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 11; SM-G981U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; HMA-TL00 Build/HUAWEIHMA-TL00)',
'Mozilla/5.0 (Linux; U; Android 8.1.0; ru-ru; MI 6X Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-T805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 9; SM-J400F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 YaApp_Android/10.93 YaSearchBrowser/10.93 BroPP/1.0 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.0 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; LT C2200 Build/O11019)',
'Mozilla/5.0 (Linux; Android 6.0; CITI 1511 3G CT1117PG Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.91 Safari/537.36',
'WordPress/5.4.2; https://goload.ru',
'Mozilla/5.0 (Linux; Android 9; MIX 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4165.0 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-A705MN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.4) Gecko/20100101 Firefox/68.4',
'Mozilla/5.0 (Linux; Android 9; SM-J730F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36 OPR/62.0.3146.57357',
'Mozilla/5.0 (Linux; Android 10; SM-T510 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SOV36 Build/47.1.C.0.474; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 YJApp-ANDROID jp.co.yahoo.android.yjtop/3.71.2',
'Mozilla/5.0 (Linux; Android 10; SO-02L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; LG-H700 Build/OPM1.171019.026)',
'Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-A310F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.0 Chrome/79.0.3945.136 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; SH-02M Build/S5110)',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47',
'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 YaBrowser/20.8.1.79 Yowser/2.5 Yptp/1.23 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4A Build/N2G47H; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36 Viber/13.1.0.4',
'Mozilla/5.0 (Linux; Android 10; SM-M3070) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; vivo 1915) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A115AZ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Opera/9.80 (Android 7.0; Opera Mini/36.2.2254/119.132; U; id) Presto/2.12.423 Version/12.16',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G900T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 8.1.0; DRA-LX5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MI 8 Lite) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.232 Whale/2.10.124.26 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-J327P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Opera/9.80 (Android; Opera Mini/47.2.2254/174.101; U; uk) Presto/2.12.423 Version/12.16',
'Mozilla/5.0 (Linux; Android 10; YAL-AL00; HMSCore 4.0.4.307; GMSCore 19.6.29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 HuaweiBrowser/10.1.2.300 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N960N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; LM-Q620) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24/kkwNgUYA-24',
'Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
'Mozilla/5.0 (Linux; Android 9; CPH1859) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.1; KIW-AL10 Build/HONORKIW-AL10)',
'Mozilla/5.0 (Linux; Android 8.1.0; vivo 1802) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-E700F Build/LMY47X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; vivo 1723 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36 GoogleApp/11.9.16.21.arm64',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; MIX) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; M2006C3MG MIUI/V12.0.10.0.QCRIDXM)',
'Mozilla/5.0 (Linux; Android 10; SM-G981N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-J400M Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; BLU NEO X Build/N070)',
'Mozilla/5.0 (Linux; Android 9; MRD-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36,gzip(gfe),gzip(gfe)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone9,3;FBMD/iPhone;FBSN/iOS;FBSV/13.7;FBSS/2;FBID/phone;FBLC/en_GB;FBOP/5]',
'Mozilla/5.0 (Linux; arm_64; Android 10; STK-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.2.101.00 SA/1 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; SM-A205U1 Build/PPR1.180610.011)',
'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.4732.1445 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Nokia 3.1 A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.06.4.5042',
'Dalvik/2.1.0 (Linux; U; Android 10; REVVLRY Build/QPYS30.85-18-9-10)',
'Mozilla/5.0 (Linux; Android 9; Redmi 6A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; M2101K9G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36 OPR/66.0.3425.61578',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; ATU-L22 Build/HUAWEIATU-L22)',
'Mozilla/5.0 (Linux; Android 10; BV4900Pro Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.166 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 6.0; itel S11Plus Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 OPR/50.0.2254.149182',
'Mozilla/5.0 (Linux; Android 10; LM-Q730) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/46.02.4.5147',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-T365M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; I3312) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.165,gzip(gfe)',
'Dalvik/2.1.0 (Linux; U; Android 10; SM-G900M Build/QQ3A.200705.002)',
'Dalvik/1.6.0 (Linux; U; Android 4.1.2; GT-I8260L Build/JZO54K)',
'Mozilla/5.0 (Linux; Android 10; V2026 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; Z1 Build/NRD90M)',
'Dalvik/2.1.0 (Linux; U; Android 10; SM-A600F Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A305G) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; MI PAD 4 MIUI/10.0.5.0)',
'Mozilla/5.0 (Linux; Android 6.0; BV7000 PRO Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.1b4) Gecko/20090423 Firefox/52.4.0',
'Mozilla/5.0 (Linux; Android 7.0; Moto G (5)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.67 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; LG-M200 Build/OPM1.171019.026)',
'Mozilla/5.0 (Linux; Android 6.0; SP6.2_Lite Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.98 Mobile Safari/537.36 Viber/12.7.5.1',
'Mozilla/5.0 (Linux; Android 9; SM-A105G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.3; Microsoft Outlook 15.0.5233; ms-office; MSOffice 15)',
'Mozilla/5.0 (Linux; Android 10; SM-M205G Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; TECNO KF8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Pixel 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; wbx 1.0.0; Zoom 3.6.0; Microsoft Outlook 15.0.5215; ms-office; MSOffice 15)',
'com.google.GoogleMobile/111.0 iPad/13.3 hw/iPad6_4',
'Mozilla/5.0 (Linux; Android 10; Infinix X680) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2678.35 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; BKL-AL20; HMSCore 6.1.0.305; GMSCore 20.15.16) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 HuaweiBrowser/11.1.4.301 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 11; en-US; CPH1911 Build/RP1A.200720.011) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/13.3.5.1304 (SpeedMode) U4/1.0 UCWEB/2.0 Mobile Safari/534.30',
'Mozilla/5.0 (Linux; Android 11; CPH1919 Build/RKQ1.200928.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64; rv:68.9) Gecko/20100101 Goanna/4.7 Firefox/68.9 PaleMoon/28.15.0',
'Mozilla/5.0 (Linux; Android 7.0; vivo 1612 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36 VivoBrowser/6.3.0.6',
'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.102 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
'Dalvik/2.1.0 (Linux; U; Android 6.0; X-Play Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 4.4.2; HTC Desire 526G dual sim) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 OPR/58.2.2878.53403',
'Mozilla/5.0 (Linux; Android 6.0; LG-H960) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; S7C Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-LS993) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-N960W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; iSWAG Lynx plus Build/LMY47I)',
'Mozilla/5.0 (iPad; CPU OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.60 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 11; CPH2025) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-T865) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.3; N9835 Build/JLS36C)',
'Mozilla/5.0 (Linux; Android 10; LM-K300 Build/QKQ1.200108.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.82 Mobile Safari/537.36 EdgW/1.0',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-G981U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.0 Chrome/79.0.3945.136 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; M2007J3SY Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36 EdgA/95.0.1020.55',
'Mozilla/5.0 (Linux; Android 10; M2006C3LG Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1; LG-X210 Build/LMY47I) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.105 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; Android 11; F-52A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.2; SM-A310F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; i5C Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 7.0; SM-G9287) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi 7A Build/QKQ1.191014.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; LG-X230) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9.0.0; TVBOX Build/NHG47K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Safari/537.36',
'com.google.GoogleMobile/46.0.0 iPhone/13.5.1 hw/iPhone9_3',
'Dalvik/2.1.0 (Linux; U; Android 10; MI A3 MIUI/12.0.3.0)',
'Mozilla/5.0 (Linux; Android 10; vivo 1804) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; SM-A705MN Build/RP1A.200720.012)',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-G988B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; SM-J410G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; itel A16 Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; Coolpad R108 Build/LMY47V)',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G920X Build/LMY47X)',
'Mozilla/5.0 (Linux; Android 8.1.0; LG-M700) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; CLIK Build/O11019)',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; MS-AC71 Build/MOB31E)',
'Mozilla/5.0 (Linux; Android 10; SM-G975U1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36 OPR/58.2.2878.53403',
'Dalvik/2.1.0 (Linux; U; Android 5.0.2; HTC Desire 816 Build/LRX22G)',
'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; V2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G600FY Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MAR-LX2 Build/HUAWEIMAR-L22B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.164 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; Moto G (5) Plus Build/NPN25.137-78)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81',
'Mozilla/5.0 (Linux; Android 8.0.0; HUAWEI NXT-AL10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MED-LX9N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G9650) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; SM-T727V Build/PPR1.180610.011)',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.0.04506; Media Center PC 5.1)',
'Mozilla/5.0 (Linux; Android 6.0.1; ASUS_X009DD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; Lenovo K33a42) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/11.2 Chrome/75.0.3770.143 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; moto e5 Build/OPPS27.91-176-11-16; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; motorola one Build/QPKS30.54-22-7)',
'Dalvik/2.1.0 (Linux; U; Android 7.0; SENSE Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; SM-G955F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; ALE-L21 Build/HuaweiALE-L21; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Infinix X571) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Apache-HttpClient/4.5.2 (Java/1.7.0_312)',
'Mozilla/5.0 (Linux; Android 8.0.0; XT1635-01) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; SM-T710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; thor Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.119 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; Android 8.0.0; G8441) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36/n6Os0imJ-33',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36 Edg/89.0.774.45',
'Dalvik/2.1.0 (Linux; U; Android 5.1; PGN606 Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 7.0; CUBOT KING KONG Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/64.0.3282.137 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; TV BOX Build/QP1A.191105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.186 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1; iris560 Build/LMY47D)',
'Mozilla/5.0 (Windows NT 10.0; Cortana 1.13.0.18362; 10.0.0.0.18363.900) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
'Mozilla/5.0 (Linux; Android 7.0; SM-J327T1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; B450) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J510MN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; CPH2217) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; V1945A Build/PKQ1.190626.001)',
'Mozilla/5.0 (Linux; Android 7.1.1; MI MAX 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.110 Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; M2007J20CI) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Redmi Note 8T Build/PKQ1.190616.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.132 Mobile Safari/537.36 Viber/13.1.0.4',
'Mozilla/5.0 (Linux; Android 8.0.0; SAMSUNG SM-G930P) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-P601) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; HARRY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; E435 Lite Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 8.1.0; N5002L Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.0; LGMP450) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:82.0) Gecko/20100101 Firefox/82.0',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; R6 PLUS Build/PPR1.180610.011)',
'Dalvik/1.6.0 (Linux; U; Android 4.4.2; G-TiDE A3 Build/KOT49H)',
'Mozilla/5.0 (Linux; Android 8.1.0; LM-X210APM) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; GM1901) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; G3121 Build/48.1.A.2.21)',
'Mozilla/5.0 (Linux; Android 10; M2006C3MG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G986N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 11; SM-A205FN Build/RP1A.200720.012)',
'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 YaBrowser/18.4.0.565.00 (alpha) Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-N950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; moto e5 play) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; BLU ENERGY X PLUS 2 Build/E150Q)',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J3110 Build/LMY47X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.76 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; ASUS_Z012DA) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.3; PDT-900 Build/V1.74)',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.7) Gecko/20100101 Firefox/78.7',
'Dalvik/2.1.0 (Linux; U; Android 8.0.0; M8 Build/O00623)',
'Mozilla/5.0 (Linux; Android 6.0.1; Rombica_Cinema4K_v01) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
'Mozilla/5.0 (Linux; Android 6.0; PE-TL10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.93 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-N950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; CMR-W19) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.119 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Le X620 Build/HEXCNFN5902101081S)',
'Mozilla/5.0 (Linux; Android 6.0; BG2-W09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-N770F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Android 5.1; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0',
'Mozilla/5.0 (Linux; U; Android 7.0.0; zh-CN; MZ-PRO 6 Plus Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 MZBrowser/8.2.110-2020060117 UWS/2.15.0.4 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; M2007J3SY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Redmi S2 Build/PQ3A.190801.002)',
'Mozilla/5.0 (Linux; Android 9; ZTE Blade A7 2019RU) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54',
'Mozilla/5.0 (X11 TOS; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 ToGate/3.13.3.0 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-A530W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Mi A2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-G531H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4235.2 Mobile Safari/537.36,gzip(gfe),gzip(gfe) (Chrome Image Compression Service)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15G77 YaBrowser/19.5.2.38.10 YaApp_iOS/32.00 YaApp_iOS_Browser/32.00 Safari/604.1',
'Mozilla/5.0 (Linux; Android 10; SM-G970U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-J400F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Micromax Q352 Build/MRA58K)',
'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.96 Mobile DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; VS810PP) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'WordPress/5.7.2; https://www.missionhomebuyers.com',
'Mozilla/5.0 (Linux; Android 9; SM-J730G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; ar-eg; Mi 9T Pro Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.7.0-gn',
'Mozilla/5.0 (Linux; Android 4.4.4; GT-I9195I Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.128 Mobile Safari/537.36 (Ecosia android@69.0.3497.128)',
'Mozilla/5.0 (Linux; Android 7.1.1; SAMSUNG SM-J510H) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.2 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; M2101K9G Build/RKQ1.201112.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-T510) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36,gzip(gfe),gzip(gfe)',
'Mozilla/5.0 (Linux; Android 10; EML-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; Redmi Note 9S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 EdgiOS/46.3.30 Mobile/15E148 Safari/605.1.15',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; M7-3G-PLUS Build/V18_20200413)',
'Mozilla/5.0 (Linux; Android 10; M2004J19C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.77 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-T377T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J330FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4412.0 Safari/537.36 Edg/90.0.794.0',
'Mozilla/5.0 (Linux; Android 10; SM-A202F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.115 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; AOYODKG_A38 Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36',
'OperaMini(Fucus/Unknown;Opera Mini/4.4.33576;en)',
'Mozilla/5.0 (Linux; Android 11; M2004J19C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; VFD 528) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm; Android 7.1.1; SM-J510FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.90.00 SA/1 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 8.1.0; Redmi 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.90.00 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 OPR/74.0.3911.107 (Edition Campaign 34)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 EdgiOS/46.2.5 Mobile/15E148 Safari/605.1.15',
'Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36 OPR/63.1.3216.58539',
'Mozilla/5.0 (Linux; Android 10; SM-G977U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; BLA-AL00 Build/HUAWEIBLA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2693 MMWEBSDK/201001 Mobile Safari/537.36 MMWEBID/729 MicroMessenger/7.0.20.1781(0x27001439) Process/toolsmp WeChat/arm64 NetType/WIFI Language/zh_CN ABI/arm64',
'Dalvik/2.1.0 (Linux; U; Android 7.1.2; RCT6973W43R Build/NHG47K)',
'Mozilla/5.0 (Linux; Android 7.0; Power_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-S260DL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; Redmi 8 MIUI/V11.0.4.0.PCNIDXM)',
'Mozilla/5.0 (Linux; Android 10; moto g(7) plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; MI MAX 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-N986U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36 OPR/62.3.3146.57763',
'Mozilla/5.0 (Linux; Android 8.0.0; G3226) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MED-LX9 Build/HUAWEIMED-LX9; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36 HuaweiBrowser/11.1.4.302 HMSCore/5.3.0.312',
'Dalvik/2.1.0 (Linux; U; Android 9; MI MAX 3 MIUI/V10.3.1.0.PEDCNXM)',
'Mozilla/5.0 (Linux; Android 6.0.1; vivo 1606) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.141 Mobile Safari/537.36',
'GuzzleHttp/6.5.3 curl/7.58.0 PHP/7.2.30-1+ubuntu18.04.1+deb.sury.org+1',
'Mozilla/5.0 (Linux; Android 7.0; X30) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.6.1.151 Yowser/2.5 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 10; COVET_PRO_LITE Build/QP1A.190711.020)',
'Dalvik/2.1.0 (Linux; U; Android 10; M2004J19C MIUI/V11.0.6.0.QJCIDXM)',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-C701F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; es-es; MI 8 Build/QKQ1.190828.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 Mobile Safari/537.36 XiaoMi/Mint Browser/3.4.7',
'Mozilla/5.0 (Linux; Android 9; SM-J260A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; EVR-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Lenovo A6020l36 Build/MMB29M)',
'Mozilla/5.0 (Linux; Android 10; RMX2111) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.80 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-A600FN Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Mozilla/5.0 (Linux; U; Android 6.0.1; id-id; Redmi 4 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.2.6-g',
'Mozilla/5.0 (Linux; Android 11; Redmi Note 9 Pro Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.71 DuckDuckGo/5 Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; SM-J250F Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36 YaApp_Android/10.91 YaSearchBrowser/10.91',
'Dalvik/2.1.0 (Linux; U; Android 10; SM-M105M Build/QP1A.190711.020)',
'Mozilla/5.0 (Linux; Android 7.0; Easy-Power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; LG-H873) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.99 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-T860) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.1 Chrome/79.0.3945.136 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; MI MAX 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 9; GM1917 MIUI/V11.0.5.0.PFGMIXM)',
'Mozilla/5.0 (Linux; Android 10; CLT-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.101 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.2.2; Primo-GH2 Build/JDQ39)',
'Mozilla/5.0 (Linux; Android 10; HD1925) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.257 (beta) Yowser/2.5 Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; F3113 Build/33.3.A.1.126)',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-G610Y) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.4.3991.125 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; CPH1923) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.81 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1; K109 Build/LMY47D)',
'Mozilla/5.0 (Linux; Android 6.0.1; SM-J320VPP) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; City Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; SM-T295) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; Impress_Life) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.0.0; SM-G935T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J500G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; HD1925 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.156 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 5.1.1; Alcatel_5056O Build/LMY47V)',
'Mozilla/5.0 (Linux; Android 10; RMX1801) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 6.0; Attila_P30 Build/MRA58K)',
'Mozilla/5.0 (Linux; U; Android 10; en-US; Mi A3 Build/QKQ1.190910.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/13.2.0.1296 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; BE2025) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 7.1.1; CPH1717) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; Moto Z (2) Build/PCX29.159-21-3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; ASUS_X00TD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-G965W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 8.1.0; BBB100-1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 8.1.0; K100 Build/O11019)',
'Dalvik/1.6.0 (Linux; U; Android 4.4; NB7022S Build/KRT16S)',
'Mozilla/5.0 (Linux; Android 11; ASUS_I006D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36 OPR/64.3.3282.60839',
'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.0 Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-M315F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; itel L5002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36',
'Dalvik/1.6.0 (Linux; U; Android 4.4.4; HUAWEI ALE-CL00 Build/HuaweiALE-CL00)',
'Dalvik/2.1.0 (Linux; U; Android 10; Pixel 4 Build/QQ3A.200805.001)',
'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4404.89 Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SM-J320FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A105FN Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-J337VPP) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; KFONWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/86.3.23 like Chrome/86.0.4240.198 Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SM-N950U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.86 Mobile Safari/537.36',
'Mozilla/5.0 (iPad; CPU OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/120.1.326106974 Mobile/15E148 Safari/604.1',
'Mozilla/5.0 (Linux; Android 8.0.0; moto e5 plus Build/OCPS27.91-32-15-18; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 11; SM-G996B Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-A205GN) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/11.2 Chrome/75.0.3770.143 Mobile Safari/537.36',
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.2; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; Tablet PC 2.0; MARKANYREPORT#25105; wbx 1.0.0; wbxapp 1.0.0)',
'Mozilla/5.0 (Linux; Android 10; U705AA) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.62 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.1.1; SAMSUNG SM-J320G) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/11.2 Chrome/75.0.3770.143 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; U; Android 10; en-US; SM-N975F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 UCBrowser/13.3.2.1303 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; arm_64; Android 6.0; E5533) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.3.90.00 SA/1 Mobile Safari/537.36',
'Dalvik/2.1.0 (Linux; U; Android 7.0; M651G Build/NRD90M)',
'Mozilla/5.0 (Linux; Android 9; FIG-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; Redmi Note 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36 OPR/60.3.3004.55692',
'Safari/15610.1.28.1.9 CFNetwork/1128.0.1 Darwin/19.6.0 (x86_64)',
'Mozilla/5.0 (Linux; Android 9; moto g(8) plus Build/PPI29.65-43; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36',
'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/186.1.410104828 Mobile/15E148 Safari/604.1',
]