import requests
import json
import time
import os
import argparse
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Headers pour l'authentification
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# URL de base de l'API GitHub
BASE_URL = "https://api.github.com/users"
OUTPUT_FILE = "data/users.json"  # Chemin vers le fichier de sortie JSON

# Paramètres de réessai
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5  # Délai initial avant de réessayer


def handle_rate_limit(response_headers):
    """
    Vérifie les en-têtes de limitation de débit et met le script en pause si nécessaire.
    """
    remaining = int(response_headers.get('X-RateLimit-Remaining', 1))
    reset_time = int(response_headers.get('X-RateLimit-Reset', 0))
    current_time = time.time()

    if remaining == 0:
        sleep_time = reset_time - current_time + 5  # Marge de 5 secondes
        if sleep_time > 0:
            print(f"\n--- Quota API atteint ! Mise en pause pour {int(sleep_time)} secondes. ---")
            print(f"Reprise prévue à : {time.ctime(reset_time)}")
            time.sleep(sleep_time)
            print("--- Reprise des opérations. ---\n")
        else:
            print(
                "\n--- Quota API potentiellement atteint, mais temps de réinitialisation déjà passé. Attente courte de 10 secondes. ---")
            time.sleep(10)


def fetch_url(url, attempt=1):
    """
    Effectue une requête GET simple, gère les erreurs de base, les quotas et les réessais.
    Retourne la réponse JSON ou None en cas d'échec persistant.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        handle_rate_limit(response.headers)  # Gère les pauses pour le quota

        # Gérer les erreurs HTTP spécifiques
        if response.status_code == 403:
            print(f"Erreur 403 Forbidden à {url}. Vérifiez votre token GitHub et le quota API.")

            time.sleep(RETRY_DELAY_SECONDS * 2)
            return None

        if response.status_code == 429:
            print(f"Erreur 429 Too Many Requests à {url}. Attente avant de réessayer.")
            time.sleep(RETRY_DELAY_SECONDS * attempt)
            if attempt < MAX_RETRIES:
                print(f"Réessai ({attempt + 1}/{MAX_RETRIES}) pour {url}...")
                return fetch_url(url, attempt + 1)
            else:
                print(f"Échec persistant après {MAX_RETRIES} tentatives pour {url}.")
                return None

        if 500 <= response.status_code < 600:
            print(f"Erreur serveur (5xx) à {url}: {response.status_code}. Attente avant de réessayer.")
            time.sleep(RETRY_DELAY_SECONDS * attempt)
            if attempt < MAX_RETRIES:
                print(f"Réessai ({attempt + 1}/{MAX_RETRIES}) pour {url}...")
                return fetch_url(url, attempt + 1)
            else:
                print(f"Échec persistant après {MAX_RETRIES} tentatives pour {url}.")
                return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau ou inattendue lors de la requête à {url}: {e}")
        time.sleep(RETRY_DELAY_SECONDS * attempt)
        if attempt < MAX_RETRIES:
            print(f"Réessai ({attempt + 1}/{MAX_RETRIES}) pour {url} suite à une erreur réseau...")
            return fetch_url(url, attempt + 1)
        else:
            print(f"Échec persistant après {MAX_RETRIES} tentatives pour {url}.")
            return None


def extract_github_users(num_users_to_fetch):
    """
    Extrait un nombre spécifié d'utilisateurs de l'API GitHub, gère la pagination et les quotas.
    """
    all_extracted_users = []
    current_since_id = 0
    fetched_count = 0

    print(f"Démarrage de l'extraction de {num_users_to_fetch} utilisateurs GitHub...")

    while fetched_count < num_users_to_fetch:
        users_list_url = f"{BASE_URL}?since={current_since_id}"
        print(f"Requête pour les utilisateurs depuis l'ID : {current_since_id}")

        users_batch = fetch_url(users_list_url)

        if users_batch is None:
            print("Erreur non récupérable lors de la récupération du lot initial. Arrêt de l'extraction.")
            break

        if not users_batch:
            print("Plus d'utilisateurs disponibles ou fin de l'API. Arrêt de l'extraction.")
            break

        for user_summary in users_batch:
            if fetched_count >= num_users_to_fetch:
                break

            login = user_summary.get('login')
            user_id = user_summary.get('id')

            if login and user_id is not None:
                user_detail_url = f"{BASE_URL}/{login}"
                print(
                    f"  Traitement de l'utilisateur : {login} (ID: {user_id}). Total traités : {fetched_count + 1}/{num_users_to_fetch}")
                details = fetch_url(user_detail_url)

                if details:
                    extracted_user = {
                        'login': login,
                        'id': user_id,
                        'avatar_url': details.get('avatar_url'),
                        'created_at': details.get('created_at'),
                        'bio': details.get('bio')
                    }
                    all_extracted_users.append(extracted_user)
                    fetched_count += 1
                else:
                    print(f"    Impossible de récupérer les détails pour {login} après réessais. Skippé.")
            else:
                print(f"  Utilisateur sans login ou ID dans le lot. Skippé : {user_summary}")

        if users_batch:
            current_since_id = users_batch[-1]['id']

        time.sleep(1)

    print(f"\nExtraction terminée. Total d'utilisateurs extraits : {len(all_extracted_users)}.")
    return all_extracted_users


def save_to_json(data, filename):
    """
    Sauvegarde une liste de dictionnaires dans un fichier JSON.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Données sauvegardées avec succès dans : {filename}")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier JSON {filename}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrait des utilisateurs depuis l'API GitHub.")
    parser.add_argument(
        "--max-users",
        type=int,
        default=120,
        help="Nombre maximum d'utilisateurs à extraire (par défaut: 120)."
    )

    args = parser.parse_args()

    if not GITHUB_TOKEN:
        print(
            "Erreur: Le token GitHub n'a pas été trouvé. Assurez-vous que le fichier .env existe et contient GITHUB_TOKEN.")
        print("Il doit être dans le dossier racine 'tp-apidelet-c1-c5/'")
        exit(1)

    NUM_USERS_TO_COLLECT = args.max_users

    users = extract_github_users(NUM_USERS_TO_COLLECT)

    if users:
        save_to_json(users, OUTPUT_FILE)
    else:
        print("Aucun utilisateur n'a été extrait ou une erreur majeure est survenue.")