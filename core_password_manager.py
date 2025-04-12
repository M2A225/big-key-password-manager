import secrets
import string
import json
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Dict, Optional, Tuple


SALT_FILENAME = "pm_salt.bin"
STORAGE_FILENAME = "passwords.enc"
PBKDF2_ITERATIONS = 48000

# --- 1. Génération de Mot de Passe ---

def generer_mot_de_passe(longueur: int = 20, utiliser_majuscules: bool = True, utiliser_chiffres: bool = True, utiliser_symboles: bool = True) -> str:
    """Génère un mot de passe sécurisé selon les critères."""
    caracteres = string.ascii_lowercase
    if utiliser_majuscules:
        caracteres += string.ascii_uppercase
    if utiliser_chiffres:
        caracteres += string.digits
    if utiliser_symboles:
        caracteres += string.punctuation # '!@#$%^&*()_+-=[]{}|;:,.<>?'

    if not caracteres:
        raise ValueError("Aucun jeu de caractères sélectionné pour la génération.")

    
    mot_de_passe_liste = []
    if utiliser_majuscules:
        mot_de_passe_liste.append(secrets.choice(string.ascii_uppercase))
    if utiliser_chiffres:
        mot_de_passe_liste.append(secrets.choice(string.digits))
    if utiliser_symboles:
        mot_de_passe_liste.append(secrets.choice(string.punctuation))
    
    
    longueur_restante = longueur - len(mot_de_passe_liste)
    for _ in range(longueur_restante):
        mot_de_passe_liste.append(secrets.choice(caracteres))
        
   
    secrets.SystemRandom().shuffle(mot_de_passe_liste)
    
    return "".join(mot_de_passe_liste)


# --- 2. Chiffrement et Déchiffrement ---

