# ZOTA - Application de Bureau avec Mise à Jour OTA

## Table des matières
- [Description du projet](#description-du-projet)  
- [Fonctionnalités](#fonctionnalités)  
- [Prérequis](#prérequis)  
- [Installation](#installation)  
- [Utilisation](#utilisation)  
- [Mécanisme de Mise à Jour OTA](#mécanisme-de-mise-à-jour-ota)  
  - [Comment cela fonctionne](#comment-cela-fonctionne)  
  - [Générer le versionjson](#générer-le-versionjson) 
- [Licence](#licence)  

---

## Description du projet
**ZOTA** est une application de bureau Python simple, construite avec **PyQt6**, qui sert de démonstration pour un système de mise à jour **Over-The-Air (OTA)**.  

Elle permet à l'application de vérifier et télécharger automatiquement les dernières versions de son code directement depuis un dépôt GitHub, garantissant que les utilisateurs ont toujours la version la plus récente **sans avoir à la retélécharger manuellement**.

---

## Fonctionnalités
- **Interface utilisateur simple** : Fenêtre PyQt6 basique pour interagir.  
- **Vérification manuelle des mises à jour** : Bouton pour déclencher la recherche de mises à jour.  
- **Mises à jour OTA** : Télécharge et installe de nouvelles versions directement depuis GitHub.  
- **Gestion de version sémantique** : Utilise `packaging` pour comparer les versions (ex: `1.0` vs `1.0.1`).  
- **Vérification d’intégrité** : Hachage **SHA256** pour garantir l’authenticité des fichiers.  
- **Sauvegarde automatique** : Création d’un fichier `.bak` avant remplacement, permettant un retour arrière manuel.  
- **Redémarrage de l’application** : Invite l’utilisateur à relancer l’application après une mise à jour réussie.  
- **Statut en temps réel** : Affiche la progression et les messages dans l’interface.  

---

## Prérequis
- Python **3.x** installé.  
- Dépendances nécessaires :  
  - `PyQt6`  
  - `requests`  
  - `packaging`  

Installation des dépendances :  
```bash
pip install -r requirements.txt
```

---

## Installation
Cloner le dépôt :  
```bash
git clone https://github.com/TheoLanles/ZOTA.git
cd ZOTA
```

Installer les dépendances :  
```bash
pip install -r requirements.txt
```

---

## Utilisation
Lancer l’application :  
```bash
python main_app.py
```

- Une fenêtre s’ouvre avec un message de bienvenue et un bouton **Vérifier les mises à jour**.  
- En cliquant dessus, l’application contacte le dépôt GitHub pour vérifier la disponibilité d’une nouvelle version.  
- Les messages d’état apparaissent dans l’interface.  
- En cas de mise à jour, une boîte de dialogue propose de **redémarrer l’application**.  

---

## Mécanisme de Mise à Jour OTA

Le système repose sur trois fichiers principaux :  
- **`updater.py`**  
- **`main_app.py`**  
- **`version.json`**

### Comment cela fonctionne
- **`updater.py`** (exécuté dans un thread séparé) :  
  - Lit la version locale depuis `version.json`.  
  - Récupère la dernière version et le hachage SHA256 depuis GitHub.  
  - Compare les versions.  
  - Télécharge la nouvelle version si disponible.  
  - Vérifie l’intégrité via SHA256.  
  - Sauvegarde l’ancienne version `.bak`.  
  - Remplace le fichier par le nouveau.  
  - Met à jour le `version.json` local.  

- **`main_app.py`** : Application principale gérant l’UI, les statuts et le redémarrage.  

- **`version.json`** : Contient la version actuelle et le hachage SHA256 du fichier correspondant.  

Exemple sur GitHub :  
```json
{
  "version": "1.0.1",
  "sha256_checksum": "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
}
```

---

### Générer le version.json
Pour préparer une nouvelle version :  

1. Mettre à jour le fichier de l’application (ex: `main_app.py`).  
2. Exécuter le script CLI :  
   ```bash
   python update_auto.py
   ```
3. Le script demande :  
   - Le fichier à vérifier (ex: `main_app.py`).  
   - La nouvelle version (ex: `1.0.1`).  
4. Un fichier **`output.json`** est généré.  
5. Copier son contenu dans le **`version.json`** du dépôt GitHub.  

---

## Licence
Projet sous licence **MIT**.  
Voir le fichier [LICENSE](LICENSE) pour plus de détails.
