from urllib.error import URLError

# --- Exceptions Selenium Base ---- #


# --- Exceptions Python Base ---- #
class EmailOuLoginIncorretoElawException(Exception):
    pass

class EmailOuLoginIncorretoGmailException(Exception):
    pass
# --- Exceptions Python Base ---- #


# --- Exceptions urllib Base ---- #
class ErroNaURLUrllib(URLError):
    pass


# --- Exceptions APIS PDF ---- #
class FalhaAoRecuperarOcr(Exception):
    pass
class NivelDeCompressaoNaoPreenchido(Exception):
    pass
class ErroNoConversorException(Exception):
    pass
class ErroNoConversorImagesException(Exception):
    pass