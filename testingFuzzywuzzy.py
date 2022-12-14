from fuzzywuzzy import process

import doc2PJ
import modeleGN
from modeleGN import *
import doc2Intrigue
import lecteurGoogle
import sys

folderid = "1toM693dBuKl8OPMDmCkDix0z6xX9syjA"  # le folder des intrigues de Chalacta
folderSqueletteEmeric = "1hpo8HQ8GKjQG63Qm_QlEX7wQ58wZ9-Bw"
folderSqueletteJu = "17ii8P23nkyEk37MqFZKS3K9xohKDg0X7"
folderSqueletteCharles = "1uz_m0PEY8fxNFembqL7om3LMskE4e5Ee"


nomspersos = ["Anko Siwa", "Ashaya Asty", "Aved - 4V-3D", "Axel Brance", "Bynar Siwa", "Dall Joval D'rasnov",
              "Desnash Rhylee", "Dophine Rhue", "Driss Ranner", "Edrik Vance", "Greeta Asty", "Hart Do", "Havok",
              "Hog'Gemod Ippolruna", "Isayjja Kahl", "Jaldine Gerams", "Jay Mozel", "Jerima D'rasnov", "Jish Zyld",
              "Jory Asty", "Kael Sin", "Kalitt", "Kess Horoby", "Kianstev Nacram", "Korrgaarr Gguurd'k", "KR3-NC0",
              "Kyle Talus", "Kyrielle Viszla", "Lars Duskon", "Lexi Ipolruna", "Mano Tori", "Mina Tarkin",
              "Naka Kushir", "Naam Poorf", "Nemko Var", "Nexxar Graam", "NT 346/bredan", "Oni Lux", "Pregda Snorn",
              "Rhebanxx Kar", "Rika Sant", "Rimo Twil", "Saryth D'rasnov", "Seika Poorf", "Sirudan Bonte",
              "Slayke Jontab", "Sol Preeda - Soree", "Tarik Koma", "Teysa Cio", "Thuorn Hermon", "Timagua", "Trevek",
              "Tristan Wrenn", "Tsvan Kessig", "Val Krendel", "Valin​ Hess", "Vauber Brasell", "Wexley Ello",
              "Wor Monba", "Xabria", "Yulsa Nazdij", "Zaar Tamwi", "Zagrinn Vrask", "Zoln Ubri"]
nomsPNJs = ['Loomis Kent (éboueurs)', 'Agent tu BSI Mort à définir', 'Nosfran ?', 'Kelar Veil',
            'Un des joueurs de Sabbacc (nom à trouver)', 'Lady Santhe ??', 'Tranche Mitaines', 'Tranche Mitaines',
            'Jaarush Adan', 'L’inquisiteur', 'Clawool', 'Yerraz', 'Droïdes mercenaires',
            'Quay Tolsite, agent des Pykes', 'FX-4', 'Oskrabkosi', 'Loomis Xent', 'Katlyn Clawwool', 'Tranche mitaines',
            'Rebelle 1',
            'Boh Pragg chef de gare Kel dor','Teezk un esclave rodien issu de la purge du cartel Rodien par Tagge',
            'Nekma', 'Katlyn Clawool', 'Benjey Doroat', 'Droïde syndiqué', 'Seerdo', 'Sid Kashan', 'Nosfran Ratspik',
            'Membres du J.A.N', 'Caleadr Schlon', 'Zuckuss (ou Boush, ou une autre star)', 'B2B', 'Haaris',
            'Le fils de Kalitt', 'Trewek', 'Revos Vannak', 'Inquisiteurice', 'Varima', 'Eliana Zorn', 'Zev Jessk',
            'Katlyn Clawool', 'Mohadarr Bodfre', 'Ex esclave', 'Inquisiteur', 'XXXX Rhylee', 'Rak Stryn  le mandalo',
            'Yerraz le go faster', 'Apprenti de l’Inquisiteur', 'Témoin X', 'XXX Geska (frère de wirt)',
            'Fraterr Millbra', 'Izzik Walo’s', 'Katlyn Clawool', 'Rosson', 'Yorshill', 'Rebelle 3', 'Drashk',
            'Baron Soontir Fel', 'esclave porcher, sbire de Hogg', 'Osrabkosi', '5ème frère',
            'La mère (Suwan) et la soeur (Ilanni) de Lexi', 'Darsha Viel', 'Jarus Adams (star tour)', 'Muic Wula',
            'Rebelle 2', 'Nosfran ?', 'O-MR1', 'Katleen Clawool', 'Varina Leech', 'Kalie Hess (Décédée)',
            'Boba Fett (ou un mandalorien bien badass de l’enfer)', 'OMR-1', 'Lieira Sonn', 'esclave 1',
            'Bossk (ou un trando qui le représente)', 'Soontir Fel', 'FX4', 'Trerlil Irgann',
            'Khaljab Welall, agent de l’Aube Ecarlate', 'Inquisiteur : 5ème frère', 'Shaani', 'Dhar']





