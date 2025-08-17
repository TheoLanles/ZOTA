import hashlib
import json
import os

def calculate_sha256(filepath: str) -> str:
    """
    Calcule le hachage SHA256 d'un fichier donné.
    Lit le fichier par blocs pour gérer efficacement les grands fichiers.
    """
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192): # Lire par blocs de 8 Ko
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{filepath}' n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Une erreur est survenue lors du calcul du SHA256 pour '{filepath}' : {e}")
        return None

def main():
    """
    Fonction principale du CLI pour générer le fichier version.json.
    Demande le nom du fichier Python et la nouvelle version.
    """
    print("--- Générateur de fichier version.json ---")

    # Demander le nom du fichier Python à vérifier
    python_file = input("Entrez le nom du fichier Python à vérifier (ex: main_app.py) : ").strip()

    # Vérifier si le fichier existe avant de continuer
    if not os.path.exists(python_file):
        print(f"Le fichier '{python_file}' n'existe pas. Veuillez vérifier le chemin et le nom du fichier.")
        return

    # Demander la nouvelle version
    new_version = input("Entrez la nouvelle version (ex: 1.0.1, 2.0) : ").strip()

    if not new_version:
        print("La version ne peut pas être vide. Opération annulée.")
        return

    # Calculer le hachage SHA256 du fichier spécifié
    print(f"Calcul du hachage SHA256 pour '{python_file}'...")
    checksum = calculate_sha256(python_file)

    if checksum is None:
        print("Échec du calcul du hachage. Le fichier version.json ne sera pas généré.")
        return

    print(f"Hachage SHA256 calculé : {checksum}")

    # Préparer les données pour le fichier JSON
    version_data = {
        "version": new_version,
        "sha256_checksum": checksum
    }

    # Définir le nom du fichier de sortie
    output_filename = "output.json"

    # Écrire les données dans le fichier JSON
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=4)
        print(f"Le fichier '{output_filename}' a été généré avec succès !")
        print(f"Contenu de {output_filename}:")
        print(json.dumps(version_data, indent=4))
    except Exception as e:
        print(f"Une erreur est survenue lors de la création du fichier '{output_filename}' : {e}")

if __name__ == "__main__":
    main()
