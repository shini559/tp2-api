from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import json
import os

from api.models import User
from api.security import get_current_username


router = APIRouter()

# Chemin vers le fichier de données filtrées
FILTERED_USERS_FILE = "data/filtered_users.json"

# Variable globale pour stocker les utilisateurs chargés.
_users_data: List[User] = []


def load_filtered_users_on_startup():
    """
    Charge les utilisateurs filtrés depuis le fichier JSON au démarrage de l'API.
    Cette fonction est appelée une seule fois.
    """
    global _users_data  # Indique que nous modifions la variable globale
    if not os.path.exists(FILTERED_USERS_FILE):
        print(
            f"Erreur: Le fichier '{FILTERED_USERS_FILE}' est introuvable. Exécutez 'extract_users.py' puis 'filtered_users.py' d'abord.")
        raise RuntimeError(f"Fichier de données manquant: {FILTERED_USERS_FILE}")
    try:
        with open(FILTERED_USERS_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Convertit les dictionnaires bruts en modèles Pydantic User
        _users_data = [User(**user_dict) for user_dict in raw_data]
        print(f"'{len(_users_data)}' utilisateurs filtrés chargés avec succès.")
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON lors de la lecture de '{FILTERED_USERS_FILE}': {e}")
        raise RuntimeError(f"Erreur de format du fichier de données: {FILTERED_USERS_FILE}")
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors du chargement des données: {e}")
        raise RuntimeError(f"Erreur de chargement des données: {e}")


@router.on_event("startup")
async def startup_event():
    """
    Événement de démarrage de FastAPI pour charger les données.
    """
    load_filtered_users_on_startup()


@router.get(
    "/users/",
    response_model=List[User],
    summary="Obtenir tous les utilisateurs filtrés",
    description="Retourne la liste complète des utilisateurs GitHub filtrés et nettoyés, nécessitant une authentification.",
    dependencies=[Depends(get_current_username)]  # Protège la route avec l'authentification
)
async def get_all_users():
    """
    Retourne la liste complète des utilisateurs filtrés.
    """
    return _users_data


@router.get(
    "/users/{login}",
    response_model=User,
    summary="Obtenir les détails d'un utilisateur par login",
    description="Retourne les informations détaillées d'un utilisateur spécifique via son login, nécessitant une authentification.",
    dependencies=[Depends(get_current_username)]  # Protège la route
)
async def get_user_by_login(login: str):
    """
    Retourne les détails d'un utilisateur par son login.
    Lève une erreur 404 si l'utilisateur n'est pas trouvé.
    """
    for user in _users_data:
        if user.login == login:
            return user

    # Si l'utilisateur n'est pas trouvé, lève une erreur 404 Not Found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Utilisateur '{login}' non trouvé."
    )


@router.get(
    "/users/search/",
    response_model=List[User],
    summary="Rechercher des utilisateurs par mot-clé dans le login",
    description="Recherche les utilisateurs dont le login contient le mot-clé spécifié (non sensible à la casse), nécessitant une authentification.",
    dependencies=[Depends(get_current_username)]  # Protège la route
)
async def search_users(
        q: Optional[str] = Query(None, description="Le mot-clé à rechercher dans le login des utilisateurs.")):
    """
    Retourne les utilisateurs dont le login contient le mot-clé spécifié.
    La recherche est insensible à la casse.
    """
    if not q:
        return _users_data

    # Convertit le mot-clé en minuscules pour une recherche insensible à la casse
    search_query = q.lower()

    # Filtre les utilisateurs dont le login contient le mot-clé
    found_users = [user for user in _users_data if search_query in user.login.lower()]

    return found_users

