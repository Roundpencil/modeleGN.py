import datetime
import pickle
import datetime
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
                 sexe="i", pj=EST_PJ):
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

    def addrole(self, r):
        self.roles.add(r)

    def __str__(self):
        return "nom perso : " + self.nom


# rôle
class Role:

    def __init__(self, intrigue, perso=None, nom="rôle sans nom", description="", pipi=0, pipr=0, sexe="i", pj=EST_PJ,
                 typeIntrigue="", niveauImplication="", perimetreIntervention = ""):
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
        if self.perso == None:
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
                 questions_ouvertes="", notes="", resolution="", orgaReferent="", timeline="", lastChange=0,
                 scenesEnJeu=""):
        self.nom = nom
        self.roles = {}  # nom, rôle
        self.scenes = set()
        self.description = description
        self.pitch = pitch
        self.questions_ouvertes = questions_ouvertes
        self.notes = notes
        self.resolution = resolution
        self.orgaReferent = orgaReferent
        self.dateModification = datetime.datetime.now()
        self.url = url
        self.timeline = timeline
        self.lastChange = lastChange
        self.scenesEnJeu = scenesEnJeu
        self.objets = set()

    def __str__(self):
        return self.nom

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
            if role.perso == personnage:
                # ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au sein d'une mêm intrigue

                if verbal: # et si on a demandé à ce que la fonction raconte sa vie, on détaille
                    print(f"Erreur Association role > PJ : "
                          f"{roleAAssocier.nom} > {personnage.nom}, "
                          f"déjà associé au rôle {role.nom} dans {self.nom}")
                return -1
        roleAAssocier.perso = personnage
        #au passage on update le niveau de perso (surtout utile pour les PNJs), en prenant toujours le max
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
        #retirer l'intrigue du GN > à faire au niveau de l'appel
        #casser toutes les relations role <> personnages
        for role in self.roles.values():
            # print(f"Role à dissocier  : {role.nom} de {role.perso}")
            if role.perso is not None:
                role.perso.roles.remove(role)
                del role

        #se séparer de tous les objets
        for objet in self.objets:
            objet.inIntrigues.remove(self)

        #effacer toutes les scènes de l'intrigue
        for scene in self.scenes:
            del scene
        # print(f"intrigue effacée {self.nom}")



# relations
class Relation:
    def __init__(self, perso1, perso2, description="Relation à définir"):
        self.perso1 = perso1
        self.perso2 = perso2
        self.description = description

    def partenaire(self, perso):
        if perso == self.perso1:
            return self.perso2

        if perso == self.perso2:
            return self.perso1

        raise Exception("Personnage inconnu dans cette relation")


# Scènes
class Scene:
    def __init__(self, intrigue, titre, date="0", pitch="Pas de description simple", description="Description complète",
                 actif=True, resume="", niveau=3):
        self.intrigue = intrigue
        self.date = date
        self.titre = titre
        self.resume = resume
        self.pitch = pitch
        self.description = description
        self.actif = actif
        self.roles = set()
        self.niveau = niveau  # 1 : dans la chronologie globale,
        # 2, dans tous les personnages de l'intrigue (pour info, donc pour les autres)
        # 3 : personnages impactés uniquement
        # faut-il dire que role et personnages héritent l'un de l'autre? Ou bien d'un objet "protagoniste"?

    def get_date(self):
        return self.date

    def getFormattedDate(self):
        print("date/type > {0}/{1}".format(self.date, type(self.date)))
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
            print("la date <{0}> n'est pas un nombre".format(self.date))
            return self.date

    def addRole(self, role):
        self.roles.add(role)

    def __str__(self):
        return ("Titre Scène : " + self.titre)


# objet pour tout sauvegarder


class GN:
    def __init__(self, folderId):
        self.personnages = {} #nom, personnage
        self.listePnjs = {} #nom, personnage
        self.intrigues = dict()  # clef : id google
        self.oldestUpdate = None
        self.idOldestUpdate = ""
        self.folderID = folderId

    # permet de mettre à jour la date d'intrigue la plus ancienne
    # utile pour la serialisation : google renvoie les fichiers dans l'ordre de dernière modif
    # Tant que les modifs dans google sont postérieures à la date de dernière modif > les prendre en compte
    # Après > arréter
    def updateOldestUpdate(self):
        pairesDatesId = dict()
        for intrigue in self.intrigues.values():
            pairesDatesId[intrigue.lastChange] = intrigue.url
        self.oldestUpdate = min(pairesDatesId.keys())
        self.idOldestUpdate = pairesDatesId[self.oldestUpdate]

    def save(self, filename):
        filehandler = open(filename, "wb")
        pickle.dump(self, filehandler)

    def getNomsPersos(self):
        return self.personnages.keys()

    def getNomsPNJs(self):
        return self.listePnjs.keys()

    def associerPNJsARoles(self, seuilAlerte=90, verbal=True):
        nomsPnjs = self.getNomsPNJs()
        for intrigue in self.intrigues.values():
            for role in intrigue.roles.values():
                if estUnPNJ(role.pj):
                    score = process.extractOne(role.nom, nomsPnjs)
                    # role.perso = self.listePnjs[score[0]]
                    intrigue.associerRoleAPerso(roleAAssocier=role, personnage= self.listePnjs[score[0]])
                    if verbal and score[1] < seuilAlerte:
                        print(f"Warning association ({score[1]}) - nom rôle : {role.nom} > PNJ : {score[0]} dans {intrigue.nom}")

    def associerPJsARoles(self, seuilAlerte=70, verbal=True):
        nomsPjs = self.getNomsPersos()
        for intrigue in self.intrigues.values():
            for role in intrigue.roles.values():
                if estUnPJ(role.pj):
                    score = process.extractOne(role.nom, nomsPjs)
                    # print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
                    check = intrigue.associerRoleAPerso(roleAAssocier=role, personnage=self.personnages[score[0]], verbal=verbal)
                    if verbal:
                        if score[1] < seuilAlerte:
                            print(f"Warning association ({score[1]}) - nom rôle : {role.nom} > PJ : {score[0]} dans {intrigue.nom}")

    @staticmethod
    def load(filename):
        monfichier = open(filename, 'rb')
        return pickle.load(monfichier)

    #apres une importation recrée
    # tous les liens entre les PJs,
    # les PNJs
    # et les fonctions d'accélération de ré-importations

    def rebuildLinks(self, verbal=True):
        self.clearAllAssociations()
        self.updateOldestUpdate()
        self.associerPNJsARoles(verbal)
        self.associerPJsARoles(verbal)

    def clearAllAssociations(self):
        for pj in self.personnages.values():
            pj.roles.clear()
        for pnj in self.listePnjs.values():
            pnj.roles.clear()

        #todo : vider les roles associés aux PJs /PNJs
        #   vider les personnages associés aux rôles
        for intrigue in self.intrigues.values():
            for role in intrigue.roles.values():
                role.perso = None

        pass


# objets

class Objet:
    def __init__(self, description="", fourniPar="Inconnu", emplacementDebut="", specialEffect=""):
        self.description = description
        self.fourniParJoueur = fourniPar
        self.emplacementDebut = emplacementDebut
        self.rfid = len(specialEffect) > 0
        self.specialEffect = specialEffect
        self.inIntrigues = set()
