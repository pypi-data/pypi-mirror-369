import hashlib
from payconpy.fpython.fpython import *
from xmlrpc import client
import xmlrpc.client as client
import filetype

def insert_odoo(model:str, data:dict|list, auth:dict, uid:int = None) -> int:
    """
    ## Inserts data into an Odoo model and returns the ID of the created record.


    Args:
        model (str): The name of the Odoo model to insert data into.
        data (dict | list): The data to insert into the Odoo model.
        auth (dict): Dict with auth for Odoo.
        uid (int, optional): UID from a retrieved auth. Defaults to None.
        

    Returns:
        int: Returns the ID of the created record

    Example for use:
    ```
    model = 'res.partner'
    data = {
        'name': 'John Doe',
        'phone': '555-555-5555'
        }
    auth = {
        'URL_RPC': 'https://your.odoo.com',
        'DB_RPC': 'your_db',
        'USERNAME_RPC': 'your_username',
        'PASSWORD_RPC': 'your_password'
        }
    insert_odoo(model, data, auth)
    12
    ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(URL_RPC))
    record_id = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'create', [data])

    return record_id

def insert_odoo_if_not_exists(model:str, data:dict, domain:tuple, auth:dict, uid:int = None) -> int:
    """
    This function inserts a record into an Odoo model if a record with the specified domain does not already exist. 
    If a record exists, it returns the ID of the existing record.

    Args:
        model (str): The name of the Odoo model where the record will be inserted.
        data (dict): A dictionary containing the data for the new record to be inserted.
        domain (tuple): A tuple specifying the domain to check for existing records.
        auth (dict): A dictionary containing authentication information including URL, database name, username, and password
        uid (int): UID from a retrieved auth

    Returns:
        int: The ID of the newly inserted record if it didn't already exist. If a record with the specified domain exists,
            it returns the ID of the existing record.

    Example:
    ```
    model = "res.partner"
    data = {"name": "John Doe", "email": "johndoe@example.com"}
    domain = [("name", "=", "John Doe")]
    auth = {
        "URL_RPC": "http://example.com/",
        "DB_RPC": "mydb",
        "USERNAME_RPC": "admin",
        "PASSWORD_RPC": "admin_password"
    }
    print(insert_odoo_if_not_exists(model, data, domain, auth))
    7
    ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy(f'{URL_RPC}xmlrpc/2/object')

    if len(domain) >= 1:
        partner_ids = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'search', [domain])
    else:
        partner_ids = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'search', [])

    # Verify if the register already exists
    if not partner_ids:
        new_data_id = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'create', [data])
        faz_log(f'New register created with id: {new_data_id} on model: {model}')
        return new_data_id
    else:
        faz_log(f'Resister already exists on model: {model} with id(s): {partner_ids}')
        return partner_ids[-1]

def update_record_odoo(model: str, data: dict, record_id: int, auth: dict, uid: int = None) -> int:
    """
    This function updates a record in an Odoo model if a record with the specified ID exists.

    Parameters:
    model (str): The name of the Odoo model where the record will be updated.
    data (dict): A dictionary containing the data to update the existing record.
    record_id (int): The ID of the existing record to be updated.
    auth (dict): A dictionary containing authentication information including URL, database name, username, and password
                for connecting to the Odoo instance.
    uid (int): UID from a retrieved auth

    Returns:
    int: The ID of the updated record.

    Example:
    ```
    model = "res.partner"
    data = {"name": "John Doe (Updated)"}
    record_id = 7  # ID of the existing record to update
    auth = {
        "URL_RPC": "http://example.com/",
        "DB_RPC": "mydb",
        "USERNAME_RPC": "admin",
        "PASSWORD_RPC": "admin_password"
    }
    print(update_odoo_record_if_exists(model, data, record_id, auth))
    7
    ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy(f'{URL_RPC}xmlrpc/2/object')

    # Verify if the record with the specified ID exists
    if models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'search', [[('id', '=', record_id)]]):
        models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'write', [[record_id], data])
        faz_log(f'Record updated with ID: {record_id} on model: {model}')
        return record_id
    else:
        faz_log(f'Record with ID {record_id} does not exist on model: {model}')
        return None

