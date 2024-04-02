from fastapi import FastAPI
from routers import cleaning_router

# Inicializa la aplicación FastAPI
app = FastAPI()

# Routers
app.include_router(cleaning_router, prefix="/cleaning_operations")
