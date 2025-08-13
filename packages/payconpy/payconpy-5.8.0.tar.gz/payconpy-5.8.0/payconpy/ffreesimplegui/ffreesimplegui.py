"""
Funções de front-end para FreeSimpleGui

"""

import os
import sys
import FreeSimpleGUI as sg
from payconpy.fpython.fpython import *

########## For FreeSimpleGui ########
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller 
    
        SE QUISER ADICIONAR ALGO NO ROBÔ BASTA USAR ESSA FUNÇÃO PARA ADICIONAR O CAMINHO PARA O EXECUTÁVEL COLOCAR
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
########## For FreeSimpleGui ########


def popup_finalizado(text: str, title: str='Finalizado!', theme: str='Material1', autoclose: int=False, back_color: str='#E0E3E4', icon: str=False):
    import platform
    my_os = platform.system()
    if my_os.lower().strip() == 'windows':
        import winsound
        winsound.MessageBeep()
    
    sg.theme(theme)
    if isinstance(icon, str): 
        sg.popup_ok(text,
                    title=title,
                    auto_close=autoclose,
                    background_color=back_color,
                    icon=resource_path(icon),
                    )
    else:
        sg.popup_ok(text,
                    title=title,
                    auto_close=autoclose,
                    background_color=back_color,
                    )
        

def popup_erro(text: str, title: str='Erro', theme: str='Material1', autoclose: int=False, back_color: str='#E0E3E4', icon: str=False):
    import platform
    my_os = platform.system()
    if my_os.lower().strip() == 'windows':
        import winsound
        winsound.MessageBeep()

    sg.theme(theme)
    if isinstance(icon, str): 
        sg.popup_ok(text,
                    title=title,
                    auto_close=autoclose,
                    background_color=back_color,
                    icon=resource_path(icon),
                    )
    else:
        sg.popup_error(text,
                    title=title,
                    auto_close=autoclose,
                    background_color=back_color,
                    )
        

def popup_input(title: str, text: str, theme: str='Material1', back_color: str='#E0E3E4', icon: str=False, password_char=''):
    import platform
    my_os = platform.system()
    if my_os.lower().strip() == 'windows':
        import winsound
        winsound.MessageBeep()

    sg.theme(theme)
    if isinstance(icon, str): 
        return sg.popup_get_text(text,
                    title=title,
                    background_color=back_color,
                    icon=resource_path(icon),
                    password_char=password_char
                )
    else:
        return sg.popup_get_text(text,
                    title=title,
                    background_color=back_color,
                    password_char=password_char
                )

def popup_get_folder(title: str='Recuperar Pasta', text: str='Insira o caminho da pasta...', default_path=os.path.join(os.path.expanduser("~"), 'Downloads'), no_window=False, theme: str='Material1', back_color: str='#E0E3E4') -> str|None:
    """Popup para buscar pasta (Não arquivo)

    Args:
        title (str, optional): Titulo da janela. Defaults to 'Recuperar Pasta'.
        text (str, optional): Texto da janela (if no_window is False). Defaults to 'Insira o caminho da pasta...'.
        default_path (str, optional): Caminho padrão para o usuário visualizar. Defaults to os.path.join(retorna_home_user(), 'Downloads').
        no_window (bool, optional): Não mostrar a janela. Defaults to False.
        theme (str, optional): tema do FreeSimpleGui. Defaults to 'Material1'.
        back_color (str, optional): Cor de fundo. Defaults to '#E0E3E4'.

    Returns:
        (str|None): Caminho ou None caso não encontre ou não selecione
    """
    
    import platform
    my_os = platform.system()
    if my_os.lower().strip() == 'windows':
        import winsound
        winsound.MessageBeep()

    sg.theme(theme)
    return sg.popup_get_folder(message=text, title=title, default_path=default_path, no_window=no_window, background_color=back_color)

def popup_true_false(title: str='Deseja continuar?', text: str='Deseja continuar?', no_titlebar=False, theme: str='Material1', back_color: str='#E0E3E4'):
    import platform
    my_os = platform.system()
    if my_os.lower().strip() == 'windows':
        import winsound
        winsound.MessageBeep()

    sg.theme(theme)
    return sg.popup_ok_cancel(text, title=title,background_color=back_color, no_titlebar=no_titlebar, )
    
