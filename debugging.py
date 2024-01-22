from MAGnet import *
def kalitt_debug():
    nom_perso = 'Brance'
    nom_gn = 'archive chalacta.mgn'
    debug_perso_gn(nom_gn, nom_perso)


def debug_perso_gn(nom_gn, nom_perso):
    gn: GN = GN.load(nom_gn)
    noms = [perso.nom for perso in gn.personnages.values()]
    # print(noms)
    kalitt = next(perso for perso in gn.personnages.values() if nom_perso in perso.nom)
    texte_kalitt = generer_squelette_perso(gn, kalitt)
    # print(texte_kalitt)
    api_drive, api_doc, sheet = lecteurGoogle.creer_lecteurs_google_apis()
    nom_fichier = 'test export requete'
    texte = generer_squelette_perso(gn, kalitt)
    parent = '1gYWJepb9U2uYOS-4bW5_uLGnFrj5nzmn'
    mon_id = g_io.creer_google_doc(api_drive, nom_fichier, parent)
    g_io.write_to_doc(
        api_doc, mon_id, texte, verbal=True
    )


# kalitt_debug()

debug_perso_gn('Demo.mgn', 'Corwin')