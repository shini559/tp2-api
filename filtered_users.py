import json
import os
from datetime import datetime

# Chemin vers le fichier d'entrée et de sortie
INPUT_FILE = "data/users.json"
OUTPUT_FILE = "data/filtered_users.json"


def load_users_data(filepath):
    """
    Charge les données des utilisateurs depuis un fichier JSON spécifié.
    Vérifie l'existence du fichier et gère les erreurs de lecture.
    """
    if not os.path.exists(filepath):
        print(f"Erreur : Le fichier '{filepath}' est introuvable. Veuillez d'abord exécuter extract_users.py.")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        return users_data
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON lors de la lecture de '{filepath}' : {e}")
        return None
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la lecture de '{filepath}' : {e}")
        return None


def remove_duplicates(users_data):
    """
    Supprime les doublons basés sur l'identifiant 'id' de l'utilisateur.
    """
    unique_users = {}  # Utilise un dictionnaire pour stocker les utilisateurs uniques par ID
    for user in users_data:
        user_id = user.get('id')
        if user_id is not None:
            unique_users[user_id] = user  # La dernière occurrence pour un ID donné est conservée

    return list(unique_users.values())  # Convertit les valeurs du dictionnaire en liste


def apply_filters(users_data):
    """
    Applique les filtres métier aux utilisateurs :
    - Le champ bio est renseigné (ni vide, ni null)
    - Le champ avatar_url est valide (pas vide)
    - Le champ created_at est postérieur au 1er janvier 2015
    """
    filtered_users = []
    MIN_CREATION_DATE = datetime(2000, 1, 1, 0, 0, 0)  # 1er janvier 2015, minuit

    for user in users_data:
        bio = user.get('bio')
        if not bio:
            continue

        avatar_url = user.get('avatar_url')
        if not avatar_url:
            continue

        created_at_str = user.get('created_at')
        if not created_at_str:
            continue
        try:

            created_at_date = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
            if created_at_date < MIN_CREATION_DATE:
                continue
        except ValueError:
            print(
                f"Avertissement : Format de date invalide pour l'utilisateur {user.get('login')}: {created_at_str}. Skippé.")
            continue


        filtered_users.append(user)

    return filtered_users


def save_to_json(data, filename):
    """
    Sauvegarde une liste de dictionnaires dans un fichier JSON.
    Assure que le répertoire existe et que le JSON est indenté.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            output_data = [
                {
                    'login': user.get('login'),
                    'id': user.get('id'),
                    'created_at': user.get('created_at'),
                    'avatar_url': user.get('avatar_url'),
                    'bio': user.get('bio')
                } for user in data
            ]
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Données sauvegardées avec succès dans : '{filename}'")
    except IOError as e:
        print(f"Erreur lors de l'écriture du fichier JSON '{filename}' : {e}")


if __name__ == "__main__":
    print("Démarrage du pipeline de traitement et de filtrage des utilisateurs.")

    # 1. Chargement des données
    initial_users = load_users_data(INPUT_FILE)
    if initial_users is None:
        print("Arrêt du script en raison d'une erreur de chargement.")
        exit(1)

    num_loaded = len(initial_users)
    print(f"'{num_loaded}' utilisateurs chargés depuis '{INPUT_FILE}'.")

    # 2. Suppression des doublons
    deduplicated_users = remove_duplicates(initial_users)
    num_duplicates_removed = num_loaded - len(deduplicated_users)
    print(f"'{num_duplicates_removed}' doublons supprimés.")

    # 3. Application des filtres métier
    final_filtered_users = apply_filters(deduplicated_users)
    num_filtered_out = len(deduplicated_users) - len(final_filtered_users)
    print(f"'{num_filtered_out}' utilisateurs filtrés par les critères métier.")

    # 4. Enregistrement des résultats
    if final_filtered_users:
        save_to_json(final_filtered_users, OUTPUT_FILE)
    else:
        print(
            "Aucun utilisateur ne correspond aux critères de filtrage. Le fichier de sortie ne sera pas créé ou sera vide.")

    # 5. Affichage du résumé
    print("\n--- Rapport de traitement ---")
    print(f"Utilisateurs chargés : {num_loaded}")
    print(f"Doublons supprimés : {num_duplicates_removed}")
    print(f"Utilisateurs filtrés (après déduplication et filtres) : {len(final_filtered_users)}")
    print("-----------------------------")