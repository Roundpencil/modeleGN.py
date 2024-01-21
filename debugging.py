from MAGnet import *
def kalitt_debug():
    gn: GN = GN.load('archive chalacta.mgn')
    noms = [perso.nom for perso in gn.personnages.values()]
    print(noms)
    kalitt = next(perso for perso in gn.personnages.values() if 'Kalit' in perso.nom)
    texte_kalitt = generer_squelette_perso(gn, kalitt)
    print(texte_kalitt)
    drive, doc, sheet = lecteurGoogle.creer_lecteurs_google_apis()



kalitt_debug()