import pickle
import datetime
import random
import re
from enum import IntEnum

from fuzzywuzzy import process

EST_PJ = 6
EST_REROLL = 5
EST_PNJ_INFILTRE = 4
EST_PNJ_PERMANENT = 3
EST_PNJ_TEMPORAIRE = 2
EST_PNJ_HORS_JEU = 1


def est_un_pnj(niveauPJ):
    return niveauPJ == EST_PNJ_HORS_JEU or niveauPJ == EST_PNJ_TEMPORAIRE or niveauPJ == EST_PNJ_INFILTRE or niveauPJ == EST_PNJ_PERMANENT


def est_un_pj(niveauPJ):
    return niveauPJ == EST_PJ


def string_type_pj(typePJ):
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


# une superclasse qui représente un fichier qui content des scènes, avec es rtôles associés
# donc y compris les propriétés du fichier où elle se trouve (notamment date de changement)
# Attention, personnage hérite de cette classe, et contient donc deu types de rôles :
# ceux qui sont liés au personnes (roles)
# et la contenance de ceux qui sont associées à ses propres scènes (via cette classe, donc)
class ConteneurDeScene:
    def __init__(self, derniere_edition_fichier, url):
        self.scenes = set()
        self.rolesContenus = {}  # nom, rôle
        self.error_log = ErreurManager()
        self.lastFileEdit = derniere_edition_fichier
        self.modifie_par = ""
        self.url = url

    def texte_error_log(self):
        return str(self.error_log)

    def add_to_error_log(self, niveau, message, origine):
        self.error_log.ajouter_erreur(niveau, message, origine)
        # une erreur :
        # un endroit ou c'est détecté : tableau des intrigues, rôles, personnages

    def clearErrorLog(self):
        self.error_log = ""

    def getNomsRoles(self):
        return self.rolesContenus.keys()

    def addScene(self, nomScene):
        sceneAajouter = Scene(self, nomScene)
        sceneAajouter.derniere_mise_a_jour = self.lastFileEdit
        self.scenes.add(sceneAajouter)
        return sceneAajouter

    def getScenesTriees(self):
        return Scene.trierScenes(self.scenes)

    def clear(self):
        # retirer l'intrigue du GN > à faire au niveau de l'appel
        # casser toutes les relations role <> personnages
        for role in self.rolesContenus.values():
            # print(f"Role à dissocier  : {role.nom} de {role.perso}")
            if role.perso is not None:
                role.perso.roles.remove(role)
                del role
        # self.roles.clear()

        # effacer toutes les scènes de l'intrigue
        for scene in self.scenes:
            del scene
        # self.scenes.clear()
        # print(f"intrigue effacée {self.nom}")
        self.error_log = ''

    def getFullUrl(self):
        return "https://docs.google.com/document/d/" + self.url

    def updater_dates_maj_scenes(self, conteneur_de_reference):
        for ma_scene in self.scenes:
            # print(f"*** je suis en train de lire la scène {ma_scene.titre} dans l'élément {self.getFullUrl()}")
            # On va chercher si cette scène existe déjà dans l'objet intrigue précédent
            for sa_scene in conteneur_de_reference.scenes:
                # print(f"je suis en train la comparer à la scène {sa_scene.titre} "
                #       f"dans l'élément {conteneur_de_reference.getFullUrl()}")
                if ma_scene.titre == sa_scene.titre:
                    # print(f"Les deux scènes ont le même titre !")
                    if ma_scene.description == sa_scene.description:
                        # print(f"et la même description !")
                        # print(f"dernières mises à jour : ma_scene : {ma_scene.derniere_mise_a_jour} / sa_scène : {sa_scene.derniere_mise_a_jour}")
                        ma_scene.derniere_mise_a_jour = sa_scene.derniere_mise_a_jour
                        ma_scene.modifie_par = sa_scene.modifie_par
                        # print(f"et, après update : ma_scene : {ma_scene.derniere_mise_a_jour} / sa_scène : {sa_scene.derniere_mise_a_jour}")
                    else:
                        # print("mais pas la même description !")
                        pass

                    break


