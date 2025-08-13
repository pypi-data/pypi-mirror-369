import fitz

def extrair_quantidade_paginas_pdf(pdf_path: str) -> int:
    """
    Retorna a quantidade total de páginas de um arquivo PDF.

    Args:
        pdf_path (str): Caminho completo para o arquivo PDF.

    Returns:
        int: Número total de páginas no PDF.

    Raises:
        FileNotFoundError: Se o arquivo não for encontrado no caminho especificado.
        ValueError: Se o arquivo não for um PDF válido ou estiver corrompido.

    Use:
        >>> total_paginas = extrair_quantidade_paginas_pdf("documento.pdf")
        >>> print(total_paginas)
        12
    """
    try:
        with fitz.open(pdf_path) as pdf:
            return pdf.page_count
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    except Exception as e:
        raise ValueError(f"Erro ao processar o PDF: {e}")
