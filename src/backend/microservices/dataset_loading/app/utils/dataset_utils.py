import uuid
from database import connect_to_database
import logging

# Inicializa el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Función para generar un ID único para cada dataset
def generate_data_id() -> str:
    return str(uuid.uuid4())


# Función para insertar un nuevo dataset en la base de datos
def insert_file_mapping(data_id, file_path):
    db = connect_to_database()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO data_files (data_id, file_path) VALUES (%s, %s)",
        (data_id, file_path)
    )
    db.commit()
    cursor.close()
    db.close()

# Función para obtener la ruta de un dataset a partir de su ID
def get_file_path(data_id):
    logger.info(f"Obteniendo ruta del archivo para el data_id: {data_id}")
    db = connect_to_database()
    cursor = db.cursor()
    try:
        logger.info("Ejecutando query para obtener la ruta del archivo")
        cursor.execute("SELECT file_path FROM data_files WHERE data_id = %s", (data_id,))
        logger.info("Obteniendo resultado de la query")
        result = cursor.fetchone()
        if result:
            logger.info(f"Ruta del archivo encontrada: {result[0]}")
            return result[0]
        else:
            logger.error(f"Archivo no encontrado en el data id: {data_id}")
            raise FileNotFoundError(f"Fichero no encontrado en el data id: {data_id}")
    finally:
        cursor.close()
        db.close()

# Funcion para obtener listado de archivos de la base de datos
def get_files_list(user_id):
    logger.info(f"Obteniendo lista de archivos para el usuario: {user_id}")
    logger.info("Conectando a la base de datos")

    db = connect_to_database()
    logger.info("Conexión establecida")
    cursor = db.cursor()
    logger.info("Creando cursor para ejecutar query")
    cursor.execute("""
        SELECT data_files.data_id, data_files.file_path 
        FROM user_datasets 
        JOIN data_files ON user_datasets.data_id = data_files.data_id 
        WHERE user_datasets.user_id = %s
    """, (user_id,))
    
    logger.info("Query ejecutada")
    datasets = cursor.fetchall()
    cursor.close()
    db.close()
    return datasets

# Funcion para verificar si un archivo ya existe

def check_file_exists(user_id: str, file_name: str) -> bool:
    # Conectamos a la base de datos
    db = connect_to_database()
    # Creamos un cursor
    cursor = db.cursor()

    # Falta comprobar la query
    query = """
    SELECT data_files.data_id
    FROM data_files
    JOIN user_datasets ON data_files.data_id = user_datasets.data_id
    WHERE user_datasets.user_id = %s AND data_files.file_path LIKE %s
    """

    # Tomamos como nombre del archivo el final de la ruta
    file_path_like = "%" + file_name

    # Ejecutamos la query
    cursor.execute(query, (user_id, file_path_like))
    # Comprobamos si hay algún resultado
    result = cursor.fetchone()
    # Cerramos el cursor
    cursor.close()
    # Cerramos la conexión
    db.close()

    return result is not None

# Funcion para actualizar la ruta de un archivo en la base de datos (FALTA GESTION DE ERRORES)

def update_file_mapping(user_id: str, file_name: str, new_file_path: str):
    # Conectamos a la base de datos
    db = connect_to_database()
    # Creamos un cursor
    cursor = db.cursor()

    # Encuentra el data_id basado en el user_id y el nombre del archivo
    # Falta probar la query
    query_find_data_id = """
    SELECT data_files.data_id
    FROM data_files
    JOIN user_datasets ON data_files.data_id = user_datasets.data_id
    WHERE user_datasets.user_id = %s AND data_files.file_path LIKE %s
    """
    # Tomamos como nombre del archivo el final de la ruta
    file_path_like = "%" + file_name  
    # Ejecutamos la query
    cursor.execute(query_find_data_id, (user_id, file_path_like))
    # Obtenemos el resultado
    result = cursor.fetchone()

    # Si hay resultado, actualizamos el file_path para el data_id encontrado
    if result:
        # Tomamos el data_id
        data_id = result[0]
        # Actualiza el file_path para el data_id encontrado
        query_update = """
        UPDATE data_files
        SET file_path = %s
        WHERE data_id = %s
        """
        # Ejecutamos la query
        cursor.execute(query_update, (new_file_path, data_id))
        # Hacemos commit a la db
        db.commit()
    # cerramos el cursor
    cursor.close()

    # cerramos la conexión
    db.close()