# personnage
class Personnage(ConteneurDeScene):
    def __init__(self, nom="personnage sans nom", concept="", driver="", description="", questions_ouvertes="",
                 sexe="i", pj=EST_PJ, orgaReferent="", pitchJoueur="", indicationsCostume="", textesAnnexes="", url="",
                 datesClefs="", lastChange=datetime.datetime(year=2000, month=1, day=1), forced=False,
                 derniere_edition_fichier=0):
        super(Personnage, self).__init__(derniere_edition_fichier=derniere_edition_fichier, url=url)
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
        self.datesClefs = datesClefs
        # trouver comment interpréter les textes en dessous des tableaux
        # : des scènes ?
        self.textesAnnexes = textesAnnexes
        # self.url = url
        self.lastProcessing = lastChange
        self.forced = forced

    def clear(self):
        for role in self.roles:
            role.perso = None
        self.roles.clear()

    def ajouter_role(self, r):
        self.roles.add(r)

    # def __str__(self):
    #     return "nom perso : " + self.nom

    def __str__(self):
        to_return = ""
        to_return += f"nom = {self.nom} \n"
        to_return += f"concept = {self.concept} \n"
        to_return += f"driver = {self.driver} \n"
        to_return += f"questions_ouvertes = {self.questions_ouvertes} \n"
        to_return += f"sexe = {self.sexe} \n"
        to_return += f"pj = {string_type_pj(self.pj)} \n"
        to_return += f"actif = {self.actif} \n"
        to_return += f"roles = {str(self.roles)} \n"
        to_return += f"relations = {str(self.relations)} \n"
        to_return += f"images = {self.images} \n"
        to_return += f"description = {self.description} \n"
        to_return += f"orgaReferent = {self.orgaReferent} \n"
        to_return += f"joueurs = {self.joueurs.values()} \n"
        to_return += f"pitchJoueur = {self.pitchJoueur} \n"
        to_return += f"indicationsCostume = {self.indicationsCostume} \n"
        to_return += f"factions = {self.factions} \n"
        to_return += f"textesAnnexes = {self.textesAnnexes} \n"
        return to_return

    def est_un_pnj(self):
        return self.pj == EST_PNJ_HORS_JEU or self.pj == EST_PNJ_TEMPORAIRE or self.pj == EST_PNJ_INFILTRE or self.pj == EST_PNJ_PERMANENT

    def est_un_pj(self):
        return self.pj == EST_PJ

    def sommer_pip(self):
        pip = 0
        for role in self.roles:
            pip += role.sommer_pip()
        return pip


# rôle
class Role:

    def __init__(self, conteneur, perso=None, nom="rôle sans nom", description="", pipi=0, pipr=0, sexe="i", pj=EST_PJ,
                 typeIntrigue="", niveauImplication="", perimetre_intervention="", issu_dune_faction=False,
                 pip_globaux=0):
        self.conteneur = conteneur
        self.perso = perso
        self.nom = nom
        self.description = description
        self.pipr = pipr
        self.pipi = pipi
        self.pip_globaux = pip_globaux
        self.pip_total = 0
        self.sommer_pip()
        self.pj = pj
        self.sexe = sexe
        self.typeIntrigue = typeIntrigue
        self.niveauImplication = niveauImplication
        self.scenes = set()
        self.perimetreIntervention = perimetre_intervention
        self.issu_dune_faction = issu_dune_faction

    def __str__(self):
        toReturn = ""
        toReturn += "provenance : " + self.conteneur.nom + "\n"
        toReturn += "nom dans provenance : " + self.nom + "\n"
        if self.perso is None:
            toReturn += "perso : aucun" + "\n"
        else:
            toReturn += "perso : " + self.perso.nom + "\n"
        toReturn += "description : " + self.description + "\n"
        # toReturn += "pipr : " + str(self.pipr) + "\n"
        # toReturn += "pipi : " + str(self.pipi) + "\n"
        toReturn += "pj : " + string_type_pj(self.pj) + "\n"
        # toReturn += "sexe : " + self.sexe + "\n"
        toReturn += "typeIntrigue : " + self.typeIntrigue + "\n"
        toReturn += "niveauImplication : " + self.niveauImplication + "\n"
        return toReturn

    def ajouter_a_scene(self, sceneAAjouter):
        self.scenes.add(sceneAAjouter)
        sceneAAjouter.roles.add(self)

    def est_un_pnj(self):
        return est_un_pnj(self.pj)

    def sommer_pip(self):
        # print(f"je suis en train de sommer {self.nom}")
        self.pip_total = int(self.pip_globaux) + int(self.pipi) + int(self.pipr)
        return self.pip_total


