import datetime
import pickle
import datetime
import random

from fuzzywuzzy import process

EST_PJ = 6
EST_REROLL = 5
EST_PNJ_INFILTRE = 4
EST_PNJ_PERMANENT = 3
EST_PNJ_TEMPORAIRE = 2
EST_PNJ_HORS_JEU = 1


def estUnPNJ(niveauPJ):
    return niveauPJ == EST_PNJ_HORS_JEU or niveauPJ == EST_PNJ_TEMPORAIRE or niveauPJ == EST_PNJ_INFILTRE or niveauPJ == EST_PNJ_PERMANENT


def estUnPJ(niveauPJ):
    return niveauPJ == EST_PJ


def stringTypePJ(typePJ):
    if typePJ == EST_PJ:
        return "PJ"
    if typePJ == EST_REROLL:
        return "Reroll"
    if typePJ == EST_PNJ_INFILTRE:
        return "PNJ Infiltré"
    if typePJ == EST_PNJ_PERMANENT:
        return "PNJ Permanent"
    if typePJ == EST_PNJ_TEMPORAIRE:
        return "PNJ Temporaire"
    if typePJ == EST_PNJ_HORS_JEU:
        return "PNJ Hors Jeu"
    return f"Type de PJ inconnu ({typePJ})"


# personnage

class Personnage:
    def __init__(self, nom="personnage sans nom", concept="", driver="", description="", questions_ouvertes="",
                 sexe="i", pj=EST_PJ, orgaReferent="", pitchJoueur="", indicationsCostume="", textesAnnexes="",
                 url="", lastChange=datetime.datetime(year=2000, month=1, day=1), forced=False):
        self.nom = nom
        self.concept = concept
        self.driver = driver
        self.questions_ouvertes = questions_ouvertes
        self.sexe = sexe  # i = indéterminé / h = homme / f = femme
        self.pj = pj
        self.actif = True
        self.roles = set()  # liste de rôles qui sont eux meme affectés à des intrigues
        self.relations = set()  # nom relation, relation
        self.images = set()
        self.description = description
        self.orgaReferent = orgaReferent
        self.joueurs = dict()
        self.pitchJoueur = pitchJoueur
        self.indicationsCostume = indicationsCostume
        self.factions = []
        # trouver comment interpréter les textes en dessous des tableaux
        # : des scènes ?
        self.textesAnnexes = textesAnnexes
        self.url = url
        self.lastProcessing = lastChange
        self.forced = forced

    def clear(self):
        for role in self.roles:
            role.perso = None
        self.roles.clear()

    def addrole(self, r):
        self.roles.add(r)

    def __str__(self):
        return "nom perso : " + self.nom

    def __str__(self):
        toReturn = ""
        toReturn += f"nom = {self.nom} \n"
        toReturn += f"concept = {self.concept} \n"
        toReturn += f"questions_ouvertes = {self.questions_ouvertes} \n"
        toReturn += f"sexe = {self.sexe} \n"
        toReturn += f"pj = {stringTypePJ(self.pj)} \n"
        toReturn += f"actif = {self.actif} \n"
        toReturn += f"roles = {str(self.roles)} \n"
        toReturn += f"relations = {str(self.relations)} \n"
        toReturn += f"images = {self.images} \n"
        toReturn += f"description = {self.description} \n"
        toReturn += f"orgaReferent = {self.orgaReferent} \n"
        toReturn += f"joueurs = {self.joueurs.values()} \n"
        toReturn += f"pitchJoueur = {self.pitchJoueur} \n"
        toReturn += f"indicationsCostume = {self.indicationsCostume} \n"
        toReturn += f"factions = {self.factions} \n"
        toReturn += f"textesAnnexes = {self.textesAnnexes} \n"
        return toReturn


