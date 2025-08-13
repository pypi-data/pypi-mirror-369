import os, re
from time import sleep
from openai import OpenAI

def create_assistant(api_key: str, name: str, instructions: str, model: str = "gpt-4-1106-preview", files_openai: list[str] | None = None, tools:dict={"type": "retrieval"}) -> dict:
    client = OpenAI(api_key=api_key)  # retrive client

    assistant = client.beta.assistants.create(
    name=name,
    instructions=instructions,
    model=model,
    tools=[tools],
    file_ids=files_openai)
    
    return assistant


def chatbot(api_key: str, file_path: str, assistant_id: str, prompts: dict, sleep_for_status: int = 3):
    """Realiza interações com um assistente OpenAI e envia documentos e perguntas usando a API da OpenAI.

    Este script cria uma instância de cliente OpenAI, recupera um assistente, envia um arquivo para criar embeddings e 
    processa um conjunto de perguntas (prompts). Ele verifica o status de cada interação e coleta as respostas.

    Args:
        api_key (str): A chave de API para acessar a API da OpenAI.
        file_path (str): O caminho do arquivo a ser enviado para a OpenAI para criação de embeddings.
        assistant_id (str): O ID do assistente a ser recuperado.
        prompts (dict): Um dicionário de prompts, onde as chaves são as identificações dos prompts e os valores são os prompts reais.
        sleep_for_status (int, optional): O número de segundos para esperar entre as verificações do status das interações. Padrão é 3.

    Returns:
        dict: Um dicionário contendo as respostas do chatbot, onde as chaves correspondem às identificações dos prompts e os valores às respostas.

    Raises:
        Exception: Erros podem ocorrer devido a falhas na comunicação com a API da OpenAI, problemas no processamento dos arquivos ou na recuperação das respostas.
    """

    client = OpenAI(api_key=api_key)  # retrive client
    
    assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)  # retrieve an assistant
    
    file = client.files.create(file=open(file_path, "rb"), purpose='assistants')  # send file for openai for create embeddings

    responses = {}
    threads_ids = []
    run_ids = []

    for prompt_key, prompt_value in prompts.items():  # create threads
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_value,
                    "file_ids": [file.id]
                }
            ])
        threads_ids.append((thread.id, prompt_key, prompt_value))

    for thread_id, _, _ in threads_ids:  # create runs for each thread
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.id)
        run_ids.append((run.id, thread_id))

    for run_id, thread_id in run_ids:  # verify runs and collect responses
        not_completed = True
        while not_completed:
            run = client.beta.threads.runs.retrieve(run_id, thread_id=thread_id)
            if run.status == 'completed':
                prompt_key_ = ''
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                for message in reversed(messages.data):
                    if message.role == 'user':
                        prompt_value_ = re.sub(r'【.+', '', message.content[0].text.value)
                        for _, prompt_key, prompt_value in threads_ids:
                            if prompt_value == prompt_value_:
                                prompt_key_ = prompt_key
                        continue
                    response = re.sub(r'【.+', '', message.content[0].text.value)
                    responses[prompt_key_] = response
                    not_completed = False
            elif run.status == 'failed':
                print(run.last_error.code + ' ' + run.last_error.message)
                not_completed = False
            else:
                sleep(sleep_for_status)

    client.files.delete(file.id)

    return responses
