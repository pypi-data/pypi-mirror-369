"""	
Aqui você encontrará algumas funções utilizando Regex

Se necessário, colaborem =)
"""

########### imports ##############
import re
from payconpy.fpython.fpython import *
########### imports ##############

def extrair_datas_re_input(text: str, pattern: str) -> str:
    """### Retorna datas no padrão escolhido

    Args:
        text (str): texto que tem datas
        pattern (str): pattern regex -> \d{2}.\d{2}.\d{4}|\d{2} por exemplo

    Returns:
        list: data(s)
    """
    datas = re.findall(pattern, text.lower())    
    if not datas or len(datas) == 0:
        datas = []
    return datas

def extrair_cpfs(text :str) -> list:
    """### Recupera CPF's

    Args:
        text (str): texto que vem o(s) cpf(s)

    Returns:
        list: cpf(s)
    """
    cpfs = re.findall("\d{3}.\d{3}.\d{3}-\d{2}", text)
    if not cpfs or len(cpfs) == 0:
        cpfs = re.findall("\d{3}.\d{3}.\d{3} -\d{2}", text)
        if cpfs and len(cpfs) > 0:
            a_cpfs = cpfs
            cpfs = []
            for a_cpf in a_cpfs:
                cpf = ''.join(i for i in a_cpf if i.isdigit()
                                or i in ['.', '-'])
                text = text.replace(a_cpf, cpf)
                cpfs.append(cpf)
    if not cpfs or len(cpfs) == 0:
        cpfs = []
    return cpfs


def recupera_numero_sem_nenhum_caractere(string):
    nums_list = re.findall('\d', string)

    num  = ''

    for n in nums_list:
        num = num+n
    return num


def extrair_email(text: str) -> list:
    """### Retorna os e-mails recuperados
    Validação / Busca de e-mails com o padrão RFC2822
    https://regexr.com/2rhq7

    Args:
        text (str): Texto com o(s) email(s)
    Returns:
        list: email(s)
    """
    email = re.findall("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", text, )
    if not email or len(email) == 0:
        email = []
    return email

def remove_caracteres_de_string():
    """Função remove esses elementos da string
    
    '.'
    
    '/'
    
    ','
    
    '-'
    
    '_'
    
    '='
    
    '|'
    
    '#'
    
    '`'
    
    '~'
    
    "'"
    
    '"'
    
    ';'
    
    'string'.strip()
    #### Função já converte o argumento para str()

    Args:
        string (str): str com os caracteres

    Returns:
        str: Retorna string sem nenhum desses caracteres
    """
    string = str(string)
    string = string.replace('.','')
    string = string.replace('/', '')
    string = string.replace(',', '')
    string = string.replace('-', '')
    string = string.replace('_', '')
    string = string.replace('=', '')
    string = string.replace('|', '')
    string = string.replace('`', '')
    string = string.replace('~', '')
    string = string.replace("'", '')
    string = string.replace('"', '')
    string = string.replace('#', '')
    string = string.replace(';', '')
    string = string.replace(':', '')
    string = string.strip()
    return string


# def extrair_numeros(str, return_first=True) -> list[str]|str:
#     """Recupera somente números de uma string

#     Args:
#         str (string): string com os números
#         return_first (bool, optional): retorna o primeiro conjunto de números. Defaults to True.

#     Returns:
#         list|str: lista com os números ou ou uma string com os números
#     """
#     if return_first:
#         return re.findall('\d+', str)[0]  # return str
#     else:
#         return re.findall('\d+', str) # return list


def extrair_num_processo(text: str, get_one=False, drop_duplicates=False) -> tuple|str:
    """Retorna os números de processos em um texto

    Args:
        text (str): texto do documento
        get_one (bool, optional): Recupera a primeira ocorrencia [0]. Defaults to False.
        drop_duplicates (bool, optional): Remove duplicados. Defaults to False.

    Returns:
        tuple|str: Dependendo da execução retorna uma lista tupla ou str, caso seja apenas o texto e remove_duplicates, será uma tupla, em outros casos uma string
    """
    if get_one: # retorna a primeira ocorrencia
        try:
            return tuple(set(re.findall("\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}", text)))[0]
        except IndexError:
            return tuple()
    if drop_duplicates:
        return tuple(set(re.findall("\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}", text)))
    else:
        return tuple(re.findall("\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4}", text))


def extrair_cnpjs(text: str, get_one=False, drop_duplicates=False) -> tuple|str:
    """### Recupera cnpj(s) da string

    Args:
        text (str): texto que pode haver cnpj(s)

    Returns:
        list: cnpj(s)
    """
    if drop_duplicates:
        return tuple(set(re.findall("\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}", text)))
    if get_one:
        try:
            return tuple(set(re.findall("\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}", text)))[0]
        except IndexError:
            return tuple()
    else:
        return tuple(re.findall("\d{2}.\d{3}.\d{3}\/\d{4}-\d{2}", text))


