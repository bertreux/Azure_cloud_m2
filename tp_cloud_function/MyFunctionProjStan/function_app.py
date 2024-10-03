import azure.functions as func
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import uuid
from azure.cosmos import CosmosClient, exceptions

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    return func.HttpResponse("Hello, World!", status_code=200)

@app.route(route="log_request")
def log_request(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Logging request data.')

    # Configuration des informations d'authentification Azure Storage
    connect_str = "<connect_str>"
    container_name = "logs"

    # Création du client de service Blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Création ou obtention du conteneur
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception as e:
        # Ignorer l'erreur si le conteneur existe déjà
        logging.info(f"Container already exists: {e}")

    # Extraction des données de la requête
    # Récupération de l'adresse IP à partir des en-têtes
    ip_address = req.headers.get('X-Forwarded-For', req.headers.get('Remote-Addr', 'Unknown'))
    log_data = f"{ip_address} - {req.method} - {req.url}\n"

    # Écriture des données dans un blob
    blob_client = container_client.get_blob_client("logs.txt")

    # Vérification si le blob existe déjà
    try:
        # Si le blob existe, on lit son contenu et on l'ajoute
        existing_blob_data = blob_client.download_blob().readall().decode('utf-8')
        log_data = existing_blob_data + log_data
    except Exception as e:
        # Si le blob n'existe pas, on crée un nouveau blob
        logging.info(f"Blob not found: {e}")

    blob_client.upload_blob(log_data, overwrite=True)

    return func.HttpResponse('Logged request!', status_code=200)

@app.route(route="store_log")
def store_log(req: func.HttpRequest) -> func.HttpResponse:
    # Obtenir les données JSON de la requête
    try:
        log_data = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    connect_str = "<connect_str>"

    # Déterminer le conteneur en fonction du niveau de log
    if log_data.get('level') == 'ERROR':
        container_name = "errors"
    else:
        container_name = "logs"

    # Création du client de service Blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Création ou obtention du conteneur
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception as e:
        # Ignorer l'erreur si le conteneur existe déjà
        logging.info(f"Container already exists: {e}")

    # Écriture des données dans un blob
    blob_client = container_client.get_blob_client("logs2.txt")

    # Vérification si le blob existe déjà
    try:
        # Si le blob existe, on lit son contenu et on l'ajoute
        existing_blob_data = blob_client.download_blob().readall().decode('utf-8')
        existing_blob_data += json.dumps(log_data) + "\n"
    except Exception as e:
        # Si le blob n'existe pas, on crée un nouveau blob
        logging.info(f"Blob not found: {e}")
        existing_blob_data = json.dumps(log_data) + "\n"

    # Télécharger les données dans le blob
    blob_client.upload_blob(existing_blob_data, overwrite=True, content_type='application/json')

    return func.HttpResponse('Logged request!', status_code=200)

# Connexion à Cosmos DB
client = CosmosClient("https://cosmosdbstan.documents.azure.com:443/", "<cosmos_key>")
database = client.get_database_client("api")
container = database.get_container_client("crud")

@app.route(route="crud_api")
def crud_api(req: func.HttpRequest) -> func.HttpResponse:
    try:        
        # Si la méthode est POST, PUT, DELETE, récupère le JSON du corps
        request_json = None
        if req.method != 'GET':
            try:
                request_json = req.get_json()
                logging.info(f"Corps JSON de la requête : {request_json}")
            except ValueError:
                logging.error("Erreur : La requête ne contient pas de JSON valide")
                return func.HttpResponse("Invalid JSON", status_code=400)

        if req.method == 'GET':
            # Exécuter la requête pour obtenir tous les utilisateurs
            users = container.query_items(
                query="SELECT * FROM crud",
                enable_cross_partition_query=True
            )
            return func.HttpResponse(json.dumps([user for user in users]), mimetype="application/json", status_code=200)

        elif req.method == 'POST':
            userid = str(uuid.uuid4())
            user_data = request_json.get('data')
            container.create_item(body={"id": userid, "userid": userid, **user_data})
            return func.HttpResponse('User added!', status_code=200)

        elif req.method == 'PUT':
            userid = request_json.get('id')
            user_data = request_json.get('data')
            container.upsert_item(body={"id": userid, "userid": userid, **user_data})
            return func.HttpResponse('User updated!', status_code=200)

        elif req.method == 'DELETE':
            userid = request_json.get('id')
            container.delete_item(item=userid, partition_key=userid)
            return func.HttpResponse('User deleted!', status_code=200)

        else:
            return func.HttpResponse('Method not supported!', status_code=400)

    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos DB Error: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)