# intrigue
class Intrigue(ConteneurDeScene):

    def __init__(self, url, nom="intrigue sans nom", description="Description à écrire", pitch="pitch à écrire",
                 questions_ouvertes="", notes="", resolution="", orgaReferent="", timeline="", questionnaire="",
                 lastProcessing=None,
                 derniere_edition_fichier=0):
        super(Intrigue, self).__init__(derniere_edition_fichier=derniere_edition_fichier, url=url)
        self.nom = nom
        self.description = description
        self.pitch = pitch
        self.questions_ouvertes = questions_ouvertes
        self.questionnaire = questionnaire
        self.notes = notes
        self.resolution = resolution
        self.orgaReferent = orgaReferent
        # self.dateModification = datetime.datetime.now() #seul usage dans le projet d'après l'inspecteur, je vire
        # self.url = url
        self.timeline = timeline
        if lastProcessing is None:
            lastProcessing = datetime.datetime.now() - datetime.timedelta(days=500 * 365)
        self.lastProcessing = lastProcessing

        self.lastFileEdit = derniere_edition_fichier
        self.objets = set()

    def __str__(self):
        return self.nom

    def clear(self):
        # retirer l'intrigue du GN > à faire au niveau de l'appel
        super().clear()

        # se séparer de tous les objets
        for objet in self.objets:
            objet.inIntrigues.remove(self)
        # self.objets.clear()

    # vérifier que le personnge que l'on souhaite associer à un rôle n'est pas déjà associé à un autre rôle
    # dans le même conteneur
    # Si c'est le cas :
    #   renvoyer -1 : un même personnage ne peut être associé qu'à un seul rôle dans un conteneur
    # Sinon :
    #   réaliser l'association entre le personnage et le rôle
    #   ajouter le rôle à la liste des rôles du personnage
    #   renvoyer 0
    def associer_role_a_perso(self, role_a_associer, personnage, verbal=True):
        # pour chaque rôle qui fait partie des rôles de l'intrigue
        for role in self.rolesContenus.values():
            # si le personnage que l'on souhaite associer au rôle est déjà associé à un rôle dans l'intrigue
            if role.perso is personnage:
                # ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au sein d'une mêm intrigue

                # todo : nettoyer à un moement le fichier des erreurs d'associations.
                # en effet, si on fait évoluer la liste des pjs/pnjs mais sans changer l'intrigue, les logs restent alors que le problème est régle...

                texteErreur = f"lors de la tentative d'associer le role " \
                              f"{role_a_associer.nom} au personnage {personnage.nom} (meilleur choix) : " \
                              f"celui-ci a déjà été automatiquement associé au rôle {role.nom} dans {self.nom}"
                self.add_to_error_log(ErreurAssociation.NIVEAUX.ERREUR,
                                      texteErreur,
                                      ErreurAssociation.ORIGINES.ASSOCIATION_AUTO
                                      )

                if verbal:  # et si on a demandé à ce que la fonction raconte sa vie, on détaille
                    print(texteErreur)
                return -1
        role_a_associer.perso = personnage
        # au passage on update le niveau de perso (surtout utile pour les PNJs), en prenant toujours le max
        personnage.pj = max(personnage.pj, role_a_associer.pj)
        personnage.roles.add(role_a_associer)
        return 0


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
    def __init__(self, conteneur, titre, date="0", pitch="Pas de description simple",
                 description="Description complète",
                 actif=True, resume="", niveau=3):
        self.conteneur = conteneur
        self.date = date  # stoquée sous la forme d'un nombre négatif représentant le nombre de jours entre le GN et
        # l'évènement
        self.titre = titre
        self.pitch = pitch
        self.description = description
        self.actif = actif
        self.roles = set()
        self.nom_factions = set()  # des strings qui contiennent les noms des factions à embarquer
        self.niveau = niveau  # 1 : dans la chronologie globale,
        # 2, dans tous les personnages de l'intrigue (pour info, donc pour les autres)
        # 3 : personnages impactés uniquement
        # faut-il dire que role et personnages héritent l'un de l'autre? Ou bien d'un objet "protagoniste"?
        self.noms_roles_lus = None
        self.derniere_mise_a_jour = datetime.datetime.now()
        self.modifie_par = ""

    def get_date(self):
        return self.date

    def getLongdigitsDate(self, size=30):
        # print(f"date : {self.date}")
        # if type(self.date) == float or type(self.date) == int or str(self.date[1:]).isnumeric():
        if type(self.date) == float or type(self.date) == int or re.match(r"^-\d+$", self.date):

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

        toReturn += f"titre scène : {self.titre} - date  : {self.getFormattedDate()} \n"
        strRolesPersos = 'Roles (Perso) : '
        for role in self.roles:
            if role.perso is None:
                strRolesPersos += f"{role.nom} (pas de perso affecté) / "
            else:
                strRolesPersos += f" {role.nom} ({role.perso.nom}) / "
        toReturn += f"roles  : {strRolesPersos[:-2]} \n"
        toReturn += f"provenance : {self.conteneur.nom} \n"
        # toReturn += f"dernière édition de la scène : {self.derniere_mise_a_jour} \n"
        toReturn += f"dernières éditions : intrigue : {self.conteneur.lastFileEdit}  " \
                    f"/ scène : {self.derniere_mise_a_jour} \n"
        toReturn += f"url intrigue : {self.conteneur.getFullUrl()} \n"
        # toReturn += f"pitch  : {self.pitch} \n"
        # toReturn += f"description : \n {self.description} \n"
        toReturn += f"\n {self.description} \n"

        # toReturn += f"actif  : {self.actif} \n"
        return toReturn

    # def dict_text(self):
    #     toReturn = dict()
    #
    #     toReturn["titre"] = f"titre scène : {self.titre} - date {self.getFormattedDate()} \n"
    #
    #     texte_entete = ""
    #     strRolesPersos = 'Roles (Perso) : '
    #     for role in self.roles:
    #         if role.perso is None:
    #             strRolesPersos += f"{role.nom} (pas de perso affecté) / "
    #         else:
    #             strRolesPersos += f" {role.nom} ({role.perso.nom}) / "
    #     texte_entete += f"roles  : {strRolesPersos} \n"
    #     texte_entete += f"provenance : {self.conteneur.nom} \n"
    #     texte_entete += f"dernière édition de la scène : {self.derniere_mise_a_jour} \n"
    #     texte_entete += f"dernière édition de l'intrigue : {self.conteneur.lastFileEdit} \n"
    #     texte_entete += f"url intrigue : {self.conteneur.getFullUrl()} \n"
    #     toReturn["en-tete"] = texte_entete
    #
    #     toReturn["corps"] = f"\n {self.description} \n"
    #
    #     # texte_entete += f"actif  : {self.actif} \n"
    #     return toReturn

    @staticmethod
    def trierScenes(scenesATrier):
        return sorted(scenesATrier, key=lambda scene: scene.getLongdigitsDate(), reverse=True)


