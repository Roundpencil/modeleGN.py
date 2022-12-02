import datetime
import pickle
import datetime

# personnage

class Personnage:

    def __init__(self, nom="personnage sans nom", concept="", driver="", description="", questions_ouvertes="",
                 sexe="i", pj=True):
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

    def __init__(self, intrigue, perso=None, nom="rôle sans nom", description="", pipi=0, pipr=0, sexe="i", pj=True, typeIntrigue="", niveauImplication = "",
                 enJeu=0):
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
        self.enJeu = enJeu #pour les PNJs uniquement : 0 : non, 1 : oui ponctuellement, 2 : oui sur le long terme

    def __str__(self):
        toReturn = ""
        toReturn += "intrigue : " + self.intrigue.nom + "\n"
        toReturn += "nom dans l'intrigue : " + self.nom + "\n"
        if self.perso == None :
            toReturn += "perso : aucun" + "\n"
        else:
            toReturn += "perso : " + self.perso.nom + "\n"
        toReturn += "description : " + self.description + "\n"
        # toReturn += "pipr : " + str(self.pipr) + "\n"
        # toReturn += "pipi : " + str(self.pipi) + "\n"
        toReturn += "pj : " + str(self.pj) + "\n"
        # toReturn += "sexe : " + self.sexe + "\n"
        toReturn += "typeIntrigue : " + self.typeIntrigue + "\n"
        toReturn += "niveauImplication : " + self.niveauImplication + "\n"
        toReturn += "en Jeu : " + str(self.enJeu) + "\n"
        return toReturn

    def ajouterAScene(self, sceneAAjouter):
        self.scenes.add(sceneAAjouter)
        sceneAAjouter.roles.add(self)


# intrigue
class Intrigue:

    def __init__(self, nom="intrigue sans nom", description="Description à écrire", pitch="pitch à écrire",
                 questions_ouvertes="", notes="", resolution="", orgaReferent="", url="", timeline="", lastChange=datetime.datetime.now(), scenesEnJeu =""):
        self.nom = nom
        self.roles = {} #nom, rôle
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

    def __str__(self):
        return self.nom

    #vérifier que le personnge que l'on souhaite associer à un rôle n'est pas déjà associé à un autre rôle
    #dans la même intrigue
    #Si c'est le cas :
    #   renvoyer -1 : un même personnage ne peut être associé qu'à un seul rôle dans une intrigue
    #Sinon :
    #   réaliser l'association entre le personnage et le rôle
    #   ajouter le rôle à la liste des rôles du personnage
    #   renvoyer 0

    def associerRoleAPerso(self, roleAAssocier, personnage):
        #pour chaque rôle qui fait partie des rôles de l'intrigue
        for role in self.roles.values():
            #si le personnage que l'on souhaite associer au rôle est déjà associé à un rôle dans l'intrigue
            if role.perso == personnage:
            #ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au sein d'une mêm intrigue
                # print("Erreur : impossible d'associer le personnage {0} au rôle {1} dans l'intrigue {2} : il est déjà "
                #       "associé au rôle {3}".format(personnage.nom, roleAAssocier.nom, self.nom, role.nom))
                return -1
        roleAAssocier.perso = personnage
        personnage.roles.add(roleAAssocier)
        return 0

    def getNomsRoles(self):
        return self.roles.keys()


    # def getOrAddRole(self, nom):
    #     for role in self.roles:
    #         if role == nom:
    #             return role
    #     nouveauRole = Role(nom=nom, intrigue=self)
    #     self.roles.add(nouveauRole)
    #     return nouveauRole
    #todo : réutiliser cette fonction quand on voudra vérifier que les persos dans les scènes sont bien dans les intrigues

    def addScene(self, nomScene):
        sceneAajouter = Scene(self, nomScene)
        self.scenes.add(sceneAajouter)
        return sceneAajouter

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
        self.niveau = niveau    # 1 : dans la chronologie globale,
                                #2, dans tous les personnages de l'intrigue (pour info, donc pour les autres)
                                #3 : personnages impactés uniquement
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

            if nbMois > 0 :
                dateTexte += str(nbMois)[:-2] + " mois, "

            if nbJours > 1:
                dateTexte += str(nbJours)[:-2] + " jours, "
            elif nbJours > 0:
                dateTexte += "1 jour, "
            return dateTexte[0:-2] #car meme dans le cadre de jours on a rajouté deux cars ;)

        else:
            print("la date <{0}> n'est pas un nombre".format(self.date))
            return self.date

    def addRole(self, role):
        self.roles.add(role)

    def __str__(self):
        return("Titre Scène : " + self.titre)


# objet pour tout sauvegarder


class GN:
    def __init__(self):
        self.personnages = {}
        self.intrigues = set()

    def save(self, filename):
        pickle.dump(self, filename, "w")
        print("pas de procédure de sauvegarde actuellement")

    def getNomsPersos(self):
        return self.personnages.keys()

    @staticmethod
    def load(filename):
        return pickle.load(filename)

# objets