def deriver_cle(mot_passe_maitre: bytes, salt: bytes) -> bytes:
    """Dérive une clé de chiffrement depuis le mot de passe maître et un sel."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    cle = base64.urlsafe_b64encode(kdf.derive(mot_passe_maitre))
    return cle

def chiffrer_donnees(cle: bytes, donnees: bytes) -> bytes:
    """Chiffre les données en utilisant la clé dérivée."""
    f = Fernet(cle)
    return f.encrypt(donnees)

def dechiffrer_donnees(cle: bytes, donnees_chiffrees: bytes) -> bytes:
    """Déchiffre les données. Lève InvalidToken ou ValueError."""
    f = Fernet(cle)
    try:
        return f.decrypt(donnees_chiffrees)
    except InvalidToken:
        raise ValueError("Impossible de déchiffrer. Mot de passe maître incorrect ou données corrompues.")


# --- 3. Gestion du Stockage ---

PasswordData = Dict[str, Dict[str, str]] # Type hint pour la structure {site: {user: password}}

def initialiser_stockage() -> str:
    """Crée le fichier de sel s'il n'existe pas. Retourne le chemin du fichier de sel."""
    if not os.path.exists(SALT_FILENAME):
        print(f"Création du fichier de sel: {SALT_FILENAME}")
        salt = os.urandom(16)
        try:
            with open(SALT_FILENAME, "wb") as f_salt:
                f_salt.write(salt)
            print("Fichier de sel créé.")
        except IOError as e:
            print(f"ERREUR: Impossible de créer le fichier de sel: {e}")
            raise # Renvoyer l'erreur
    return SALT_FILENAME

def charger_ou_creer_stockage(mot_passe_maitre: str) -> PasswordData:
    """Charge ou crée le stockage chiffré."""
    try:
        salt_path = initialiser_stockage() # Assure que le sel existe
        with open(salt_path, "rb") as f_salt:
            salt = f_salt.read()
    except (IOError, FileNotFoundError) as e:
        print(f"ERREUR critique: Impossible de lire ou créer le fichier de sel: {e}")
        raise # L'application ne peut pas fonctionner sans sel

    cle = deriver_cle(mot_passe_maitre.encode('utf-8'), salt)

    if not os.path.exists(STORAGE_FILENAME):
        print(f"'{STORAGE_FILENAME}' non trouvé. Création d'un nouveau stockage.")
        try:
            # Crée un fichier vide chiffré
            donnees_vides_chiffrees = chiffrer_donnees(cle, json.dumps({}).encode('utf-8'))
            with open(STORAGE_FILENAME, "wb") as f_storage:
                f_storage.write(donnees_vides_chiffrees)
            return {}
        except IOError as e:
             print(f"ERREUR: Impossible de créer le fichier de stockage initial: {e}")
             raise
    else:
        print(f"Chargement de '{STORAGE_FILENAME}'...")
        try:
            with open(STORAGE_FILENAME, "rb") as f_storage:
                donnees_chiffrees = f_storage.read()
            
            donnees_json = dechiffrer_donnees(cle, donnees_chiffrees)
            passwords_data: PasswordData = json.loads(donnees_json.decode('utf-8'))
            print("Stockage déchiffré avec succès.")
            return passwords_data
        except ValueError as e: # Capturé de dechiffrer_donnees
            print(f"Erreur lors du chargement : {e}")
            raise
        except (IOError, json.JSONDecodeError) as e:
            print(f"ERREUR: Impossible de lire ou décoder le fichier de stockage: {e}")
            raise # Erreur critique

def sauvegarder_stockage(passwords_data: PasswordData, mot_passe_maitre: str):
    """Chiffre et sauvegarde le dictionnaire des mots de passe."""
    try:
        with open(SALT_FILENAME, "rb") as f_salt:
            salt = f_salt.read()
    except (IOError, FileNotFoundError) as e:
         print(f"ERREUR critique: Fichier de sel '{SALT_FILENAME}' introuvable lors de la sauvegarde: {e}")
         raise

    try:
        cle = deriver_cle(mot_passe_maitre.encode('utf-8'), salt)
        donnees_json = json.dumps(passwords_data, indent=4).encode('utf-8')
        donnees_chiffrees = chiffrer_donnees(cle, donnees_json)
        
        with open(STORAGE_FILENAME, "wb") as f_storage:
            f_storage.write(donnees_chiffrees)
        print(f"Stockage sauvegardé dans '{STORAGE_FILENAME}'.")
    except IOError as e:
        print(f"ERREUR: Impossible de sauvegarder le fichier de stockage: {e}")
        raise # Informer l'appelant de l'échec
    except Exception as e:
        print(f"ERREUR inattendue lors de la sauvegarde: {e}")
        raise

# --- 4. Fonctions de Gestion des Entrées (utilisées par la GUI) ---
# Ces fonctions opèrent sur le dictionnaire `passwords_data` en mémoire.

def ajouter_ou_modifier_entree(passwords_data: PasswordData, nom_site: str, nom_utilisateur: str, mot_de_passe: str):
    """Ajoute ou met à jour une entrée."""
    if not nom_site or not nom_utilisateur:
        raise ValueError("Le nom du site et le nom d'utilisateur ne peuvent pas être vides.")
    if nom_site not in passwords_data:
        passwords_data[nom_site] = {}
    passwords_data[nom_site][nom_utilisateur] = mot_de_passe

def recuperer_entree(passwords_data: PasswordData, nom_site: str, nom_utilisateur: str) -> Optional[str]:
    """Récupère le mot de passe pour une entrée."""
    return passwords_data.get(nom_site, {}).get(nom_utilisateur)

def recuperer_utilisateurs_pour_site(passwords_data: PasswordData, nom_site: str) -> list[str]:
     """Retourne la liste des noms d'utilisateur pour un site donné."""
     return list(passwords_data.get(nom_site, {}).keys())

def lister_sites(passwords_data: PasswordData) -> list[str]:
    """Retourne la liste des noms de sites enregistrés."""
    return sorted(list(passwords_data.keys()))

def supprimer_entree(passwords_data: PasswordData, nom_site: str, nom_utilisateur: str) -> bool:
    """Supprime une entrée utilisateur spécifique pour un site."""
    if nom_site in passwords_data and nom_utilisateur in passwords_data[nom_site]:
        del passwords_data[nom_site][nom_utilisateur]
        # Si c'était le dernier utilisateur pour ce site, supprimer le site aussi
        if not passwords_data[nom_site]:
            del passwords_data[nom_site]
        return True
    return False

def supprimer_site(passwords_data: PasswordData, nom_site: str) -> bool:
     """Supprime toutes les entrées pour un site."""
     if nom_site in passwords_data:
         del passwords_data[nom_site]
         return True
     return False

# (Le bloc if __name__ == "__main__": pour le test en ligne de commande peut être gardé ou supprimé)