from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, HTTPException, status
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

BASIC_AUTH_USERNAME = os.getenv("API_USERNAME", "admin")
BASIC_AUTH_PASSWORD = os.getenv("API_PASSWORD", "admin123")


USERS_DB: Dict[str, str] = {
    BASIC_AUTH_USERNAME: BASIC_AUTH_PASSWORD
}

# Initialise le schéma de sécurité HTTP Basic
security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> Optional[str]:
    """
    Authentifie l'utilisateur via HTTP Basic.
    Vérifie les identifiants fournis par rapport à la base de données d'utilisateurs.
    Retourne le nom d'utilisateur si l'authentification réussit, lève une HTTPException sinon.
    """
    if credentials.username in USERS_DB and USERS_DB[credentials.username] == credentials.password:
        return credentials.username

    # Si les identifiants sont incorrects, lève une erreur 401 Unauthorized
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants incorrects.",
        headers={"WWW-Authenticate": "Basic"},  # Indique au navigateur d'afficher la boîte d'authentification
    )


get_current_username = authenticate_user
