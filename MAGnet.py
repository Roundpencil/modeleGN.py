import argparse
import logging
from IHM_MAGnet import *


# from maGNette import console_magnet

def main():
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
    sys.setrecursionlimit(5000)  # mis en place pour prévenir pickle de planter

    # lecture des paramètres

    parser = argparse.ArgumentParser()

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("--intrigue", "-i", type=str, default="-01", help="si une seule intrigue doit être lue")
    group1.add_argument("--allintrigues", "-ai", action="store_true",
                        help="si on veut reparcourir toutes les intrigues")

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("--perso", "-p", type=str, default="-01", help="si un seul perso doit être lu")
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
    # args = parser.parse_args()
    #
    # args, unknown_args = parser.parse_known_args()

    # if not args.console and unknown_args:
    #     raise Exception("-c/--console est nécessaire pour passer en mode ligne de commande")
    #
    # if not args.console and not unknown_args:
    #     print("Lancement de l'IHM")
    #     root = tk.Tk()
    #     app = Application(master=root)
    #     app.mainloop()
    #
    # if args.console:
    #     print("Exécution de MAGnet en mode console")

    args = parser.parse_args()

    # if args.console and len(args.__dict__) > 0:
    #     print(f"{args.console}, {args.__dict__}")
    #     raise Exception("-c/--console est nécessaire pour passer en mode ligne de commande")

    if not args.console:
        print("Lancement de l'IHM")
        root = tk.Tk()
        app = Application(master=root)
        app.mainloop()

    if args.console:
        # Code to execute when the -c/--console argument is provided
        print("Exécution de MAGnet en mode console")


if __name__ == '__main__':
    main()
