from fuzzywuzzy import process

import modeleGN
from modeleGN import *
import doc2Intrigue

def main():
    nomspersos = ["Anko Siwa", "Ashaya Asty", "Aved - 4V-3D", "Axel Brance", "Bynar Siwa", "Dal Joval D'rasnov", "Desnash Rhylee", "Dophine Rhue", "Driss Ranner", "Edrik Vance", "Greeta Asty", "Hart Do", "Havok", "Hog'Gemod Ippolruna", "Isayjja Kahl", "Jaldine Gerams", "Jay Mozel", "Jerima D'rasnov", "Jish Zyld", "Jory Asty", "Kael Sin", "Kalitt", "Kess Horoby", "Kianstev Nacram", "Korrgaarr Gguurd'k", "KR3-NC0", "Kyle Talus", "Kyrielle Viszla", "Lars Duskon", "Lexi Ipolruna", "Mano Tori", "Mina Tarkin", "Naka Kushir", "Naam Poorf", "Nemko Var", "Nexxar Graam", "NT 346/bredan", "Oni Lux", "Pregda Snorn", "Rhebanxx Kar", "Rika Sant", "Rimo Twil", "Saryth D'rasnov", "Seika Poorf", "Sirudan Bonte", "Slayke Jontab", "Sol Preeda - Soree", "Tarik Koma", "Teysa Cio", "Thuorn Hermon", "Timagua", "Trevek", "Tristan Wrenn", "Tsvan Kessig", "Val Krendel", "Valin​ Hess", "Vauber Brasell", "Wexley Ello", "Wor Monba", "Xabria", "Yulsa Nazdij", "Zaar Tamwi", "Zagrinn Vrask", "Zoln Ubri"]
    monGN = GN()

    for perso in nomspersos:
        monGN.personnages[perso] = Personnage(nom=perso, pj=True)

    monGN = GN.load("archive Chalacta")
    # listerRolesPerso(monGN, "Kyle Talus")
    doc2Intrigue.extraireIntrigues(monGN, singletest="-01")
    # listerRolesPerso(monGN, "Kyle Talus")
    # doc2Intrigue.extraireIntrigues(monGN)
    monGN.updateOldestUpdate()
    monGN.save("archive Chalacta")
    print("****************************")
    print("****************************")
    print("****************************")
    # listerPNJs(monGN)
    # genererCsvPNJs(monGN)
    # genererCsvObjets(monGN)

    # #lister les correspondaces entre les roles et les noms standards
    # mesroles = tousLesRoles(monGN)
    # fuzzyWuzzyme(mesroles, nomspersos)

    print(normaliserNomsPNJs(monGN))

    # print(getAllRole(GN))
#todo : conserver une archive des warning associations roles - persos et scenes-roles, ou au moins des indices de confiance
#todo : comprendre pouruqoi PNJ vides (problème de détection de tailles de car?)
#todo : trouver comment normaliser le nom des PNJs
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

def listerPNJs(monGN):
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if role.estUnPNJ():
                print(role)

def genererCsvPNJs(monGN):
    print("nomRole;description;typePJ;niveau implication;details intervention;intrigue")
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if role.estUnPNJ():
                nompnj = role.nom.replace('\n', chr(10))
                description = role.description.replace('\n', "***")
                niveauImplication = role.niveauImplication.replace('\n', chr(10))
                perimetreIntervention = role.perimetreIntervention.replace('\n', chr(10))
                print(f"{nompnj};"
                      f"{description};"
                      f"{stringTypePJ(role.pj)};"
                      f"{niveauImplication};"
                      f"{perimetreIntervention};"
                      f"{intrigue.nom}")

def genererCsvObjets(monGN):
    print("description;Avec FX?;FX;Débute Où?;fourni par Qui?;utilisé où?")
    for intrigue in monGN.intrigues.values():
        for objet in intrigue.objets:
                description = objet.description.replace('\n', "***")
                avecfx = objet.rfid
                fx = objet.specialEffect.replace('\n', "***")
                debuteou = objet.emplacementDebut.replace('\n', "***")
                fournipar = objet.fourniParJoueur.replace('\n', "***")
                utiliseou = [x.nom for x in objet.inIntrigues]
                print(f"{description};"
                      f"{avecfx};"
                      f"{fx};"
                      f"{debuteou};"
                      f"{fournipar};"
                      f"{utiliseou}")

def tousLesRoles(monGN):
    tousLesRoles = []
    print(f"dernière modification GN : {monGN.oldestUpdate}/{monGN.intrigues[monGN.idOldestUpdate]}")
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if not modeleGN.estUnPNJ(role.pj) and role.pj != EST_REROLL:
                tousLesRoles.append(role.nom)
        # print(f"date dernière MAJ {intrigue.dateModification}")
    return tousLesRoles

def fuzzyWuzzyme(input, choices):
    # input.sort()
    toReturn = []
    input=set(input)
    for element in input:
        # scores = process.extract(element, choices, limit=5)
        scores = process.extractOne(element, choices)
        toReturn.append([element, scores[0], scores[1]])
    toReturn.sort(key=lambda x: x[2])

    for element in toReturn:
        print(f"fuzzy : {element}")

def normaliserNomsPNJs(monGN):
    nomsPNJs = []
    nomsNormalises = dict()
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if role.estUnPNJ():
                nomsPNJs.append(role.nom)
    nomsPNJs= list(set(nomsPNJs))
    print("Nom D'origine ;Meilleur choix;Confiance")
    for i in range(len(nomsPNJs)):
        choices = process.extract(nomsPNJs[i], nomsPNJs, limit=2)
        print(f"{choices[0][0]};{choices[1][0]};{choices[1][1]}")
        #le premier choix sera toujours de 100, vu qu'il se sera trouvé lui-même
        # si le second choix est >= 90 il y a de fortes chances qu'on ait le même perso
        if choices[1][1] >= 90:
            nomsNormalises[nomsPNJs[i]] = [choices[1][0], choices[1][1]]
        else:
            nomsNormalises[nomsPNJs[i]] = [choices[0][0], choices[0][1]]


    return nomsNormalises


main()