def main():
    sys.setrecursionlimit(5000) #mis en place pour prévenir pickle de planter



    # todo charger les relations depuis le tableau des relations
    #trouver comment remplacer les vt par des \n

    monGN = GN(folderIntriguesID=folderid,
               folderPJID=[folderSqueletteJu, folderSqueletteEmeric, folderSqueletteCharles])


    for pnj in nomsPNJs:
        monGN.dictPNJs[pnj] = Personnage(nom=pnj, pj=EST_PNJ_HORS_JEU)

    # si on veut charger un fichier
    monGN = GN.load("archive Chalacta")

    apiDrive, apiDoc = lecteurGoogle.creerLecteursGoogleAPIs()
    doc2Intrigue.extraireIntrigues(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest="-01")
    doc2PJ.extrairePJs(monGN, apiDrive=apiDrive, apiDoc=apiDoc, singletest="-01")
    monGN.forcerImportPersos(nomspersos)
    monGN.rebuildLinks(verbal=False)
    monGN.save("archive Chalacta")
    print("****************************")
    print("****************************")
    print("****************************")
    # listerErreurs(monGN)
    # trierScenes(monGN)
    # listerTrierPersos(monGN)
    # #écrit toutes les scènes qui sont dans le GN, sans ordre particulier
    # dumpAllScenes(monGN)

    ## pour avoir tous les objets du jeu :
    # generecsvobjets(monGN)

    squelettePerso(monGN, "Kyle Talus")
    listerRolesPerso(monGN, "Kyle Talus")
    # listerPNJs(monGN)
    # genererCsvPNJs(monGN)
    # genererCsvObjets(monGN)

    # #lister les correspondaces entre les roles et les noms standards
    # mesroles = tousLesRoles(monGN)
    # fuzzyWuzzyme(mesroles, nomspersos)

    # # print(normaliserNomsPNJs(monGN))
    # #génération d'un premier tableau de noms de PNJs à partir de ce qu'on lit dans les intrigues
    # nomsPNSnormalisés = normaliserNomsPNJs(monGN)
    # print([ nomsPNSnormalisés[k][0] for k in nomsPNSnormalisés])

    # print(getAllRole(GN))

    # afficherLesPersos(monGN)
    # afficherDatesScenes(monGN)
    # genererCsvOrgaIntrigue(monGN)
    # listerLesRoles(monGN)
    # del monGN.intrigues['1gf3VUIophPUIgu6EPmubO0kPiOwAx9-3DacvVEfAgiw']
    # listerDatesIntrigues(monGN)

    ## test de la fonction d'effaçage'
    # testEffacerIntrigue(monGN)

    # print(" l'intrigue la plus ancienne est {0}, c'est {1}, maj : {2}".format(monGN.idOldestUpdate, monGN.intrigues[monGN.idOldestUpdate], monGN.oldestUpdate))

    # test de la focntion de rapprochement des PNJs
    # fuzzyWuzzyme(listerPNJs(monGN), nomsPNJs)

    # #test de la focntion de lecture des PJs
    # dumpPersosLus(monGN)
    # dumpSortedPersos(monGN)
    # genererTableauIntrigues(monGN)


