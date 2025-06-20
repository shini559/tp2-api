from fastapi import FastAPI
from api.routes import router

# Crée l'application FastAPI
app = FastAPI(
    title="API Utilisateurs GitHub Filtrés", # Titre de l'API pour la documentation
    description="API pour accéder aux données filtrées des utilisateurs GitHub, avec authentification HTTP Basic.",
    version="1.0.0", # Version de l'API
    docs_url="/docs", # URL de la documentation Swagger UI
    redoc_url="/redoc" # URL de la documentation ReDoc
)

# Inclut le routeur dans l'application principale
app.include_router(router)

