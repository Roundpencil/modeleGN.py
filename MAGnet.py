import argparse

import GUiSwitch
import lecteurGoogle
from IHM_MAGnet import *


# from maGNette import console_magnet

def main():
    logging.basicConfig(filename='fichier_log.log', encoding='utf-8', level=logging.DEBUG,
                        format='%(asctime)s %(message)s')
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter

    # lecture des paramètres

    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("--intrigue", "-i", type=str, default="-01", help="si une seule intrigue doit être lue")
    group1.add_argument("--allintrigues", "-ai", action="store_true",
                        help="si on veut reparcourir toutes les intrigues")

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("--personnage", "-p", type=str, default="-01", help="si un seul personnage doit être lu")
    group2.add_argument("--allpjs", "-ap", action="store_true", help="si on veut reparcourir tous les pjs")

    parser.add_argument("--initfile", "-f", type=str, default="config.init",
                        help="pour spécifier le fichier d'init à charger")
    parser.add_argument("--nofichiererreurs", "-nfe", action="store_true",
                        help="pour ne pas générer la table des intrigues")
    parser.add_argument("--notableintrigues", "-nti", action="store_true",
                        help="pour ne pas générer la table des intrigues")
    parser.add_argument("--noexportdrive", "-ned", action="store_true", help="pour ne pas provoquer l'export drive")
    parser.add_argument("--nochangelog", "-ncl", action="store_true",
                        help="pour ne pas provoquer la création des changelogs")
    parser.add_argument("--init", "-in", action="store_true", help="fait que la fonction self.load n'est pas appelée")
    parser.add_argument("--nosave", "-ns", action="store_true", help="fait que la focntion GN.save n'est pas appelée")
    parser.add_argument("--verbal", "-v", action="store_true", help="si on veut afficher toutes les erreurs")
    parser.add_argument("--console", "-c", action="store_true",
                        help="pour utiliser MAGnet en mode console")

    args = parser.parse_args()

    # on crée les lecteurs
    # todo : ajouter erreurs sur expiration du token ici
    message = (None, None)
    derniere_version = True

    try:
        api_drive, api_doc, api_sheets = lecteurGoogle.creer_lecteurs_google_apis()
        derniere_version, maj_versions, url_derniere_version = verifier_derniere_version(api_doc)
        # print(f"derniere version = {derniere_version}")
    except Exception as e:
        if "Token has been expired or revoked." in str(e):
            # if token has been expired or revoked, show a popup with a specific error message
            message = ("Expirations des droits",
                       "Le fichier token.json a expiré. \n"
                       "Pas de panique ! \n\n"
                       "1. Supprimez-le \n"
                       "2. Rechargez le fichier de paramètres \n"
                       "3. Suivez les instructions sur la page web google qui s'affiche "
                       "pour vous ré-authentifier \n\n"
                       "Pour plus d'informations sur cette erreur liée à google, consulter le manuel")
            print(f"une erreur RefreshError est survenue pendant la lecture du fichier ini : {e}")

        elif "The OAuth client was deleted." in str(e):
            # if OAuth client was deleted, show a popup with a specific error message
            message = ("Cette version de MAGnet a expiré",
                       "Cette version de MAGnet a expiré. '\n'"
                       "pour continuer à l'utiliser, merci de télécharger la dernière version")

        else:
            # if other RefreshError is raised, show a popup with a generic error message
            message = ("Error", f"Erreur inattendue : {e}")
            logging.debug(f"Erreur inattendue dans la lecture du fichier de configuration : {e}")

    if not args.console:
        print("Lancement de l'IHM")
        root = tk.Tk()
        root.iconbitmap(r'coin-MAGNet.ico')
        style = ttk.Style(root)
        # fenetre_wizard.tk.call('source', 'azure dark/azure dark.tcl')

        if message[0]:
            messagebox.showerror(message[0], message[1])

        if not derniere_version:
            response = messagebox.askquestion("Un nouvelle version est disponible !",
                                              f"souhaitez-vous télécharger la mise à jour ? \n "
                                              f"{maj_versions}",
                                              icon="warning")
            if response == "yes":
                # if "Download" button clicked, open the latest version URL in the web browser
                webbrowser.open_new(url_derniere_version)

        mode_leger = True
        if not mode_leger:
            root.tk.call('source', 'azure3/azure.tcl')
            style.theme_use('azure')
            style.configure("Accentbutton", foreground='white')
            style.configure("Togglebutton", foreground='white')

        app = GUiSwitch.MAGnetMainGUI(mode_leger=mode_leger,
                                      api_drive=api_drive,
                                      api_doc=api_doc,
                                      api_sheets=api_sheets,
                                      master=root)
        app.mainloop()

    if args.console:
        # Code to execute when the -c/--console argument is provided
        print("Exécution de MAGnet en mode console")


if __name__ == '__main__':
    main()
