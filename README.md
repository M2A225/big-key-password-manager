# Big Key - Gestionnaire de Mots de Passe Simple

Big Key est une application de bureau simple pour gérer vos mots de passe de manière sécurisée. Elle utilise le chiffrement pour protéger vos données sensibles stockées localement.

## Fonctionnalités

* **Stockage Sécurisé :** Les mots de passe sont chiffrés avant d'être sauvegardés dans un fichier local.
* **Interface Graphique Simple :** Interface utilisateur conviviale construite avec CustomTkinter.
* **Ajout Facile :** Ajoutez de nouvelles entrées (site web/service, nom d'utilisateur, mot de passe).
* **Recherche/Affichage :** Visualisez les mots de passe enregistrés (après authentification).
* **(Optionnel - à vérifier si implémenté)** Génération de mots de passe.
* **Copie dans le Presse-papiers :** Copiez facilement les mots de passe dans le presse-papiers.

## Prérequis

* Python 3.x
* Les bibliothèques listées dans `requirements.txt`.

## Installation et Lancement (depuis le code source)

1.  **Cloner ou télécharger le dépôt/code source.**
2.  **Naviguer jusqu'au dossier du projet :**
    ```bash
    cd chemin/vers/big_key
    ```
3.  **Créer et activer un environnement virtuel (recommandé) :**
    ```bash
    # Créer l'environnement (une seule fois)
    python -m venv env 
    # Activer l'environnement (à chaque fois que vous travaillez sur le projet)
    # Sur Windows:
    .\env\Scripts\activate
    # Sur macOS/Linux:
    # source env/bin/activate 
    ```
4.  **Installer les dépendances :**
    *(Il est recommandé de créer un fichier `requirements.txt` en exécutant `pip freeze > requirements.txt` dans votre environnement activé une fois que tout fonctionne)*
    ```bash
    pip install -r requirements.txt 
    ```
    *Ou, si vous n'avez pas de fichier `requirements.txt` :*
    ```bash
    pip install customtkinter cryptography pyperclip
    ```
5.  **Lancer l'application :**
    ```bash
    python main_gui.py
    ```

## Création de l'exécutable (`.exe` pour Windows)

Si vous souhaitez créer un fichier exécutable autonome pour Windows :

1.  Assurez-vous d'avoir activé votre environnement virtuel (`.\env\Scripts\activate`).
2.  Installez PyInstaller : `pip install pyinstaller`
3.  Lancez la commande de build depuis le dossier `big_key` :
    ```bash
    pyinstaller --onefile --windowed --name BigKey main_gui.py
    ```
    *(Ajoutez `--add-data "env/Lib/site-packages/customtkinter;customtkinter"` ou une option similaire si vous rencontrez des problèmes avec les ressources de CustomTkinter).*
4.  L'exécutable `BigKey.exe` sera créé dans le sous-dossier `dist`.

## Utilisation

1.  Lancez l'application (via `python main_gui.py` ou l'exécutable `.exe`).
2.  **(Hypothèse)** Entrez un mot de passe principal pour déverrouiller/déchiffrer vos données.
3.  Utilisez les boutons pour ajouter, rechercher, ou copier des informations d'identification.
4.  Les données sont sauvegardées (probablement dans un fichier `.json` ou `.txt` chiffré) lorsque vous ajoutez/modifiez des entrées ou fermez l'application.


---

*Développé par [appolinaire motche]*