# objet pour tout sauvegarder
class Faction:
    def __init__(self, nom: str):
        self.nom = nom
        self.personnages = set()

    def __str__(self):
        list_perso = [p.nom for p in self.personnages]
        return f"Faction {self.nom} avec les personnages {list_perso}"


class GN:
    def __init__(self,
                 dossiers_intrigues, dossier_output: str,
                 association_auto: bool = False, dossiers_pj=None, dossiers_pnj=None, id_factions=None):

        # création des objets nécessaires
        self.dictPJs = {}  # idgoogle, personnage
        self.dictPNJs = {}  # idgoogle, personnage
        self.factions = dict()  # nom, Faction
        self.intrigues = dict()  # clef : id google
        self.oldestUpdateIntrigue = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatePJ = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatedIntrigue = ""  # contient l'id de la dernière intrigue updatée dans le GN
        self.oldestUpdatedPJ = ""  # contient l'id du dernier PJ updaté dans le GN

        # injection des paramètres du fichier de config
        self.association_auto = None
        self.id_factions = None
        self.dossiers_pnjs = None
        self.dossiers_pjs = None
        self.dossier_outputs_drive = None
        self.dossiers_intrigues = None
        self.injecter_config(dossiers_intrigues, dossier_output, association_auto, dossiers_pj=dossiers_pj,
                             dossiers_pnj=dossiers_pnj, id_factions=id_factions)

    def injecter_config(self,
                        dossiers_intrigues, dossier_output, association_auto,
                        dossiers_pj=None, dossiers_pnj=None, id_factions=None, noms_pjs=None, noms_pnjs=None):
        # todo : injecter les noms des PJs et le dossier PNJ

        self.liste_noms_pjs = noms_pjs
        self.liste_noms_pnjs = noms_pnjs
        if isinstance(dossiers_intrigues, list):
            self.dossiers_intrigues = dossiers_intrigues
        else:
            self.dossiers_intrigues = [dossiers_intrigues]

        if dossiers_pj is not None:
            if isinstance(dossiers_pj, list):
                self.dossiers_pjs = dossiers_pj
            else:
                self.dossiers_pjs = [dossiers_pj]
        else:
            self.dossiers_pjs = None

        if dossiers_pnj is not None:
            if isinstance(dossiers_pnj, list):
                self.dossiers_pnjs = dossiers_pnj
            else:
                self.dossiers_pnjs = [dossiers_pnj]
        else:
            self.dossiers_pnjs = None

        self.id_factions = id_factions
        self.dossier_outputs_drive = dossier_output

        self.association_auto = association_auto

    def ajouter_faction(self, faction: Faction):
        self.factions[faction.nom] = faction

    def rechercher_faction(self, nom: str) -> Faction:
        if nom in self.factions:
            return self.factions[nom]
        else:
            raise ValueError(f"La faction {nom} n'a pas été trouvée")

    def effacer_personnages_forces(self):
        # print(list(self.dictPJs.values()) + list(self.dictPNJs.values()))
        # for personnage in self.dictPJs.values():
        #     if personnage.forced:
        #         self.dictPNJs.pop(personnage.nom, None)
        #         personnage.clear()
        # # print(list(self.dictPJs.values()) + list(self.dictPNJs.values()))
        # # for personnage in list(self.dictPJs.values()) + list(self.dictPNJs.values()):
        # #     if personnage.forced:
        # #         self.dictPJs.pop(personnage.nom, None)
        # #         self.dictPNJs.pop(personnage.nom, None)
        # #         personnage.clear()

        for personnage in list(self.dictPJs.values()) + list(self.dictPNJs.values()):
            if personnage.forced:
                self.dictPJs.pop(personnage.url, None)
                self.dictPNJs.pop(personnage.url, None)
                personnage.clear()

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
        # for prop, value in vars(self).items():
        #     print(prop, ":", type(value))

        filehandler = open(filename, "wb")
        pickle.dump(self, filehandler)
        filehandler.close()

    def noms_pjs(self):
        # return self.dictPJs.keys()
        return [x.nom for x in self.dictPJs.values()]

    def noms_pnjs(self):
        return [pnj.nom for pnj in self.dictPNJs.values()]

    def noms_pjpnjs(self, pj: bool):
        if pj:
            return self.noms_pjs()
        else:
            return self.noms_pnjs()

    # def associerPNJsARoles(self, seuilAlerte=90, verbal=True):
    #     nomsPnjs = self.liste_noms_pnjs()
    #     for intrigue in self.intrigues.values():
    #         for role in intrigue.rolesContenus.values():
    #             if est_un_pnj(role.pj):
    #                 score = process.extractOne(role.nom, nomsPnjs)
    #                 if score is None:
    #                     print(f"probleme lors de l'association de {role.nom} avec la liste : {nomsPnjs}")
    #                 # role.perso = self.listePnjs[score[0]]
    #                 # print(f"je m'apprête à associer PNJ {role.nom}, identifié comme {score} ")
    #                 # print(f"\t à {self.dictPNJs[score[0]].nom} (taille du dictionnaire PNJ = {len(self.dictPNJs)}")
    #                 intrigue.associer_role_a_perso(role_a_associer=role, personnage=self.dictPNJs[score[0]])
    #                 if score[1] < seuilAlerte:
    #                     texteErreur = f"Warning association ({score[1]}) " \
    #                                   f"- nom rôle : {role.nom} > PNJ : {score[0]} dans {intrigue.nom}"
    #                     intrigue.add_to_error_log(texteErreur)
    #                     if verbal:
    #                         print(texteErreur)
    #
    # def associer_pj_a_roles(self, seuilAlerte=70, verbal=True):
    #     print("Début de l'association automatique des rôles aux persos")
    #     nomsPjs = self.liste_noms_pjs()
    #     if verbal:
    #         print(f"noms pjs = {self.liste_noms_pjs()}")
    #     dictNomsPJ = dict()
    #     for pj in self.dictPJs.values():  # on crée un dictionnaire temporaire nom > pj pour faire les associations
    #         dictNomsPJ[pj.nom] = pj
    #
    #     # Associer les rôles sans passer par la case tableau d'association
    #     # pour les rôles issus des scènes dans les fiches de PJs
    #     for pj in self.dictPJs.values():
    #         # print(f"je suis en train de chercher des roles dans le pj {pj.nom}")
    #         # print(f"noms de roles trouvés : {pj.rolesContenus}")
    #         for role in pj.rolesContenus.values():
    #             # print(f"je suis en train d'essayer d'associer le rôle {role.nom} issu du personnage {pj.nom}")
    #             score = process.extractOne(role.nom, nomsPjs)
    #             # print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
    #             role.perso = dictNomsPJ[score[0]]
    #             role.perso.roles.add(role)
    #
    #             if score[1] < seuilAlerte:
    #                 texteErreur = f"Warning association ({score[1]}) - nom rôle : " \
    #                               f"{role.nom} > PJ : {score[0]} dans {pj.nom}"
    #                 pj.add_to_error_log(texteErreur)
    #                 if verbal:
    #                     # print(f"je paaaaaarle {score[1]}")
    #                     print(texteErreur)
    #
    #     # faire l'association dans les intrigues à partir du nom de l'intrigue
    #     # pour chaque role contenu dans chaque intrigue, retrouver le nom du pj correspondant
    #     for intrigue in self.intrigues.values():
    #         for role in intrigue.rolesContenus.values():
    #             if est_un_pj(role.pj):
    #                 # print(f"nom du role testé = {role.nom}")
    #                 score = process.extractOne(role.nom, nomsPjs)
    #                 # print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
    #                 check = intrigue.associer_role_a_perso(role_a_associer=role, personnage=dictNomsPJ[score[0]],
    #                                                        verbal=verbal)
    #
    #                 if score[1] < seuilAlerte:
    #                     texteErreur = f"Warning association ({score[1]}) - nom rôle : " \
    #                                   f"{role.nom} > PJ : {score[0]} dans {intrigue.nom}"
    #                     intrigue.add_to_error_log(texteErreur)
    #                     if verbal:
    #                         # print(f"je paaaaaarle {score[1]}")
    #                         print(texteErreur)
    #
    #     print("Fin de l'association automatique des rôles aux persos")

    def associer_pnj_a_roles(self, seuilAlerte=70, verbal=True):
        self.associer_pjpnj_a_roles(pj=False, seuilAlerte=seuilAlerte, verbal=verbal)

    def associer_pj_a_roles(self, seuilAlerte=70, verbal=True):
        self.associer_pjpnj_a_roles(pj=True, seuilAlerte=seuilAlerte, verbal=verbal)

    def associer_pjpnj_a_roles(self, pj: bool, seuilAlerte=70, verbal=True):
        print("Début de l'association automatique des rôles aux persos")
        noms_persos = self.noms_pjpnjs(pj)
        if pj:
            dict_reference = self.dictPJs
        else:
            dict_reference = self.dictPNJs
            test = [e.nom for e in self.dictPNJs.values()]
            print(f"test = {test}")

        if verbal:
            print(f"pj? {pj}, noms persos = {noms_persos}")

        dict_noms_persos = dict()
        for perso in dict_reference.values():  # on crée un dictionnaire temporaire nom > pj pour faire les associations
            dict_noms_persos[perso.nom] = perso

        # Associer les rôles sans passer par la case tableau d'association
        # pour les rôles issus des scènes dans les fiches de PJs
        for perso in dict_reference.values():
            # print(f"je suis en train de chercher des roles dans le pj {pj.nom}")
            # print(f"noms de roles trouvés : {pj.rolesContenus}")
            for role in perso.rolesContenus.values():
                print(f"je suis en train d'essayer d'associer le rôle {role.nom} issu du personnage {perso.nom}")
                score = process.extractOne(role.nom, noms_persos)
                print(f"Pour {role.nom} dans {role.conteneur.nom}, score = {score}")
                role.perso = dict_noms_persos[score[0]]
                role.perso.roles.add(role)

                if score[1] < seuilAlerte:
                    texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                   f"{role.nom} > perso : {score[0]} dans {perso.nom}"
                    perso.add_to_error_log(ErreurAssociation.NIVEAUX.WARNING,
                                           texte_erreur,
                                           ErreurAssociation.ORIGINES.ASSOCIATION_AUTO)
                    if verbal:
                        # print(f"je paaaaaarle {score[1]}")
                        print(texte_erreur)

        # faire l'association dans les intrigues à partir du nom de l'intrigue
        if pj:
            critere = est_un_pj
        else:
            critere = est_un_pnj
        # pour chaque role contenu dans chaque intrigue, retrouver le nom du pj correspondant
        for intrigue in self.intrigues.values():
            for role in intrigue.rolesContenus.values():
                if critere(role.pj):
                    # print(f"nom du role testé = {role.nom}")
                    score = process.extractOne(role.nom, noms_persos)
                    # print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
                    check = intrigue.associer_role_a_perso(role_a_associer=role, personnage=dict_noms_persos[score[0]],
                                                           verbal=verbal)

                    if score[1] < seuilAlerte:
                        texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                       f"{role.nom} > perso : {score[0]} dans {intrigue.nom}"
                        intrigue.add_to_error_log(ErreurAssociation.NIVEAUX.WARNING,
                                                  texte_erreur,
                                                  ErreurAssociation.ORIGINES.ASSOCIATION_AUTO
                                                  )
                        if verbal:
                            # print(f"je paaaaaarle {score[1]}")
                            print(texte_erreur)

        print("Fin de l'association automatique des rôles aux persos")

    @staticmethod
    def load(filename):
        mon_fichier = open(filename, 'rb')
        return pickle.load(mon_fichier)

    # apres une importation recrée
    # tous les liens entre les PJs,
    # les PNJs
    # et les fonctions d'accélération de ré-importations

    def rebuild_links(self, verbal=True):
        self.clear_all_associations()
        self.updateOldestUpdate()
        self.ajouter_roles_issus_de_factions(verbal)
        self.associer_pnj_a_roles(verbal)
        self.associer_pj_a_roles(verbal)

    # lire les factions dans toutes les scènes
    # normaliser leurs noms pour etre sur de lire la bonne
    # pour chaque nom de la faction chercher si le role est dans la scène
    # si oui (indice de confiance suffisant) > ajouter la scène au role
    # si non > ajouter un nouveau role avec une propriété issu_dune_faction= true

    def ajouter_roles_issus_de_factions(self, seuil_nom_faction=85, seuil_reconciliation_role=80, verbal: bool = False):
        # lire toutes les scènes pours trouver les factions
        for intrigue in self.intrigues.values():
            for scene in intrigue.scenes:
                for nom_faction in scene.nom_factions:
                    # quand on trouve une faction on cherche dans le GN le bon nom
                    print(f"nom_faction, self.factions = {nom_faction}, {self.factions.keys()}")
                    score_faction = process.extractOne(nom_faction, self.factions.keys())
                    print(f"score_faction = {score_faction}")
                    if score_faction[1] < seuil_nom_faction:
                        intrigue.error_log += f"Warning : la faction {nom_faction} " \
                                              f"a été associée à {score_faction[0]} " \
                                              f"à seulement {score_faction[1]}% de confiance"
                    ma_faction = self.factions[score_faction[0]]
                    # pour chaque personnage de la faction, on vérifie s'il a une correspondance
                    # dans les persos de la scène, en définissant un seuil d'acceptabilité
                    for personnage_dans_faction in ma_faction.personnages:
                        print(f"personnage_dans_faction, intrigue.rolesContenus.keys() ="
                              f" {personnage_dans_faction.nom}, {intrigue.rolesContenus.keys()}")
                        score_role = process.extractOne(personnage_dans_faction.nom, intrigue.rolesContenus.keys())
                        if score_role[1] < seuil_reconciliation_role:
                            texte_info = f"{personnage_dans_faction.nom} " \
                                         f"a été ajouté via la faction {nom_faction} " \
                                         f"pour la scène {scene.titre} \n"
                            intrigue.error_log.ajouter_erreur(ErreurAssociation.NIVEAUX.INFO,
                                                              texte_info,
                                                              ErreurAssociation.ORIGINES.FACTION
                                                              )
                            # ajouter un nouveau role dans l'intrigue avec personnage_dans_faction = true
                            role_a_ajouter = Role(intrigue,
                                                  nom=personnage_dans_faction.nom,
                                                  description=f"Role ajouté via la faction {nom_faction}",
                                                  issu_dune_faction=True
                                                  )
                            intrigue.rolesContenus[role_a_ajouter.nom] = role_a_ajouter
                            # l'ajouter à la scène
                            role_a_ajouter.ajouter_a_scene(scene)

                        else:
                            # ajouter la scène au role
                            intrigue.rolesContenus[score_role[0]].ajouter_a_scene(scene)

    # todo : quand on loade le fichier faction, clearer les factions pour prendre en compte les suppressions entre deux loading

    # utilisée pour préparer lassociation roles/persos
    # l'idée est qu'avec la sauvegarde les associations restent, tandis que si les pj/pnj ont bougé ca peut tout changer
    def clear_all_associations(self):
        # for pj in self.dictPJs.values():
        #     pj.roles.clear()
        # for pnj in self.dictPNJs.values():
        #     pnj.roles.clear()
        for perso in list(self.dictPJs.values()) + list(self.dictPNJs.values()):
            perso.roles.clear()
            perso.error_log.clear(ErreurAssociation.ORIGINES.ASSOCIATION_AUTO)
            perso.error_log.clear(ErreurAssociation.ORIGINES.FACTION)

        for intrigue in self.intrigues.values():
            # intrigue.clearErrorLog()
            for role in intrigue.rolesContenus.values():
                role.perso = None

    # def forcer_import_pnjs(self, liste_pnjs):
    #     for nom in liste_pnjs:
    #         #on met comme clef le nom en l'absence d'URL
    #         self.dictPNJs[nom] = Personnage(nom=nom, forced=True, pj=EST_PNJ_HORS_JEU)

    # def forcer_import_pjs(self, nomsPersos, suffixe="_imported", verbal=False):
    #     print("début de l'ajout des personnages sans fiche")
    #     nomsLus = [x.nom for x in self.dictPJs.values()]
    #     print(f"noms lus = {nomsLus}")
    #     # pour chaque perso de ma liste :
    #     # SI son nom est dans les persos > ne rien faire
    #     # SINON, lui créer une coquille vide
    #     persosSansCorrespondance = []
    #     for perso in nomsPersos:
    #         if perso in nomsLus and verbal:
    #             print(f"le personnage {perso} a une correspondance dans les persos déjà présents")
    #         else:
    #             # persosSansCorrespondance.append(
    #             #     [perso,
    #             #      process.extractOne(perso, nomsLus)[0],
    #             #      process.extractOne(perso, nomsLus)[1]])
    #             scoreproche = process.extractOne(perso, nomsLus)
    #             # print(f"avant assicoation, {perso} correspond à {scoreproche[0]} à {scoreproche[1]}%")
    #             if scoreproche is not None and scoreproche[1] >= 75:
    #                 if verbal:
    #                     print(f"{perso} correspond à {scoreproche[0]} à {scoreproche[1]}%")
    #                 # donc on ne fait rien
    #             else:
    #                 if verbal:
    #                     print(f"{perso} a été créé (coquille vide)")
    #                 self.dictPJs[perso + suffixe] = Personnage(nom=perso, pj=EST_PJ,
    #                                                            forced=True)  # on met son nom en clef pour se souvenir qu'il a été généré

    def forcer_import_pjs(self, noms_persos, suffixe="_imported", verbal=False):
        return self.forcer_import_pjpnjs(noms_persos=noms_persos, pj=True, suffixe=suffixe, verbal=verbal)

    def forcer_import_pnjs(self, noms_persos, suffixe="_imported", verbal=False):
        return self.forcer_import_pjpnjs(noms_persos=noms_persos, pj=False, suffixe=suffixe, verbal=verbal)

    def forcer_import_pjpnjs(self, noms_persos, pj: bool, suffixe="_imported", verbal=False):
        print("début de l'ajout des personnages sans fiche")
        # nomsLus = [x.nom for x in self.dictPJs.values()]
        if pj:
            dict_actif = self.dictPJs
        else:
            dict_actif = self.dictPNJs
        noms_lus = self.noms_pjpnjs(pj)
        print(f"noms lus = {noms_lus}")
        # pour chaque perso de ma liste :
        # SI son nom est dans les persos > ne rien faire
        # SINON, lui créer une coquille vide
        if pj:
            valeur_pj = EST_PJ
        else:
            valeur_pj = EST_PNJ_HORS_JEU
        persosSansCorrespondance = []
        for perso in noms_persos:
            if perso in noms_lus and verbal:
                print(f"le personnage {perso} a une correspondance dans les persos déjà présents")
            else:
                scoreproche = process.extractOne(perso, noms_lus)
                # print(f"avant assicoation, {perso} correspond à {scoreproche[0]} à {scoreproche[1]}%")
                if scoreproche is not None and scoreproche[1] >= 75:
                    if verbal:
                        print(f"{perso} correspond à {scoreproche[0]} à {scoreproche[1]}%")
                    # donc on ne fait rien
                else:
                    if verbal:
                        print(f"{perso} a été créé (coquille vide)")
                    dict_actif[perso + suffixe] = Personnage(nom=perso, pj=valeur_pj,
                                                               forced=True)  # on met son nom en clef pour se souvenir qu'il a été généré

                    # self.dictPJs[perso + suffixe] = Personnage(nom=perso, pj=valeur_pj,
                    #                                            forced=True)  # on met son nom en clef pour se souvenir qu'il a été généré


