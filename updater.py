# updater.py

import os
import sys
import json
import requests
from time import sleep
from packaging.version import parse, Version # Importation de parse et Version

# Importations PyQt6 nécessaires pour les signaux
from PyQt6.QtCore import QObject, pyqtSignal

class Updater(QObject):
    """
    Cette classe gère les mises à jour OTA pour une application de bureau Python.
    Elle vérifie les mises à jour sur un dépôt GitHub, les télécharge et les installe.
    Elle est conçue pour fonctionner dans un thread séparé afin de ne pas bloquer l'interface utilisateur.
    """

    # Définition des signaux pour communiquer avec le thread principal
    status_update = pyqtSignal(str)  # Signal pour envoyer des messages de statut
    update_finished = pyqtSignal(bool, str) # Signal pour indiquer la fin (bool: redémarrage nécessaire, str: message final)

    def __init__(self, repo_url, filename_to_update):
        super().__init__()
        self.filename_to_update = filename_to_update
        self.repo_url = repo_url

        # Transformer l'URL GitHub standard en URL de contenu brut (raw)
        if "github.com" in self.repo_url:
            self.repo_url = self.repo_url.replace("github.com", "raw.githubusercontent.com")
            # Assurer qu'il n'y a pas de "/blob/" dans l'URL qui est souvent ajouté par le navigateur
            self.repo_url = self.repo_url.replace("/blob/", "/")

        self.version_url = f"{self.repo_url}/main/version.json"
        self.firmware_url = f"{self.repo_url}/main/{self.filename_to_update}"

        self.current_version = self._get_current_version()

    def _get_current_version(self) -> Version:
        """
        Lit la version actuelle depuis le fichier local 'version.json'.
        Gère les formats de version comme '1.0', '1.0.0', etc.
        Retourne un objet Version pour des comparaisons robustes.
        """
        version_file = 'version.json'
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                    # Récupère la version sous forme de chaîne et la parse.
                    # Utilise '0.0.0' comme valeur par défaut si la clé est manquante.
                    version_str = str(version_data.get('version', '0.0.0'))
                    return parse(version_str)
            except (json.JSONDecodeError, IOError) as e:
                # Émet un signal de statut en cas d'erreur de lecture
                self.status_update.emit(f"Erreur de lecture de {version_file} : {e}")
                return parse('0.0.0') # Retourne une version par défaut en cas d'erreur
        else:
            # Si le fichier n'existe pas, on suppose la version '0.0.0' et on le crée
            initial_version = '0.0.0'
            try:
                with open(version_file, 'w') as f:
                    json.dump({'version': initial_version}, f)
                return parse(initial_version)
            except IOError as e:
                self.status_update.emit(f"Erreur de création de {version_file} : {e}")
                return parse('0.0.0')

    def _check_connection(self):
        """Vérifie si une connexion Internet est active."""
        try:
            # Fait une requête légère à un serveur fiable
            requests.head("https://www.google.com", timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def download_and_install_update(self):
        """
        Méthode principale qui orchestre le processus de mise à jour.
        Doit être appelée après avoir déplacé l'objet dans un thread.
        """
        self.status_update.emit("Vérification de la connexion Internet...")
        if not self._check_connection():
            self.status_update.emit("Pas de connexion Internet.")
            self.update_finished.emit(False, "Échec : Pas de connexion Internet.")
            return

        self.status_update.emit(f"Version actuelle : {self.current_version}")
        self.status_update.emit("Recherche de mises à jour...")

        try:
            # 1. Obtenir la dernière version depuis le dépôt
            response = requests.get(self.version_url)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

            # IMPORTANT : Parser la version distante en objet Version pour une comparaison correcte
            latest_version_str = response.json().get('version', '0.0.0')
            latest_version = parse(str(latest_version_str)) # Assurez-vous que c'est une chaîne avant de parser

            self.status_update.emit(f"Dernière version disponible : {latest_version}")

            # 2. Comparer les versions (maintenant les deux sont des objets Version)
            if self.current_version >= latest_version:
                self.status_update.emit("Aucune nouvelle mise à jour disponible.")
                self.update_finished.emit(False, "Votre application est à jour.")
                return

            # 3. Télécharger le nouveau code
            self.status_update.emit(f"Téléchargement de la nouvelle version depuis {self.firmware_url}...")
            firmware_response = requests.get(self.firmware_url)
            firmware_response.raise_for_status()
            latest_code = firmware_response.text

            # 4. Sauvegarder le nouveau code dans un fichier temporaire
            temp_filename = "latest_code.tmp"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                f.write(latest_code)

            # 5. Mettre à jour le fichier de version local avec la nouvelle version
            with open('version.json', 'w') as f:
                json.dump({'version': str(latest_version)}, f) # Sauvegarde en tant que chaîne

            # 6. Remplacer l'ancien fichier par le nouveau
            # Cette opération est critique. Si elle échoue, l'application peut être corrompue.
            self.status_update.emit(f"Installation de la mise à jour (remplacement de {self.filename_to_update})...")
            os.replace(temp_filename, self.filename_to_update) # os.replace est atomique sur la plupart des OS

            self.status_update.emit("Mise à jour terminée. Veuillez redémarrer l'application.")
            self.update_finished.emit(True, "Mise à jour installée avec succès !")

        except requests.exceptions.RequestException as e:
            self.status_update.emit(f"Erreur réseau : {e}")
            self.update_finished.emit(False, f"Échec de la mise à jour : {e}")
        except (KeyError, json.JSONDecodeError):
            self.status_update.emit("Erreur : le fichier version.json distant est mal formé ou la clé 'version' est manquante.")
            self.update_finished.emit(False, "Échec : Fichier de version distant invalide.")
        except Exception as e:
            # Capture toutes les autres exceptions inattendues
            self.status_update.emit(f"Une erreur inattendue est survenue : {e}")
            self.update_finished.emit(False, f"Échec : Erreur inattendue ({e}).")