# rôle
class Role:

    def __init__(self, intrigue, perso=None, nom="rôle sans nom", description="", pipi=0, pipr=0, sexe="i", pj=EST_PJ,
                 typeIntrigue="", niveauImplication="", perimetreIntervention=""):
        self.intrigue = intrigue
        self.perso = perso
        self.nom = nom
        self.description = description
        self.pipr = pipr
        self.pipi = pipi
        self.pj = pj
        self.sexe = sexe
        self.typeIntrigue = typeIntrigue
        self.niveauImplication = niveauImplication
        self.scenes = set()
        self.perimetreIntervention = perimetreIntervention

    def __str__(self):
        toReturn = ""
        toReturn += "intrigue : " + self.intrigue.nom + "\n"
        toReturn += "nom dans l'intrigue : " + self.nom + "\n"
        if self.perso is None:
            toReturn += "perso : aucun" + "\n"
        else:
            toReturn += "perso : " + self.perso.nom + "\n"
        toReturn += "description : " + self.description + "\n"
        # toReturn += "pipr : " + str(self.pipr) + "\n"
        # toReturn += "pipi : " + str(self.pipi) + "\n"
        toReturn += "pj : " + stringTypePJ(self.pj) + "\n"
        # toReturn += "sexe : " + self.sexe + "\n"
        toReturn += "typeIntrigue : " + self.typeIntrigue + "\n"
        toReturn += "niveauImplication : " + self.niveauImplication + "\n"
        return toReturn

    def ajouterAScene(self, sceneAAjouter):
        self.scenes.add(sceneAAjouter)
        sceneAAjouter.roles.add(self)

    def estUnPNJ(self):
        return estUnPNJ(self.pj)


# intrigue
class Intrigue:

    def __init__(self, url, nom="intrigue sans nom", description="Description à écrire", pitch="pitch à écrire",
                 questions_ouvertes="", notes="", resolution="", orgaReferent="", timeline="", lastProcessing=0,
                 scenesEnJeu="", lastFileEdit = 0):
        self.nom = nom
        self.roles = {}  # nom, rôle
        self.scenes = set()
        self.description = description
        self.pitch = pitch
        self.questions_ouvertes = questions_ouvertes
        self.notes = notes
        self.resolution = resolution
        self.orgaReferent = orgaReferent
        # self.dateModification = datetime.datetime.now() #seul usage dans le projet d'après l'inspecteur, je vire
        self.url = url
        self.timeline = timeline
        self.lastProcessing = lastProcessing
        self.lastFileEdit = lastFileEdit
        self.scenesEnJeu = scenesEnJeu
        self.objets = set()
        self.errorLog = ""

    def __str__(self):
        return self.nom

    def getErrorLog(self):
        return self.errorLog

    def addToErrorLog(self, text):
        self.errorLog += text + "\n"
        # une erreur :
        # un endroit ou c'est détecté : tableau des intrigues, rôles, personnages


    def clearErrorLog(self):
        self.errorLog = ""


    # vérifier que le personnge que l'on souhaite associer à un rôle n'est pas déjà associé à un autre rôle
    # dans la même intrigue
    # Si c'est le cas :
    #   renvoyer -1 : un même personnage ne peut être associé qu'à un seul rôle dans une intrigue
    # Sinon :
    #   réaliser l'association entre le personnage et le rôle
    #   ajouter le rôle à la liste des rôles du personnage
    #   renvoyer 0
    def associerRoleAPerso(self, roleAAssocier, personnage, verbal=True):
        # pour chaque rôle qui fait partie des rôles de l'intrigue
        for role in self.roles.values():
            # si le personnage que l'on souhaite associer au rôle est déjà associé à un rôle dans l'intrigue
            if role.perso is personnage:
                # ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au sein d'une mêm intrigue

                texteErreur = f"Erreur Association role > PJ : " \
                              f"{roleAAssocier.nom} > {personnage.nom}, " \
                              f"déjà associé au rôle {role.nom} dans {self.nom}"
                self.addToErrorLog(texteErreur)

                if verbal:  # et si on a demandé à ce que la fonction raconte sa vie, on détaille
                    print(texteErreur)
                return -1
        roleAAssocier.perso = personnage
        # au passage on update le niveau de perso (surtout utile pour les PNJs), en prenant toujours le max
        personnage.pj = max(personnage.pj, roleAAssocier.pj)
        personnage.roles.add(roleAAssocier)
        return 0

    def getNomsRoles(self):
        return self.roles.keys()

    def getFullUrl(self):
        return "https://docs.google.com/document/d/" + self.url

    def addScene(self, nomScene):
        sceneAajouter = Scene(self, nomScene)
        self.scenes.add(sceneAajouter)
        return sceneAajouter

    def clear(self):
        # retirer l'intrigue du GN > à faire au niveau de l'appel
        # casser toutes les relations role <> personnages
        for role in self.roles.values():
            # print(f"Role à dissocier  : {role.nom} de {role.perso}")
            if role.perso is not None:
                role.perso.roles.remove(role)
                del role
        # self.roles.clear()

        # se séparer de tous les objets
        for objet in self.objets:
            objet.inIntrigues.remove(self)
        # self.objets.clear()

        # effacer toutes les scènes de l'intrigue
        for scene in self.scenes:
            del scene
        # self.scenes.clear()
        # print(f"intrigue effacée {self.nom}")
        self.errorLog = ''

    def getScenesTriees(self):
        return Scene.trierScenes(self.scenes)