def ajouterPersosSansFiche(monGN, nomspersos):

    monGN.forcerImportPersos(nomspersos)

    print(f"fin de l'ajout des personnages sans fiche. j'ai {len(monGN.dictPJs.values())} personnages en tout")

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

        for role in intrigue.roles.values():
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
    nomPerso = process.extractOne(nomPerso, nomspersos)[0]
    for perso in monGN.dictPJs.values():
        if perso.nom == nomPerso:
            # print(f"{nomPerso} trouvé")
            for role in perso.roles:
                print(role)
            break


def squelettePerso(monGN, nomPerso):
    # mesScenes = dict()
    # nomPerso = process.extractOne(nomPerso, nomspersos)[0]
    # for role in monGN.dictPJs[nomPerso].roles:
    #     for scene in role.scenes:
    #         mesScenes[str(scene.getLongdigitsDate())] = scene
    #
    # for key in sorted([str(x) for x in mesScenes.keys()], reverse=True):
    #     print(
    #         f"date : {mesScenes[key].getFormattedDate()} ({mesScenes[key].date}) : {mesScenes[key].titre} dans {mesScenes[key].intrigue.nom}")
    #     print(f"{mesScenes[key].description}")

    mesScenes = []
    nomPerso = process.extractOne(nomPerso, nomspersos)[0]
    for perso in monGN.dictPJs.values():
        if perso.nom == nomPerso:
            # print(f"{nomPerso} trouvé")
            for role in perso.roles:
                for scene in role.scenes:
                    # print(f"{scene.titre} trouvée")
                    mesScenes.append(scene)
            break

    # print(f"{nomPerso} trouvé")
    mesScenes = Scene.trierScenes(mesScenes)
    for scene in mesScenes:
        print(scene)


def listerPNJs(monGN):
    toReturn = []
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if role.estUnPNJ():
                print(role)
                toReturn.append(role.nom)
    return toReturn


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
    print(f"dernière modification GN : {monGN.oldestUpdate}/{monGN.intrigues[monGN.oldestUpdatedIntrigue]}")
    for intrigue in monGN.intrigues.values():
        for role in intrigue.roles.values():
            if not modeleGN.estUnPNJ(role.pj) and role.pj != EST_REROLL:
                tousLesRoles.append(role.nom)
        # print(f"date dernière MAJ {intrigue.dateModification}")
    return tousLesRoles


def fuzzyWuzzyme(input, choices):
    # input.sort()
    toReturn = []
    input = set(input)
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
    nomsPNJs = list(set(nomsPNJs))
    print("Nom D'origine ;Meilleur choix;Confiance")
    for i in range(len(nomsPNJs)):
        choices = process.extract(nomsPNJs[i], nomsPNJs, limit=2)
        print(f"{choices[0][0]};{choices[1][0]};{choices[1][1]}")

        # le premier choix sera toujours de 100, vu qu'il se sera trouvé lui-même
        # si le second choix est > 90 il y a de fortes chances qu'on ait le même perso
        # sinon on ne prend pas de risques et on garde le meme perso
        if choices[1][1] > 90:
            nomsNormalises[nomsPNJs[i]] = [choices[1][0], choices[1][1]]
        else:
            nomsNormalises[nomsPNJs[i]] = [choices[0][0], choices[0][1]]

    return nomsNormalises

def generecsvobjets(monGn):
    for intrigue in monGn.intrigues.values():
        for objet in intrigue.objets:
            print(f"{intrigue.nom};{intrigue.orgaReferent};{objet.description};{objet.fourniParJoueur};{objet.fourniParJoueur};{objet.rfid};{objet.specialEffect};")


def dumpPersosLus(monGN):
    for pj in monGN.dictPJs.values():
        # if pj.url != "":
            print(pj)

