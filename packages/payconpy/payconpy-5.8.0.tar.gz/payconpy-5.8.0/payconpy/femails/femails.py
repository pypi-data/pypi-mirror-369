import platform
my_os = platform.system()

from payconpy.fregex.fregex import extrair_email
from payconpy.fpython.fpython import transforma_lista_em_string
from pretty_html_table import build_table
from email import encoders
from email.mime.base import MIMEBase
import os
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from payconpy.fpython.fpython import *
from payconpy.fregex.fregex import extrair_email
import smtplib
import win32com.client as win32

def enviar_email_outlook(to: list|str, assunto: str='Assunto do E-mail', body: str='<p>Olá!</p>', anexos :list|tuple|str|bool=False, enviar_dataframe_no_corpo: list|tuple|bool=False) -> None:
    """Função que envia e-mails via outlook (nativamente do sistema)
    ## É de suma importancia ter uma conta no Outlook
    ### É possível enviar 
    
    Args:
        to (list | str) -> lista ou string do(s) destinatário(s)
        
        assunto (str) -> Assunto do e-mail. Default is Assunto do E-mail
        
        body (str) -> Corpo do e-mail (preferível HTML) Default is <p>Olá!</p>
        
        anexos (list | tuple | str | bool=False) ->  Lista, tupla, ou string contendo o caminho do arquivo que será adicionado no e-mail (caso envie True sem enviar nada, ocorrerá erro!)
        
        enviar_dataframe_no_corpo (list | tuple | bool) -> Essa variável caso venha uma lista ou tupla será desempacotada na função build_table() do pretty_html_table. Então é possível enviar qualquer parametro na ordem da função. (caso envie True sem enviar nada, ocorrerá erro!)
        https://pypi.org/project/pretty-html-table/
        
        
    Returns:
        None
    """
    #--- Converte para string para verificação ---#
    emails = transforma_lista_em_string(to)
    emails = extrair_email(emails)
    
    if enviar_dataframe_no_corpo:
        # (df, 'theme_on_pretty_html_table')
        if isinstance(enviar_dataframe_no_corpo, list) or isinstance(enviar_dataframe_no_corpo, tuple):
            html_table = build_table(*enviar_dataframe_no_corpo)
            body = f"""{body}
            {html_table}"""

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    if isinstance(to, str):
        mail.To = to
    if isinstance(to, list) or  isinstance(to, tuple):
        mail.To = ";".join(emails)
    mail.Subject = assunto
    
    if anexos:
        if isinstance(anexos, str):
            mail.Attachments.Add(anexos)
        if isinstance(anexos, list) or isinstance(anexos, tuple):
            for anexo in anexos:
                mail.Attachments.Add(anexo)

    mail.HTMLBody = (body)
    try:
        mail.Send()
    except Exception as e:
        exception = str(e)
        if 'Verifique se você inseriu pelo menos um nome' in exception:
            print('Precisamos saber para quem enviar isto. Verifique se você inseriu pelo menos um nome.')
            return
        
    print('E-mail enviado com sucesso!')

def envia_email_gmail(
    email_app_google: str,
    passwd_app_gmail: str,
    emails_to: str|tuple|list,
    assunto: str,
    body_msg,
    anexos: tuple|list|bool = False,
    ):
    """Função para enviar um e-mail completo no Google Gmail
    
    ### Primeiramente, verifique se o email que enviará está configurado.
    
    Se não, siga o passo-a-passo abaixo para configurar o e-mail.
    ### Passo-a-passo para ativar envio de e-mails no Gmail
    1- Ative a verificação por duas etapas no Gmail: https://myaccount.google.com/signinoptions/two-step-verification
    
    2- Vá para esse link para criar uma senha de app: https://myaccount.google.com/apppasswords
        2a - Selecione App, E-mail
        2b - Selecione dispositivo, Outro (nome personalizado)
        2c - Capture a senha para adicionar na função.
        
    ### Dica para utilização de um body:
        Utilize template:
            file: template.html:
                <!DOCTYPE html>
                <html>
                <body>
                    <p>Olá <strong>$nome_placeholder</strong>, hoje é <strong>$data_placeholder</strong>.</p>
                </body>
                </html>
        >>> from string import Template
        >>> with open('template.html', 'r', encoding='utf-8') as html:
        >>>     template = Template(html.read())
        >>>     nome = 'Nome'
        >>>     data_atual = datetime.now().strftime('%d/%m/%Y')
        >>>     body_msg = template.substitute(nome_placeholder=nome, data_placeholder=data_atual)


    Args:
        email_app_google (str): E-mail que enviará para os destinatários, (emails_to)
        passwd_app_gmail (str): Passwd do E-mail que enviará para os destinatários, (emails_to)
        emails_to (str|tuple|list): Destinatário(s)
        assunto (str): Assunto do E-mail
        body_msg (str): Corpo do E-mail
        anexos (tuple | list | bool): Anexos, optional, default = False
    """

    msg = MIMEMultipart()

    # para quem está indo a msg
    if isinstance(emails_to, str):
        emails_to = extrair_email(emails_to)
        if len(emails_to) == 0:
            print(f'Não foi possível compreender o e-mail enviado: {emails_to}')
            return
    emails_to = ';'.join(emails_to)
    msg['to'] = emails_to

    # assunto
    msg['subject'] = assunto

    # corpo
    body = MIMEText(body_msg, 'html')
    msg.attach(body)

    # insere_os_anexos
    if isinstance(anexos, (tuple, list)):
        for anexo in anexos:
            anexo_abspath = os.path.abspath(anexo)
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(anexo_abspath, "rb").read())
            encoders.encode_base64(part)
            file_name = anexo_abspath.split("\\")[-1]
            print(f'Recuperando anexo: {file_name}')
            part.add_header(f'Content-Disposition', f'attachment; filename={file_name}')
            msg.attach(part)
    elif isinstance(anexos, str):
        anexo_abspath = os.path.abspath(anexos)
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(anexo_abspath, "rb").read())
        encoders.encode_base64(part)
        file_name = anexo_abspath.split("\\")[-1]
        print(f'Recuperando anexo: {file_name}')
        part.add_header('Content-Disposition', f'attachment; filename={file_name}')
        msg.attach(part)

    # abre conexao com smtp
    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        try:
            smtp.login(email_app_google, passwd_app_gmail)
        except smtplib.SMTPAuthenticationError as e:
            print(f'E-mail não enviado:\n\tUsuário ou senha inválido!\n\n{e.smtp_error}')
            return
        smtp.send_message(msg)
        print('E-mail enviado com sucesso!')