# relations
class Relation:
    def __init__(self, perso1, perso2, description="Relation à définir"):
        self.perso1 = perso1
        self.perso2 = perso2
        self.description = description

    def partenaire(self, perso):
        if perso is self.perso1:
            return self.perso2

        if perso is self.perso2:
            return self.perso1

        raise Exception("Personnage inconnu dans cette relation")


# Scènes
class Scene:
    def __init__(self, intrigue, titre, date="0", pitch="Pas de description simple", description="Description complète",
                 actif=True, resume="", niveau=3):
        self.intrigue = intrigue
        self.date = date  # stoquée sous la forme d'un nombre négatif représentant le nombre de jours entre le GN et
        # l'évènement
        self.titre = titre
        self.pitch = pitch
        self.description = description
        self.actif = actif
        self.roles = set()
        self.niveau = niveau  # 1 : dans la chronologie globale,
        # 2, dans tous les personnages de l'intrigue (pour info, donc pour les autres)
        # 3 : personnages impactés uniquement
        # faut-il dire que role et personnages héritent l'un de l'autre? Ou bien d'un objet "protagoniste"?
        self.rawRoles = None

    def get_date(self):
        return self.date

    def getLongdigitsDate(self, size=30):
        # print(f"date : {self.date}")
        if type(self.date) == float or type(self.date) == int or str(self.date[1:]).isnumeric():
            # print(f"date est numérique")

            refdate = str(int(self.date))[1:] + str(
                random.randint(1000, 9999))  # permet d'éviter les évènements qui ont la meme date
            return "0" * (size - len(str(refdate))) + str(refdate)
        else:
            # print(f"date n'est pas numérique")
            return str(self.date) + "0" * (size - len(str(self.date)))

    def getFormattedDate(self):
        # print("date/type > {0}/{1}".format(self.date, type(self.date)))
        if type(self.date) == float or type(self.date) == int or str(self.date[1:]).isnumeric():
            if type(self.date) == str:
                maDate = float(self.date[1:])
            else:
                maDate = -1 * self.date
            dateTexte = 'Il y a '
            nbAnnees = maDate // 365
            nbMois = (maDate - nbAnnees * 365) // 30.5
            nbJours = maDate - nbAnnees * 365 - nbMois * 30.5

            if nbAnnees > 1:
                dateTexte += str(nbAnnees)[:-2] + " ans, "
            elif nbAnnees == 1:
                dateTexte += "1 an, "

            if nbMois > 0:
                dateTexte += str(nbMois)[:-2] + " mois, "

            if nbJours > 1:
                dateTexte += str(nbJours)[:-2] + " jours, "
            elif nbJours > 0:
                dateTexte += "1 jour, "
            return dateTexte[0:-2]  # car meme dans le cadre de jours on a rajouté deux cars ;)

        else:
            # print("la date <{0}> n'est pas un nombre".format(self.date))
            return self.date

    def addRole(self, role):
        self.roles.add(role)

    def __str__(self):
        toReturn = ""

        toReturn += f"titre scène : {self.titre} \n"
        toReturn += f"date  : {self.getFormattedDate()} \n" # - {self.getLongdigitsDate()}\n"
        strRolesPersos = 'Roles (Perso) : '
        for role in self.roles:
            if role.perso is None:
                strRolesPersos += f"{role.nom} (pas de perso affecté) / "
            else:
                strRolesPersos += f" {role.nom} ({role.perso.nom}) / "
        toReturn += f"roles  : {strRolesPersos} \n"
        toReturn += f"intrigue : {self.intrigue.nom} \n"
        toReturn += f"dernière édition de l'intrigue : {self.intrigue.lastFileEdit} \n"
        toReturn += f"url intrigue : {self.intrigue.getFullUrl()} \n"
        # toReturn += f"pitch  : {self.pitch} \n"
        # toReturn += f"description : \n {self.description} \n"
        toReturn += f"\n {self.description} \n"
        #todo : ajouter une date de dernier impact pour les pjs au début des intrigues concernées
        # (et des scènes, par ricochet?)

        # toReturn += f"actif  : {self.actif} \n"
        return toReturn

    @staticmethod
    def trierScenes(scenesATrier):
        return sorted(scenesATrier, key=lambda scene: scene.getLongdigitsDate(), reverse=True)

