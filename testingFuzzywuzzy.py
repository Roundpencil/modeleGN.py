from fuzzywuzzy import process
from modeleGN import *
import doc2Intrigue

def main():
    nomspersos = ["Anko Siwa", "Ashaya Asty", "Aved - 4V-3D", "Axel Brance", "Bynar Siwa", "Dal Joval D'rasnov", "Desnash Rhylee", "Dophine Rhue", "Driss Ranner", "Edrik Vance", "Greeta Asty", "Hart Do", "Havok", "Hog'Gemod Ippolruna", "Isayjja Kahl", "Jaldine Gerams", "Jay Mozel", "Jerima D'rasnov", "Jish Zyld", "Jory Asty", "Kael Sin", "Kalitt", "Kess Horoby", "Kianstev Nacram", "Korrgaarr Gguurd'k", "KR3-NC0", "Kyle Talus", "Kyrielle Viszla", "Lars Duskon", "Lexi Ipolruna", "Mano Tori", "Mina Tarkin", "Naka Kushir", "Naam Poorf", "Nemko Var", "Nexxar Graam", "NT 346/bredan", "Oni Lux", "Pregda Snorn", "Rhebanxx Kar", "Rika Sant", "Rimo Twil", "Saryth D'rasnov", "Seika", "Sirudan Bonte", "Slayke Jontab", "Sol Preeda - Soree", "Tarik Koma", "Teysa Cio", "Thuorn Hermon", "Timagua", "Trevek", "Tristan Wrenn", "Tsvan Kessig", "Val Krendel", "Valin​ Hess", "Vauber Brasell", "Wexley Ello", "Wor Monba", "Xabria", "Yulsa Nazdij", "Zaar Tamwi", "Zagrinn Vrask", "Zoln Ubri"]
    monGN = GN()

    for perso in nomspersos:
        monGN.personnages[perso] = Personnage(nom=perso, pj=True)

    monGN = GN.load("archive Chalacta")
    monGN.updateOldestUpdate()
    listerRolesPerso(monGN, "Kyle Talus")
    doc2Intrigue.extraireIntrigues(monGN, singletest="-01")
    listerRolesPerso(monGN, "Kyle Talus")
    # doc2Intrigue.extraireIntrigues(monGN)
    # monGN.updateOldestUpdate()
    # monGN.save("archive Chalacta")

    # afficherLesPersos(monGN)
    # afficherDatesScenes(monGN)
    # genererCsvOrgaIntrigue(monGN)
    # listerLesRoles(monGN)
    # del monGN.intrigues['1gf3VUIophPUIgu6EPmubO0kPiOwAx9-3DacvVEfAgiw']
    # listerDatesIntrigues(monGN)

    ## test de la fonction d'effaçage'
    # testEffacerIntrigue(monGN)

    # print(" l'intrigue la plus ancienne est {0}, c'est {1}, maj : {2}".format(monGN.idOldestUpdate, monGN.intrigues[monGN.idOldestUpdate], monGN.oldestUpdate))


def testEffacerIntrigue(monGN):
    listerRolesPerso(monGN, "Kyle Talus")
    monGN.intrigues["1p5ndWGUb3uCJ1iSSkPpHrDAzwY8iBdK8Lf9CLpP9Diw"].clear()
    del monGN.intrigues["1p5ndWGUb3uCJ1iSSkPpHrDAzwY8iBdK8Lf9CLpP9Diw"]
    print("J'ai effacé l'intrigue Rox et Rouky")
    listerRolesPerso(monGN, "Kyle Talus")

def afficherLesPersos(monGN):
    for intrigue in monGN.intrigues:
        # print("propriétaire intrigue : {0} : {1}".format(intrigue.nom, intrigue.orgaReferent))
        # for clef in intrigue.roles.keys():
        #     print(clef + " a pour nom complet : " + str(intrigue.roles[clef].nom))

        for role in intrigue.roles.values() :
            print("pour le rôle " + role.nom)
            print("Personnage : " + role.perso.nom)
            texteScenes = ""
            for scene in role.scenes:
                texteScenes += scene.titre + "; "
            print("scenes : " + texteScenes)


def afficherDatesScenes(monGN):
    for intrigue in monGN.intrigues:
        for scene in intrigue.scenes:
            print("scène : {0} / date : {1} > {2}".format(scene.titre, scene.date, scene.getFormattedDate()))


def genererCsvOrgaIntrigue(monGN):
    for intrigue in monGN.intrigues:
        print("{0};{1}".format(intrigue.nom, intrigue.orgaReferent))

def listerLesRoles(monGN):
    for intrigue in monGN.intrigues:
        print(f"intrigue : {intrigue.nom} - url : {intrigue.url}")
        for role in intrigue.roles.values():
            print(str(role))
def listerDatesIntrigues(monGN):
    for intrigue in monGN.intrigues.values():
        print("{0} - {1} - {2}".format(intrigue.nom, intrigue.lastChange, intrigue.url))

def listerRolesPerso(monGN, nomPerso):
    for role in monGN.personnages[nomPerso].roles:
        print("Role : {0}".format(role))

main()