def get_odoo(model: str, data: dict, auth: dict, filters: list = [], uid: int = None, start_index: int = 0, end_index: int = None, limit: int = None) -> list[dict]:
    """
    Retrieves data from an Odoo model using XML-RPC, applying filters, and supports retrieving records by a specified range.

    Parameters:
    model (str): The name of the Odoo model to retrieve data from.
    data (dict): A dictionary containing additional arguments to pass to the XML-RPC call, such as fields to retrieve.
    auth (dict): A dictionary containing authentication information including URL, database name, username, and password
                for connecting to the Odoo instance.
    filters (list): A list of tuples representing the filters to apply. Each tuple should contain the field name,
                    the operator, and the value to filter by. Default is an empty list.
    uid (int): The authenticated user ID. If not provided, the function will authenticate using the credentials in `auth`.
    start_index (int): The starting index for retrieving records. Default is 0.
    end_index (int): The ending index for retrieving records. If not provided, all records after `start_index` will be retrieved.
    limit (int): Maximum number of records to return. If not provided, the limit is calculated based on `start_index` and `end_index`.

    Returns:
    list[dict]: A list of dictionaries containing the retrieved records.

    Example:
    ```
    model = "res.partner"
    data = {"fields": ["name", "email"]}
    auth = {
        "URL_RPC": "http://example.com/",
        "DB_RPC": "mydb",
        "USERNAME_RPC": "admin",
        "PASSWORD_RPC": "admin_password"
    }
    filters = [("name", "ilike", "John")]
    start_index = 0
    end_index = 10
    print(get_odoo(model, data, auth, filters, start_index=start_index, end_index=end_index))
    [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "John Smith", "email": "john.smith@example.com"}
    ]
    ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy(f'{URL_RPC}xmlrpc/2/object')

    # Apply filters to the search call
    domain = []
    for filter in filters:
        domain.append(filter)
    
    # Calculate the limit as the difference between end_index and start_index
    if end_index is not None:
        calculated_limit = (end_index - start_index + 1)
        limit = min(limit, calculated_limit) if limit is not None else calculated_limit

    # Set the limit and offset for pagination
    if limit is not None:
        data['limit'] = limit
    data['offset'] = start_index

    values = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'search_read', [domain], data)
    return values


def insert_odoo_lots(model, data, auth, uid=None):
    """
    ### Alert! No verify if records exists
    Inserts a batch of records into a specified Odoo model using XML-RPC and returns the IDs of the newly created records. This function is 
    particularly useful for inserting multiple records in a single call, enhancing performance when dealing with large datasets.

    Args:
        model (str): The name of the Odoo model where the records will be inserted. 
                    For example, 'res.partner' for the Partner model.
        data (list): A list of dictionaries, where each dictionary represents the data for a record to be inserted into the model. 
                    Each key in the dictionary should correspond to a field name in the Odoo model.
        auth (dict): A dictionary containing authentication information for the Odoo instance. 
                    It should include the following keys: 'URL_RPC' (the base URL for the Odoo instance), 
                    'DB_RPC' (the database name), 'USERNAME_RPC' (the username), and 'PASSWORD_RPC' (the password).

    Returns:
        list: A list of integers representing the IDs of the newly created records in the Odoo model. If the insertion is successful, 
            this list will contain the IDs of all inserted records. If an error occurs during insertion, an XML-RPC fault may be raised.

    Example:
        ```
        model = 'res.partner'
        data = [
            {'name': 'John Doe', 'email': 'john@example.com'},
            {'name': 'Jane Doe', 'email': 'jane@example.com'}
        ]
        auth = {
            'URL_RPC': 'http://example.odoo.com',
            'DB_RPC': 'odoo_db',
            'USERNAME_RPC': 'admin',
            'PASSWORD_RPC': 'admin_password or api_key'
        }
        record_ids = insert_odoo_lots(model, data, auth)
        print(record_ids) # [1, 2]
        ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(URL_RPC))

    if not isinstance(data, list):
        data = [data]

    record_ids = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, 'create', [data])
    return record_ids

def authenticate_odoo(auth: dict) -> int:
    """
    Authenticates a user in an Odoo instance and returns the UID (User ID) of the authenticated user.

    Parameters:
    auth (dict): A dictionary containing authentication information for connecting to the Odoo instance.
                    Required keys:
                    - 'URL_RPC': The URL of the Odoo instance's XML-RPC endpoint.
                    - 'DB_RPC': The name of the Odoo database.
                    - 'USERNAME_RPC': The username for authentication.
                    - 'PASSWORD_RPC': The password for authentication.

    Returns:
    int: The UID (User ID) of the authenticated user.

    Example:
    ```
    auth = {
        "URL_RPC": "http://example.com/",
        "DB_RPC": "mydb",
        "USERNAME_RPC": "admin",
        "PASSWORD_RPC": "admin_password"
    }
    uid = authenticate_odoo(auth)
    print(uid)
    1  # UID of the authenticated user
    ```
    """    
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']
    
    common = client.ServerProxy(f'{URL_RPC}xmlrpc/2/common')
    uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    return uid

def send_file_to_odoo_cloud_storage(file_path: str, auth: dict, uid: int = None, res_model: str = 'legal.document', res_field: str = "attachment", type_id_legal_document: int|bool = 2) -> int|str:
    """
    Envia um arquivo para o cloud storage do Odoo e retorna o ID do anexo e o ID do registro associado.

    Args:
        file_path (str): Caminho absoluto ou relativo do arquivo a ser enviado.
        auth (dict): Credenciais de acesso ao Odoo, incluindo URL, DB, username e password.
        uid (int, optional): UID do usuário autenticado. Se não fornecido, a função autenticará automaticamente. Defaults to None.
        res_model (str, optional): Modelo relacionado onde o arquivo será anexado. Defaults to 'legal.document'.
        res_field (str, optional): Campo onde o arquivo será enviado (tipo binário). Defaults to 'attachment'.
        type_id_legal_document (int|bool, optional): ID do tipo de documento legal. Defaults to 2.

    Returns:
        int: ID do registro no `ir.attachment` no Odoo.
        int: ID do registro no modelo especificado.

    Example:
        # Exemplo de uso
        url = "https://example.odoo.com/"
        db = "example_db"
        username = "example_user"
        password = "example_password"

        AUTH = {
            "URL_RPC": url,
            "DB_RPC": db,
            "USERNAME_RPC": username,
            "PASSWORD_RPC": password
        }

        record_id = 1
        file_path = "_inicial_tribunal.pdf"
        uid = authenticate_odoo(AUTH)
        attachment_id, res_id = send_file_to_odoo_cloud_storage(file_path, AUTH, uid, res_model='legal.document', res_field='attachment')
        print(f"Attachment created successfully with ID: {attachment_id} and res_id: {res_id}")

        # Adicionando o anexo ao campo `documents_ids` de um registro no modelo `legal.process`
        documents_ids = [res_id]

        data_update = {
            'documents_ids': documents_ids
        }
        update_record_odoo('legal.process', data_update, record_id=record_id, auth=AUTH, uid=uid)
    """
    def get_file_info_base64(base64_string):
        # pip install filetype
        missing_padding = len(base64_string) % 4
        if missing_padding != 0:
            base64_string += '=' * (4 - missing_padding)
        
        # Decodificar a string base64
        file_data = base64.b64decode(base64_string)
        
        # Usar filetype para identificar o tipo de arquivo
        kind = filetype.guess(file_data)
        
        if kind is None:
            return 'unknown', 'application/octet-stream'
        
        # Retorna a extensão do arquivo e o tipo MIME
        return kind.extension, kind.mime
    
    # O arquivo precisa ser convertido em base64 antes de ser enviado
    attatchment_bs64 = file_to_base64(file_path)
    _extension, content_type = get_file_info_base64(attatchment_bs64)

    session = requests.Session()

    login_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": auth['DB_RPC'],
            "login": auth['USERNAME_RPC'],
            "password": auth['PASSWORD_RPC'],
            "context": {}
        }
    }

    login_response = session.post(f"{auth['URL_RPC']}web/session/authenticate", json=login_payload)

    if login_response.status_code == 200:
        login_data = login_response.json()
        if login_data.get("result") and login_data["result"].get("uid"):
            print("Web session authenticated successfully.")
        else:
            print("Failed to authenticate the web session.")
            return None
    else:
        print(f"Failed to authenticate the web session. Status code: {login_response.status_code}")
        return None

    with open(file_path, 'rb') as file_data:
        file_content = file_data.read()
        md5_hash = hashlib.md5(file_content).hexdigest()

    file_name = os.path.basename(file_path)
    res_id = insert_odoo('legal.document', {
        'attachment_filename': file_name,
        'type_id': type_id_legal_document}, auth=auth, uid=uid)

    upload_payload = {
        'params': {
            'fileName': md5_hash,
            'contentType': content_type,
            'res_model': res_model,
            'res_field': res_field,
            'res_id': res_id,
        }
    }

    upload_response = session.post(
        f"{auth['URL_RPC']}cloud_storage/upload_and_create_attachment",
        json=upload_payload
    )

    if upload_response.status_code == 200:
        try:
            upload_data = upload_response.json()
            # print("Upload Response:", upload_data)  # Debugging line to print the response
            
            signed_url = upload_data.get('result', {}).get('signed_url')
            ir_attachment_id = upload_data.get('result', {}).get('attachment_id')
            
            if not signed_url:
                print("No signed URL received, assuming the file already exists.")
            else:
                print(f"Signed URL for upload: {signed_url}")
            
            # print(f"Attachment ID: {ir_attachment_id}")
            
            # Step 2: Upload the file to the signed URL if it's provided
            if signed_url:
                with open(file_path, 'rb') as file_data:
                    response = requests.put(signed_url, data=file_data, headers={"Content-Type": content_type})

                if response.status_code == 200:
                    print("File uploaded successfully.")
                else:
                    print("Failed to upload the file.")
                    return None
            else:
                print("No need to upload, file already exists in GCS.")
            
            return ir_attachment_id, res_id

        except json.JSONDecodeError:
            print("Failed to parse JSON response:")
            # print(upload_response.text)
            return None
    else:
        print(f"Failed to get signed URL and create attachment. Status code: {upload_response.status_code}")
        # print("Response content:", upload_response.text)
        return None

def execute_odoo_action(model: str, method: str, auth: dict, uid: int = None, record_id: int=None, args: list=[]) -> list:
    """
    Executes an action on an Odoo model using XML-RPC.

    Args:
        model (str): The name of the Odoo model to execute the action on.
        method (str): The method name to be called on the model.
        record_id (int): The record ID on which to execute the action.
        auth (dict): A dictionary containing authentication information with keys 'URL_RPC', 'DB_RPC', 'USERNAME_RPC', and 'PASSWORD_RPC'.
        uid (int, optional): The user ID to authenticate with. If None, the function will authenticate and retrieve the user ID.

    Returns:
        list: The result of the action or None if the action returns None.

    Example:
        Here's an example of how you could use the execute_odoo_action() function:

        ```
        def main():
            # Execute the 'action_done' method on the 'x_work_litigio_flow' model for a specific record ID
            model = 'x_work_litigio_flow'
            method = 'action_done'
            record_id = 1  # Replace with the actual record ID
            auth = {
                'URL_RPC': 'http://your_odoo_server',
                'DB_RPC': 'your_database_name',
                'USERNAME_RPC': 'your_username',
                'PASSWORD_RPC': 'your_password'
            }
            result = execute_odoo_action(model, method, record_id, auth)
            print(result)

        if __name__ == "__main__":
            main()
        ```
    """
    URL_RPC = auth['URL_RPC']
    DB_RPC = auth['DB_RPC']
    USERNAME_RPC = auth['USERNAME_RPC']
    PASSWORD_RPC = auth['PASSWORD_RPC']

    common = client.ServerProxy(f'{URL_RPC}/xmlrpc/2/common')
    if uid is None:
        uid = common.authenticate(DB_RPC, USERNAME_RPC, PASSWORD_RPC, {})
    models = client.ServerProxy(f'{URL_RPC}/xmlrpc/2/object')

    try:
        if record_id is None:
            result = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, method, args)
        else:
            result = models.execute_kw(DB_RPC, uid, PASSWORD_RPC, model, method, [[record_id]])
    except client.Fault as fault:
        if "cannot marshal None unless allow_none is enabled" in str(fault):
            faz_log(f"Action completed successfully but returned None: {fault}")
            return None
        else:
            faz_log(f"XML-RPC Fault: {fault}")
            faz_log(f"Method: {method}, Model: {model}, Record ID: {record_id}")
            raise

    return result