# objet pour tout sauvegarder


class GN:
    def __init__(self, folderIntriguesID, folderPJID):
        self.dictPJs = {}  # idgoogle, personnage
        self.dictPNJs = {}  # nom, personnage
        self.intrigues = dict()  # clef : id google
        self.oldestUpdateIntrigue = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatePJ = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatedIntrigue = ""  # contient l'id de la dernière intrigue updatée dans le GN
        self.oldestUpdatedPJ = ""  # contient l'id du dernier PJ updaté dans le GN
        if isinstance(folderIntriguesID, list):
            self.folderIntriguesID = folderIntriguesID
        else:
            self.folderIntriguesID = [folderIntriguesID]

        if isinstance(folderPJID, list):
            self.folderPJID = folderPJID
        else:
            self.folderPJID = [folderPJID]
        print(f"PJID = {self.folderPJID}")

    # permet de mettre à jour la date d'intrigue la plus ancienne
    # utile pour la serialisation : google renvoie les fichiers dans l'ordre de dernière modif
    # Tant que les modifs dans google sont postérieures à la date de dernière modif > les prendre en compte
    # Après > arréter
    def updateOldestUpdate(self):
        pairesDatesIdIntrigues = dict()
        for intrigue in self.intrigues.values():
            pairesDatesIdIntrigues[intrigue.lastProcessing] = intrigue.url
        if len(pairesDatesIdIntrigues) > 0:
            self.oldestUpdateIntrigue = min(pairesDatesIdIntrigues.keys())
            self.oldestUpdatedIntrigue = pairesDatesIdIntrigues[self.oldestUpdateIntrigue]

        pairesDatesIdPJ = dict()
        for pj in self.dictPJs.values():
            # print(pj.nom)
            pairesDatesIdPJ[pj.lastProcessing] = pj.url
        # print(pairesDatesIdPJ)
        if len(pairesDatesIdPJ) > 0:
            self.oldestUpdatePJ = min(pairesDatesIdPJ.keys())
            # print(f"oldestdate pj : {self.oldestUpdatePJ} ")
            self.oldestUpdatedPJ = pairesDatesIdPJ[self.oldestUpdatePJ]

    def save(self, filename):
        filehandler = open(filename, "wb")
        pickle.dump(self, filehandler)
        filehandler.close()

    def getNomsPersos(self):
        # return self.dictPJs.keys()
        return [x.nom for x in self.dictPJs.values()]

    def getNomsPNJs(self):
        return self.dictPNJs.keys()

    def associerPNJsARoles(self, seuilAlerte=90, verbal=True):
        nomsPnjs = self.getNomsPNJs()
        for intrigue in self.intrigues.values():
            for role in intrigue.roles.values():
                if estUnPNJ(role.pj):
                    score = process.extractOne(role.nom, nomsPnjs)
                    # role.perso = self.listePnjs[score[0]]
                    # print(
                    #     f"je m'appête à associer PNJ {role.nom}, identifié comme {score} à {self.dictPNJs[score[0]]} (taille du dictionnaire PNJ = {len(self.dictPNJs)}")
                    intrigue.associerRoleAPerso(roleAAssocier=role, personnage=self.dictPNJs[score[0]])
                    if score[1] < seuilAlerte:
                        texteErreur = f"Warning association ({score[1]}) " \
                                      f"- nom rôle : {role.nom} > PNJ : {score[0]} dans {intrigue.nom}"
                        intrigue.addToErrorLog(texteErreur)
                        if verbal:
                            print(texteErreur)

    def associerPJsARoles(self, seuilAlerte=70, verbal=True):
        print("Début de l'association automatique des rôles aux persos")
        nomsPjs = self.getNomsPersos()
        dictNomsPJ = dict()
        for pj in self.dictPJs.values():  # on crée un dictionnaire temporaire nom > pj pour faire les associations
            dictNomsPJ[pj.nom] = pj

        for intrigue in self.intrigues.values():
            for role in intrigue.roles.values():
                if estUnPJ(role.pj):
                    score = process.extractOne(role.nom, nomsPjs)
                    # print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
                    check = intrigue.associerRoleAPerso(roleAAssocier=role, personnage=dictNomsPJ[score[0]],
                                                        verbal=verbal)

                    if score[1] < seuilAlerte:
                        texteErreur = f"Warning association ({score[1]}) - nom rôle : " \
                                      f"{role.nom} > PJ : {score[0]} dans {intrigue.nom}"
                        intrigue.addToErrorLog(texteErreur)
                        if verbal:
                            # print(f"je paaaaaarle {score[1]}")
                            print(texteErreur)

        print("Fin de l'association automatique des rôles aux persos")

    @staticmethod
    def load(filename):
        monfichier = open(filename, 'rb')
        return pickle.load(monfichier)
        monfichier.close()

    # apres une importation recrée
    # tous les liens entre les PJs,
    # les PNJs
    # et les fonctions d'accélération de ré-importations

    def rebuildLinks(self, verbal=True):
        self.clearAllAssociations()
        self.updateOldestUpdate()
        self.associerPNJsARoles(verbal)
        self.associerPJsARoles(verbal)

    # utilisée pour préparer lassociation roles/persos
    # l'idée est qu'avec la sauvegarde les associations restent, tandis que si les pj/pnj ont bougé ca peut tout changer
    def clearAllAssociations(self):
        for pj in self.dictPJs.values():
            pj.roles.clear()
        for pnj in self.dictPNJs.values():
            pnj.roles.clear()

        for intrigue in self.intrigues.values():
            # intrigue.clearErrorLog()
            # todo ne nettoyer que les erreurs générées par l'association...
            #  quand on aura un objet erreur :)
            for role in intrigue.roles.values():
                role.perso = None

    def forcerImportPersos(self, nomsPersos, suffixe="_imported"):
        print("début de l'ajout des personnages sans fiche")
        nomsLus = [x.nom for x in self.dictPJs.values()]
        # pour chaque perso de ma liste :
        # SI son nom est dans les persos > ne rien faire
        # SINON, lui créer une coquille vide
        persosSansCorrespondance = []
        for perso in nomsPersos:
            if perso in nomsLus:
                print(f"le personnage {perso} a une correspondance dans les persos déjà présents")
            else:
                # persosSansCorrespondance.append(
                #     [perso,
                #      process.extractOne(perso, nomsLus)[0],
                #      process.extractOne(perso, nomsLus)[1]])
                scoreproche = process.extractOne(perso, nomsLus)
                if scoreproche is not None and scoreproche[1] >= 75:
                    print(f"{perso} correspond à {scoreproche[0]} à {scoreproche[1]}%")
                    # donc on ne fait rien
                else:
                    print(f"{perso} a été créé (coquille vide)")
                    self.dictPJs[perso + suffixe] = Personnage(nom=perso,
                                                     pj=EST_PJ, forced=True)  # on met son nom en clef pour se souvenir qu'il a été généré


# objets

class Objet:
    def __init__(self, description="", fourniPar="Inconnu", emplacementDebut="", specialEffect=""):
        self.description = description
        self.fourniParJoueur = fourniPar
        self.emplacementDebut = emplacementDebut
        self.rfid = len(specialEffect) > 0
        self.specialEffect = specialEffect
        self.inIntrigues = set()
