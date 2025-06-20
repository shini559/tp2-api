from pydantic import BaseModel, Field
from typing import Optional

# Définit le modèle de données pour un utilisateur GitHub
class User(BaseModel):
    """
    Représente un utilisateur GitHub avec les informations extraites.
    """
    login: str = Field(..., description="Le nom d'utilisateur GitHub.")
    id: int = Field(..., description="L'identifiant unique de l'utilisateur GitHub.")
    avatar_url: str = Field(..., description="L'URL de l'avatar de l'utilisateur.")
    created_at: str = Field(..., description="La date et l'heure de création du compte (format ISO 8601).")
    bio: Optional[str] = Field(None, description="La biographie de l'utilisateur (peut être nulle si non fournie).")

    class Config:
        from_attributes = True
