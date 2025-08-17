# main_app.py

import sys
import subprocess # Importation nécessaire pour lancer un nouveau processus
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSlot

# Importer notre classe de mise à jour
from updater import Updater

# --- Configuration ---
# L'URL de votre dépôt GitHub (le code doit être dans la branche 'main')
# Exemple : https://github.com/VotreNom/VotreProjet
REPO_URL = "https://github.com/TheoLanles/ZOTA"
# Le nom du fichier que vous voulez mettre à jour.
# ATTENTION : Si vous mettez à jour le fichier principal de l'application (main_app.py),
# assurez-vous que la nouvelle version est compatible, sinon l'application ne démarrera plus.
FILENAME_TO_UPDATE = "main_app.py"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application avec mise à jour ota v1.3")
        self.setGeometry(100, 100, 400, 200)

        # Création de l'interface
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Bienvenue ! Cliquez sur le bouton pour vérifier les mises à jour.")
        self.update_button = QPushButton("Vérifier les mises à jour")

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.update_button)
        self.setCentralWidget(self.central_widget)

        # Connexions
        self.update_button.clicked.connect(self.start_update_check)

        # Préparation du thread pour la mise à jour
        self.update_thread = None
        self.updater = None

    def start_update_check(self):
        """Démarre le processus de mise à jour dans un thread séparé."""
        self.update_button.setEnabled(False)
        self.status_label.setText("Initialisation de la mise à jour...")

        # Crée un nouveau thread et un nouvel objet Updater à chaque fois
        self.update_thread = QThread()
        self.updater = Updater(repo_url=REPO_URL, filename_to_update=FILENAME_TO_UPDATE)

        # Déplace l'updater dans le thread
        self.updater.moveToThread(self.update_thread)

        # Connecte les signaux de l'updater aux slots de la fenêtre principale
        self.updater.status_update.connect(self.update_status_label)
        self.updater.update_finished.connect(self.on_update_complete)

        # Connecte le signal 'started' du thread à la méthode de l'updater
        self.update_thread.started.connect(self.updater.download_and_install_update)

        # Nettoyage après la fin du thread
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.updater.update_finished.connect(self.update_thread.quit)

        self.update_thread.start()

    @pyqtSlot(str)
    def update_status_label(self, message):
        """Met à jour le texte de l'étiquette de statut."""
        self.status_label.setText(message)

    def restart_application(self):
        """Lance une nouvelle instance de l'application et ferme l'actuelle."""
        # Lance un nouveau processus avec le même interpréteur et les mêmes arguments
        subprocess.Popen([sys.executable] + sys.argv)
        # Ferme l'application actuelle
        self.close()

    @pyqtSlot(bool, str)
    def on_update_complete(self, restart_needed, message):
        """Gère la fin du processus de mise à jour."""
        self.status_label.setText(message)
        self.update_button.setEnabled(True)

        if restart_needed:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Redémarrage requis") # Titre de la boîte de dialogue
            msg_box.setText("Mise à jour installée avec succès !")
            msg_box.setInformativeText("Voulez-vous redémarrer l'application maintenant pour appliquer les changements ?")
            # Ajoute les boutons Oui et Non
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)

            # Exécute la boîte de dialogue et récupère le bouton cliqué
            button_clicked = msg_box.exec()

            if button_clicked == QMessageBox.StandardButton.Yes:
                self.restart_application()
            # Si l'utilisateur clique sur Non, l'application reste ouverte mais la mise à jour n'est pas appliquée
            # tant qu'elle n'est pas redémarrée manuellement.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