def dumpSortedPersos(monGN):
    tousLesPersos = [x.nom for x in monGN.dictPJs.values()]
    tousLesPersos.sort()
    print(tousLesPersos)
    print(len(tousLesPersos))
    print(len(nomspersos))


def dumpAllScenes(monGN):
    for intrigue in monGN.intrigues.values():
        print(f"{str(intrigue)}")
        print(f" a {len(intrigue.scenes)} scenes")

        mesScenes = dict()
        for scene in intrigue.scenes:
            print(f"titre / longdigit : {scene.titre} / {scene.getLongdigitsDate()}")
            mesScenes[str(scene.getLongdigitsDate())] = scene
        print(f"toutes les scènes : {mesScenes}")

        for key in sorted([str(x) for x in mesScenes.keys()], reverse=True):
            print(mesScenes[key])


def trierScenes(monGN):
    # for intrigue in monGN.intrigues.values():
    #     print(f"{str(intrigue)}")
    #     print(f" a {len(intrigue.scenes)} scenes")
    #     scenesTriees = sorted(intrigue.scenes, key=lambda scene: scene.getLongdigitsDate(), reverse=True)
    #     for s in scenesTriees:
    #         print(s)

    for intrigue in monGN.intrigues.values():
        print()
        print()
        print(f"intrigue {intrigue.nom} : ")
        triee = intrigue.getScenesTriees()
        for scene in triee:
            print(scene)



def listerTrierPersos(monGN):
    touspj = []
    for pj in monGN.dictPJs.values():
        touspj.append(pj.nom)
    touspj.sort()
    for pj in touspj:
        print(pj)

def listerErreurs(monGN):
    for intrigue in monGN.intrigues.values():
        if len(intrigue.errorLog) > 1:
            print("")
            print("")
            print(f"pour {intrigue.nom} : ")
            print(intrigue.errorLog)
            suggererTableauPersos(intrigue)


def genererTableauIntrigues(monGN):
    print("Intrigue; Orga Référent")
    toPrint = monGN.intrigues.values()
    toPrint = sorted(toPrint, key=lambda x: x.nom)
    for intrigue in toPrint:
        print(f"{intrigue.nom};{intrigue.orgaReferent.strip()};")


def rogue(): #utilisé pour nettoyer les tableaux de persos des grosses intrigues
    iwant = ["Nexxar", "Mina Tarkin", "Edrik", "Nexxar", "Jak", "Trevek",
             "Dio Muftak", "Osrabkosi", "Rebbanx", "Kar", "Edrik", "Wexley",
             "Veert", "Desnash", "Vert", "Zev", "Ssor","FX - 4", "Kianstef", "Dhar",
             "Desnash", "Dhar", "Jay", "Mosel", "FX - 4", "Timagua", "Veert", "Edrik",
             "Wexley", "Tsvan", "Ssor", "Kael", "Syn", "Seika", "Jerima", "Thuorn"]
    iwant = [x.strip() for x in iwant]
    iwant = set(iwant)
    for nom in iwant:
        # print(str(nom))
        score = process.extractOne(str(nom), nomspersos)
        print(f"{nom} > {process.extractOne(nom, nomspersos)}")

def suggererTableauPersos(intrigue):
    persosDansIntrigue = [x.perso for x in intrigue.roles.values()]
    print("Tableau suggéré")
    iwant = []
    for scene in intrigue.scenes:
        if scene.rawRoles is not None:
            iwant += scene.rawRoles
    iwant = [x.strip() for x in iwant]
    iwant = set(iwant)
    for nom in iwant:
        # print(str(nom))
        score = process.extractOne(str(nom), nomspersos)
        toPrint=""
        if score[0] in persosDansIntrigue:
            toPrint += "[OK]"
        else:
            toPrint += "[XX]"
        toPrint += f"{nom} > {process.extractOne(nom, nomspersos)}"
        print(toPrint)


main()
