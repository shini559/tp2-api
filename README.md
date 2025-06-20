# Projet: Construction d’un pipeline API complet en Python avec GitHub et FastAPI 

## Description du Projet

Ce projet vise à créer un pipeline complet pour extraire, nettoyer et exposer des données d'utilisateurs GitHub via une API REST sécurisée. L'objectif est de simuler une API interne pour d'autres développeurs, offrant un accès filtré et pertinent aux profils GitHub.

Le pipeline se compose de trois étapes principales :

1. **Extraction des données** : Collecte des profils utilisateurs depuis l'API publique de GitHub.
2. **Filtrage et nettoyage des données** : Traitement des données brutes pour supprimer les doublons et appliquer des critères métier.
3. **Exposition de l'API REST** : Création d'une API sécurisée avec FastAPI pour consulter les utilisateurs filtrés.

---

## Structure du Projet

Voici l'arborescence du projet :

```
tp2-api/
├── extract_users.py             # Script d'extraction depuis l’API GitHub
├── filtered_users.py            # Script de filtrage métier
├── data/
│   ├── users.json               # Données brutes extraites par extract_users.py
│   └── filtered_users.json      # Données nettoyées et filtrées par filtered_users.py
├── api/
│   ├── __init__.py              # Rend 'api' un package Python
│   ├── main.py                  # Lancement de l’API FastAPI
│   ├── models.py                # Schémas Pydantic (structure des données utilisateur)
│   ├── routes.py                # Définition des endpoints de l'API
│   └── security.py              # Gestion de l’authentification HTTP Basic
├── tests/
│   └── test_api.py              # Tests unitaires pour l'API (facultatif)
├── .env                         # Fichier de variables d'environnement (secrets, identifiants API)
├── .env.example                 # Exemple de fichier d’environnement
├── README.md                    # Ce fichier de documentation
└── requirements.txt             # Dépendances Python du projet
```

---

## Scripts du Projet

### `extract_users.py`

**Objectif** : Extraire des informations d'utilisateurs GitHub depuis l'API publique ([https://api.github.com/users](https://api.github.com/users)).

**Fonctionnalités** :

- Récupération par lots (30 utilisateurs par requête).
- Extraction des champs : `login`, `id`, `avatar_url`, `created_at`, `bio`.
- Gestion automatique de la pagination en utilisant l'id du dernier utilisateur.
- Respect des limitations de l'API GitHub (quota de 5000 requêtes/heure avec token), avec pause automatique si nécessaire.
- Gestion robuste des erreurs HTTP (403 Forbidden, 429 Too Many Requests, 5xx Server Errors) avec réessais progressifs.
- Stockage des données brutes dans `data/users.json`.

**Utilisation** :

```bash
python extract_users.py --max-users <nombre_max_utilisateurs>
```

### `filtered_users.py`

**Objectif** : Nettoyer et filtrer les données brutes extraites par `extract_users.py`.

**Fonctionnalités** :

- Lecture des données depuis `data/users.json`.
- Suppression des doublons basés sur l'identifiant unique `id`.
- Application de filtres métier :
  - Le champ `bio` doit être renseigné.
  - Le champ `avatar_url` doit être valide.
  - Le compte `created_at` doit être postérieur au 1er janvier 2015.
- Sauvegarde des données nettoyées et filtrées dans `data/filtered_users.json`.
- Affichage d'un rapport de traitement.

**Utilisation** :

```bash
python filtered_users.py
```

---

## Dossier `api/` (Application FastAPI)

**Objectif** : Exposer les données filtrées via une API REST.

- `main.py` : Point d'entrée de l'application FastAPI. Configure les métadonnées de l'API et inclut les routes.
- `models.py` : Définit le schéma Pydantic `User` pour la validation et la documentation des données utilisateur.
- `routes.py` : Définit les différents endpoints de l'API (`/users/`, `/users/{login}`, `/users/search?q=...`) et charge les données filtrées au démarrage de l'application.
- `security.py` : Gère l'authentification HTTP Basic, en lisant les identifiants depuis les variables d'environnement (`.env`).

---
## Variables d'Environnement (.env)

Le projet utilise un fichier `.env` pour stocker les variables d'environnement sensibles, comme le token GitHub et les identifiants de l'API.

Créez un fichier nommé `.env` à la racine du projet avec le contenu suivant :

```bash
GITHUB_TOKEN="Ici votre token GitHub"
API_USERNAME="Votre nom d'utilisateur API"
API_PASSWORD="Votre mot de passe API"
```

Remplacez les valeurs par vos propres identifiants.

---

## Installation et Lancement

### 1. Cloner le dépôt et naviguer dans le dossier

```bash
git clone https://github.com/votre-utilisateur/tp2-api.git
cd tp2-api/
```

### 2. Créer l'environnement virtuel (recommandé)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Générer les données d'utilisateurs brutes

```bash
python3 extract_users.py --max-users 120 # Par exemple, pour extraire 120 utilisateurs
```

### 5. Nettoyer et filtrer les données

```bash
python3 filtered_users.py
```

### 6. Lancer l'API FastAPI

```bash
uvicorn api.main:app --reload --port 8000 # Utilisez --reload pour le rechargement automatique en développement et --port pour spécifier le port
```

L'API sera accessible à l'adresse `http://127.0.0.1:8000`.

---

## Tester l'API

### Via l'interface Swagger UI

Ouvrez : `http://localhost:8000/docs`

### Via la ligne de commande (curl)

Exemple pour obtenir les détails d'un utilisateur :

```bash
curl -u your_api_username:your_api_password http://localhost:8000/users/mojombo
```

Exemple de réponse :

```json
{
  "login": "mojombo",
  "id": 1,
  "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4",
  "created_at": "2007-10-20T05:24:19Z",
  "bio": "Developer, entrepreneur & investor in startups."
}
```

---

##  Contribution

Les contributions sont les bienvenues ! Tu peux :
- proposer des améliorations,
- signaler des bugs,
- ajouter de nouvelles fonctionnalités.


---