def extrair_datas(text: str, get_one=False, drop_duplicates=False) -> str:
    """### Retorna datas no padrão \d{2}/\d{2}/\d{4} -> 00/00/0000

    Args:
        text (str): texto que tem datas

    Returns:
        list: data(s)
    """
    if get_one: 
        try:
            return tuple(set(re.findall("\d{2}/\d{2}/\d{4}", text.lower())))[0]
        except IndexError:
            return tuple()
    if drop_duplicates:
        return tuple(set(re.findall("\d{2}/\d{2}/\d{4}", text.lower())))
    else:
        return tuple(re.findall("\d{2}/\d{2}/\d{4}", text.lower()))


def pega_id(assunto: str) -> str:
    """
    Essa função simplesmente pega uma string, separa ela por espaços e verifica se a palavra existe ou é igual a "ID",
        se existe, pega a string, caso seja igual, pega a string e um acima para pegar o id em si

    Args:
        assunto (str): Assunto do E-mail

    Returns:
        str | bool: Retorna o id com o número ou False se não tiver um assunto com ID
    """
    assunto = assunto.upper()
    assunto = assunto.strip()
    list_string_official = []
    if 'ID' in assunto:
        # Separa todos as strings por espaço
        assunto_list = assunto.split(' ')

        for i in range(len(assunto_list)):
            # se a palavra do assunto for id e a próxima palavra for 'elaw' pega id e o número
            if assunto_list[i] == 'ID' and assunto_list[i+1] == 'ELAW':
                list_string_official.append(assunto_list[i])
                list_string_official.append(assunto_list[i+2])
                id_ = ' '.join(list_string_official)
                faz_log(id_)
                return id_
            if assunto_list[i] == 'ID' and 'ELAW' in assunto_list[i+1]:
                list_string_official.append(assunto_list[i])
                try:
                    list_string_official.append(assunto_list[i+2])
                except Exception:
                    list_string_official.append(assunto_list[i+1])
                    id_ = ' '.join(list_string_official)
                    num_id = re.findall(r'\d+', id_)  # pega somente números da string
                    id_ = f'ID {num_id[0]}'#EX (ID 111111)#
                    faz_log(id_)
                    return id_
                id_ = ' '.join(list_string_official)
                faz_log(id_)
                return id_
            if assunto_list[i] == 'ID' or assunto_list[i] == 'ID:' or assunto_list[i] == 'ID.' or assunto_list[i] == '-ID':
                list_string_official.append(assunto_list[i])
                list_string_official.append(assunto_list[i+1])
                id_ = ' '.join(list_string_official)
                faz_log(id_)
                return id_
        else:
            faz_log(f'Não existe ID para o ASSUNTO: {assunto}', 'w')
            return False
    else:
        faz_log(f'Não existe ID para o ASSUNTO: {assunto}', 'w')
        return False

def extrair_ids(text: str) -> tuple[list, int]:
    """Extrair IDS do Elaw

    Args:
        text (str): texto que ter

    Returns:
        tuple[list, int]: _description_
    """
    ids = re.findall("id: \d+|id elaw\d+|id elaw \d+|id \d+|id - \d+", text, flags=re.IGNORECASE)
    if not ids or len(ids) == 0:
        ids = []
    return ids, len(ids)

def extrair_nome_do_arquivo_num_path(path_abs: str|list|tuple):
    """Extrai nome de um arquivo em um caminho absoluto
    
    Use:
        my_path: tuple|list = ('E:\\MyDocs\\.bin\\config.ini', 'E:\\MyDocs\\.bin\\data.db')
        return -> ['.bin', 'data.db']
        
        my_path: str = 'E:\\MyDocs\\.bin\\config.ini'
        return -> config.ini

    Args:
        path_abs (str): Caminho Absoluto

    Returns:
        list|str: um ou mais arquivos
    """
    if isinstance(path_abs, list) or isinstance(path_abs, tuple):
        for path_ in path_abs:
            files = [f.replace('\\', '') for f in re.findall(r'\\[a-z]*\.\w{2,3}', path_)]
        return files
    
    if isinstance(path_abs, str):
        pattern = re.findall(r'\\[a-z]*\.\w{2,3}', path_abs)
        return pattern[-1].replace('\\', '')
    
def formata_cpf_e_cnpj(nums_cpf_cnpj:str) -> str:
    """Formata um cpf e um cnpj
    Exemplo:
        cpf -> 00000000000 input
        cpf -> 000.000.000-00 output
        
        cnpj -> 00000000000100 input
        cnpj -> 00.000.000/0001-00 output

    Args:
        nums_cpf_cnpj (str): cnpj ou cpf

    Raises:
        IndexError: Quando nao for possível formatar

    Returns:
        str: cpf ou cnpj formatado
    """
    nums_cpf_cnpj = pega_somente_numeros(nums_cpf_cnpj)
    if len(nums_cpf_cnpj) == 11:
        return f'{nums_cpf_cnpj[0:3]}.{nums_cpf_cnpj[3:6]}.{nums_cpf_cnpj[6:9]}-{nums_cpf_cnpj[9:]}'
    elif len(nums_cpf_cnpj) == 14:
        return f'{nums_cpf_cnpj[0:2]}.{nums_cpf_cnpj[2:5]}.{nums_cpf_cnpj[5:8]}/{nums_cpf_cnpj[8:12]}-{nums_cpf_cnpj[12:]}'
    else:
        raise IndexError('len nums_cpf_cnpj != 11 or 14')