import os
import pikepdf
from pikepdf import Pdf

def compress_pdf(input_path, output_path, compression_level='medium'):
    """
    Comprime um arquivo PDF.
    
    Args:
        input_path (str): Caminho do arquivo PDF de entrada.
        output_path (str): Caminho onde o PDF comprimido será salvo.
        compression_level (str): Nível de compressão ('low', 'medium', 'high').
            - 'low': Compressão leve, mantém alta qualidade
            - 'medium': Compressão média, bom equilíbrio entre qualidade e tamanho
            - 'high': Compressão alta, prioriza redução de tamanho
    
    Returns:
        tuple: (bool, str) - (Sucesso da operação, Mensagem)
    
    Exemplos:
    ```
        # Exemplo básico com compressão média (padrão)
        success, message = compress_pdf(
            input_path="documento.pdf",
            output_path="documento_comprimido.pdf"
        )
        print(message)
        
        # Exemplo com compressão alta
        success, message = compress_pdf(
            input_path="documento.pdf",
            output_path="documento_comprimido.pdf",
            compression_level="high"
        )
        
        # Tratamento de erros
        success, message = compress_pdf("arquivo.pdf", "comprimido.pdf")
        if not success:
            print(f"Erro: {message}")
        else:
            print(f"Sucesso: {message}")
    ```
    """
    try:
        # Verificar se o arquivo de entrada existe
        if not os.path.exists(input_path):
            return False, f"Erro: O arquivo {input_path} não existe."
        
        # Verificar se o arquivo de entrada é um PDF
        if not input_path.lower().endswith('.pdf'):
            return False, f"Erro: O arquivo {input_path} não é um PDF."
        
        # Criar diretório de saída se não existir
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Definir configurações de compressão com base no nível escolhido
        if compression_level == 'low':
            compression_params = {
                'object_stream_mode': pikepdf.ObjectStreamMode.disable,
                'compress_streams': True,
                'stream_decode_level': pikepdf.StreamDecodeLevel.none,
                'linearize': False
            }
        elif compression_level == 'high':
            compression_params = {
                'object_stream_mode': pikepdf.ObjectStreamMode.generate,
                'compress_streams': True,
                'stream_decode_level': pikepdf.StreamDecodeLevel.generalized,
                'linearize': True
            }
        else:  # medium (default)
            compression_params = {
                'object_stream_mode': pikepdf.ObjectStreamMode.preserve,
                'compress_streams': True,
                'stream_decode_level': pikepdf.StreamDecodeLevel.specialized,
                'linearize': False
            }
        
        # Abrir o PDF de entrada
        pdf = Pdf.open(input_path)
        
        # Salvar o PDF comprimido
        pdf.save(output_path, **compression_params)
        
        # Fechar o PDF
        pdf.close()
        
        # Verificar tamanhos para informar a taxa de compressão
        input_size = os.path.getsize(input_path)
        output_size = os.path.getsize(output_path)
        compression_ratio = (1 - (output_size / input_size)) * 100
        
        return True, f"PDF comprimido com sucesso! Redução de tamanho: {compression_ratio:.2f}% ({input_size/1024:.2f}KB → {output_size/1024:.2f}KB)"
    
    except Exception as e:
        return False, f"Erro ao comprimir o PDF: {str(e)}"
