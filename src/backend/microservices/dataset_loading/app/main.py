from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
import logging
from typing import List
from pydantic import BaseModel
import utils.dataset_utils as du

# Inicializa el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lanza la api 
app = FastAPI()

# clase para el modelo de datos
class Dataset(BaseModel):
    data_id: str
    file_name: str

#Endpoint para subir un archivo y almacenarlo en el servidor (Falta implementar el LOGGING)

@app.post("/upload-dataset/{user_id}")

# Se espera recibir un user_id, un archivo y un booleano para sobreescribir o no (Por defecto no sobreescribe)
# Pendiente de añadir que se envie tambien un nombre para el archivo, en vez de usar el que tiene el archivo por defecto
async def upload_dataset(user_id: str, file: UploadFile = File(...), overwrite: bool = False):

    # Ruta donde se almacenarán los archivos
    storage_path = f"/files/{user_id}"

    # Crear la carpeta si no existe
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    # Ruta al archivo final
    file_location = f"{storage_path}/{file.filename}"

    # Verificar si el archivo ya existe
    existing_file =du.check_file_exists(user_id, file.filename)

    # Si el archivo ya existe y no se ha confirmado la sobrescritura, devuelve un mensaje para confirmar
    if existing_file and not overwrite:
        return {"message": "El archivo ya existe. ¿Desea sobreescribir?", "overwrite_required": True}

    # Si el archivo es un CSV, Excel o JSON, lo guardamos en el servidor
    if file.content_type in ["text/csv", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/json"]:
        try:
            # Guardar el archivo en el servidor
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)

            # Si estamos sobreescribiendo, actualizamos la entrada existente en lugar de crear una nueva
            if existing_file:
                du.update_file_mapping(user_id, file.filename, file_location) 

            # Si no estamos sobreescribiendo, creamos una nueva entrada
            else:
                data_id = du.generate_data_id()
                du.insert_file_mapping(data_id, file_location)

            message = "Archivo subido correctamente"

            # Devolver el ID del archivo y un mensaje de confirmación
            return {"data_id": data_id, "message": message}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {e}")
    else:
        raise HTTPException(status_code=400, detail="Formato de archivo no soportado.")

    

@app.get("/list_datasets/{user_id}", response_model=List[Dataset])
async def list_datasets_for_user(user_id: str):

    # Obtener la lista de datasets del usuario
    datasets = du.get_files_list(user_id)

    # Si no hay datasets, devolver un error 404
    if not datasets:
        raise HTTPException(status_code='nabo', detail="No se han encontrado datasets almacenados")
    
    # Si hay datasets, devolver una lista con los IDs y nombres de los archivos
    return [{"data_id": data_id, "file_name": file_path.split("/")[-1]} for data_id, file_path in datasets]







    


