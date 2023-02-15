
# j'aimerais créer une fonction update_roles_from_drive qui fonctionne comme update_roles_from_csv, mais au lieu de lire un fichier dsv ouvre un document google sheets pour y lire les valeurs
# This content may violate our content policy. If you believe this to be in error, please submit your feedback — your input will aid our research in this area.

# Bien sûr! Pour lire les valeurs d'un document Google Sheets, vous pouvez utiliser l'API Google Sheets. Vous devrez d'abord installer l'API et créer des identifiants de développeur pour obtenir une clé d'accès.
# Une fois que vous avez accès à l'API, vous pouvez utiliser des méthodes pour lire les données d'une feuille de calcul spécifique. Par exemple, pour lire toutes les valeurs d'une feuille de calcul, vous pouvez utiliser la méthode get de la classe api_doc.spreadsheets() de l'API, en spécifiant l'ID de la feuille de calcul et la plage de cellules à lire.

# Voici un exemple de fonction "update_roles_from_drive" qui lira les valeurs d'un document Google Sheets pour mettre à jour les rôles d'une intrigue:

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

def update_roles_from_drive(intrigue, spreadsheet_id, credentials_path):
    # Charger les identifiants d'accès à l'API depuis le fichier json
    credentials = Credentials.from_authorized_user_info(info=json.load(open(credentials_path)))

    # Construire le api_doc Sheets
    sheets_service = build('sheets', 'v4', credentials=credentials)

    # Lire les valeurs de la feuille de calcul
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range='Roles!A:C').execute()
    values = result.get('values', [])

    for i, row in enumerate(values):
        if i == 0:
            # La première ligne contient les titres des colonnes, on l'ignore
            continue
        role_name, perso_name = row[:2]
        perso = GN.nomVersPersonnage(perso_name)
        if perso is None:
            print(f"Le personnage {perso_name} n'a pas été trouvé dans le GN, vérifiez la typo")
            continue
        role = intrigue.get_role_by_name(role_name)
        if role is None:
            print(f"Le role {role_name} n'a pas été trouvé dans l'intrigue {intrigue.nom}, vérifiez la typo")
            continue
        role.personnage = perso
        perso.roles.add(role)



# * ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


# et de la même manière, j'aimerais créer une focntion generate_drive_association qui focntionne comme generate_csv mais avec un document google sheet au lieu d'un csv

# Pour créer la fonction update_roles_from_drive, vous pouvez utiliser la bibliothèque Google Sheets API pour Python. Cette bibliothèque vous permettra de lire les valeurs d'un feuille de calcul Google Sheets en utilisant des requêtes HTTP. Voici un exemple de ce à quoi pourrait ressembler la fonction:

def update_roles_from_drive(gn, spreadsheet_id, sheet_name, verbal=True):
    # Utiliser la bibliothèque Google Sheets API pour ouvrir la feuille de calcul et obtenir les données
    result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    values = result.get('values', [])

    # Parcourir les lignes de données pour mettre à jour les rôles
    for row in values:
        role_name = row[0]
        personnage_name = row[1]

        # trouver le personnage correspondant dans le GN
        personnage = gn.nomVersPersonnage(personnage_name)

        if personnage is None:
            # Si le personnage n'a pas été trouvé, ajouter une erreur au journal d'erreurs
            gn.add_to_error_log(f"Le personnage {personnage_name} n'a pas été trouvé dans le GN")
            if verbal:
                print(f"Le personnage {personnage_name} n'a pas été trouvé dans le GN")
            continue

        # trouver le role correspondant dans les intrigues du GN
        role = None
        for intrigue in gn.intrigues.values():
            role = intrigue.getRoleByName(role_name)
            if role is not None:
                break
        if role is None:
            # Si le rôle n'a pas été trouvé, ajouter une erreur au journal d'erreurs
            gn.add_to_error_log(f"Le rôle {role_name} n'a pas été trouvé dans le GN")
            if verbal:
                print(f"Le rôle {role_name} n'a pas été trouvé dans le GN")
            continue

        # Associer le personnage au rôle
        role.perso = personnage
        personnage.roles.add(role)
    if verbal:
        print("Mise à jour des rôles depuis le drive terminée")


# * ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** **


# peux-tu me redonner le code de generate_drive_association ?

# Pour générer une association à partir d'un document Google Sheet, vous devrez utiliser les bibliothèques Google Sheets API et Google Drive API pour accéder aux données du document. Voici un exemple de code qui montre comment utiliser ces bibliothèques pour lire les données d'un feuille de calcul Google et les utiliser pour générer des associations:

import openai_secret_manager

# on importe les bibliothèques de Google Sheets et Drive
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def generate_drive_association(spreadsheet_id, sheet_name, gn: GN):
    """
    Génère les associations entre les personnages et les rôles à partir d'un document Google Sheet
    :param spreadsheet_id: L'ID du document Google Sheet
    :param sheet_name: Le nom de la feuille de calcul dans le document
    :param gn: L'objet GN sur lequel générer les associations
    """
    try:
        # On récupère les secrets pour l'accès à l'API google
        secrets = openai_secret_manager.get_secret("google")

        # On utilise les secrets pour construire un api_doc Sheets
        sheets_service = build('sheets', 'v4', credentials=secrets)

        # On utilise l'ID du document et le nom de la feuille pour accéder aux données
        result = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
        rows = result.get('values')

        # On parcourt les lignes du tableau pour créer les associations
        for row in rows:
            nom_personnage = row[0]
            nom_role = row[1]

            # On cherche les objets Personnage et Role correspondants
            personnage = gn.nomVersPersonnage(nom_personnage)
            role = gn.nomVersRole(nom_role)

            # On crée l'association entre le personnage et le rôle
            gn.associer_role_a_perso(role, personnage)

    except HttpError as error:
        print(f"An error occurred: {error}")

# Ce code utilise l'ID du document et le nom de la feuille pour accéder aux données du document et parcourt les lignes pour générer des associations en utilisant la fonction self.associer_role_a_perso . N'oubliez pas d'ajouter les bibliothèques google-api-python-client et google-auth-httplib2 pour utiliser ces fonctions


def generer_csv_association(roles_dict, filename):
    # Ouvrir un fichier CSV en mode écriture
    with open(filename, 'w', newline='') as csvfile:
        # Créer un objet CSV writer
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Écrire les en-têtes de colonnes
        writer.writerow(['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage'])
        # Pour chaque rôle dans le dictionnaire de rôles
        for role in roles_dict.values():
            # Récupérer les valeurs de chaque champ
            nom = role.nom
            description = role.description
            pipr = role.pipr
            pipi = role.pipi
            sexe = role.sexe
            personnage = role.personnage if role.personnage else ""
            # Écrire les valeurs dans le fichier CSV
            writer.writerow([nom, description, pipr, pipi, sexe, personnage])
    print("Fichier CSV généré avec succès: {}".format(filename))


def lire_association_roles_depuis_csv(roles_list, filename):
    try:
        # Ouvrir le fichier CSV en mode lecture
        with open(filename, 'r', newline='') as csvfile:
            # Créer un objet CSV reader
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            # Vérifier les en-têtes de colonnes
            headers = next(reader)
            if headers != ['nom', 'description', 'pipr', 'pipi', 'sexe', 'personnage']:
                raise ValueError("Le fichier CSV ne contient pas les bonnes entêtes de colonnes")
            # Pour chaque ligne du fichier CSV
            for row in reader:
                nom = row[0]
                personnage = row[5]

                # et mettre à jour les paramètres du GN en fcontion de ceux du programme > ca se joue à quel niveau?
                # qu'est-ce qui est propriété de quoi? peut-on changer d'association en cours de vie de self?

                # Trouver le rôle correspondant dans la liste de rôles
                role = next((role for role in roles_list if role.nom == nom), None)
                if role:
                    # Mettre à jour le champ personnage de ce rôle
                    role.perso = personnage
            print("Les informations de personnages ont été mises à jour.")
    except FileNotFoundError:
        print(f"Le fichier {filename} n'existe pas.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier: {e}")