# objets

class Objet:
    def __init__(self, description="", fourniPar="Inconnu", emplacementDebut="", specialEffect=""):
        self.description = description
        self.fourniParJoueur = fourniPar
        self.emplacementDebut = emplacementDebut
        self.rfid = len(specialEffect) > 0
        self.specialEffect = specialEffect
        self.inIntrigues = set()


class ErreurAssociation:
    def __init__(self, niveau, texte, genere_par):
        self.niveau = niveau
        self.texte = texte
        self.origine = genere_par

    def __str__(self):
        if self.niveau == self.NIVEAUX.ERREUR:
            prefixe = "Erreur : "
        elif self.niveau == self.NIVEAUX.WARNING:
            prefixe = "Warning : "
        else:
            prefixe = "Info : "

        return prefixe + self.texte

    class NIVEAUX(IntEnum):
        INFO = 10
        WARNING = 20
        ERREUR = 30

    class ORIGINES(IntEnum):
        SCENE = 1
        FACTION = 2
        ASSOCIATION_AUTO = 3


class ErreurManager:
    def __init__(self):
        self.erreurs = []

    def nb_erreurs(self):
        return len(self.erreurs)

    def ajouter_erreur(self, niveau: ErreurAssociation.NIVEAUX, message, origine: ErreurAssociation.ORIGINES):
        self.erreurs.append(ErreurAssociation(niveau, message, origine))

    def __str__(self):
        return '\n'.join([str(erreur) for erreur in self.erreurs])

    def clear(self, niveau: ErreurAssociation.ORIGINES):
        if niveau is None:
            # dans ce cas c'est qu'on veut TOUT effacer, par exempe car on va recréer le conteneur
            self.erreurs.clear()
        else:
            for erreur in self.erreurs:
                if erreur.origine == niveau:
                    self.erreurs.remove(erreur)
