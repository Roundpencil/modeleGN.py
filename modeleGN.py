import pickle
import datetime
import random
import re
from enum import IntEnum

from fuzzywuzzy import process
import sys


class TypePerso(IntEnum):
    EST_PNJ_HORS_JEU = 1
    EST_PNJ_TEMPORAIRE = 2
    EST_PNJ_PERMANENT = 3
    EST_PNJ_INFILTRE = 4
    EST_REROLL = 5
    EST_PJ = 6


def est_un_pnj(niveauPJ):
    return niveauPJ in [
        TypePerso.EST_PNJ_HORS_JEU,
        TypePerso.EST_PNJ_TEMPORAIRE,
        TypePerso.EST_PNJ_INFILTRE,
        TypePerso.EST_PNJ_PERMANENT,
    ]


def est_un_pj(niveau_pj):
    return niveau_pj == TypePerso.EST_PJ


def string_type_pj(type_pj: TypePerso):
    grille_pj = {TypePerso.EST_PJ: "PJ",
                 TypePerso.EST_REROLL: "Reroll",
                 TypePerso.EST_PNJ_INFILTRE: "PNJ Infiltré",
                 TypePerso.EST_PNJ_HORS_JEU: "PNJ Hors Jeu",
                 TypePerso.EST_PNJ_PERMANENT: "PNJ Permanent",
                 TypePerso.EST_PNJ_TEMPORAIRE: "PNJ Temporaire"}
    return grille_pj.get(type_pj, f"Type de PJ inconnu ({type_pj})")

    # if type_pj == TypePerso.EST_PJ:
    #     return "PJ"
    # if type_pj == TypePerso.EST_REROLL:
    #     return "Reroll"
    # if type_pj == TypePerso.EST_PNJ_INFILTRE:
    #     return "PNJ Infiltré"
    # if type_pj == TypePerso.EST_PNJ_PERMANENT:
    #     return "PNJ Permanent"
    # if type_pj == TypePerso.EST_PNJ_TEMPORAIRE:
    #     return "PNJ Temporaire"
    # if type_pj == TypePerso.EST_PNJ_HORS_JEU:
    #     return "PNJ Hors Jeu"
    # return f"Type de PJ inconnu ({type_pj})"


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

    def clear_error_log(self):
        self.error_log.clear()

    def get_noms_roles(self):
        return self.rolesContenus.keys()

    def ajouter_scene(self, nomScene):
        scene_a_ajouter = Scene(self, nomScene)
        scene_a_ajouter.derniere_mise_a_jour = self.lastFileEdit
        self.scenes.add(scene_a_ajouter)
        return scene_a_ajouter

    def get_scenes_triees(self, date_gn=None):
        return Scene.trier_scenes(self.scenes, date_gn=date_gn)

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
        self.error_log.clear()

    def get_full_url(self):
        return f"https://docs.google.com/document/d/{self.url}"

    def updater_dates_maj_scenes(self, conteneur_de_reference, verbal=False):
        for ma_scene in self.scenes:
            # print(f"*** je suis en train de lire la scène {ma_scene.titre} dans l'élément {self.get_full_url()}")
            # On va chercher si cette scène existe déjà dans l'objet intrigue précédent
            for sa_scene in conteneur_de_reference.scenes:
                if verbal:
                    print(f"je suis en train la comparer à la scène {sa_scene.titre} "
                          f"dans l'élément {conteneur_de_reference.get_full_url()}")
                if ma_scene.titre == sa_scene.titre:
                    # print(f"Les deux scènes ont le même titre !")
                    if ma_scene.description == sa_scene.description:
                        # print(f"et la même description !")
                        # print(f"dernières mises à jour : ma_scene : {ma_scene.derniere_mise_a_jour} / sa_scène : {sa_scene.derniere_mise_a_jour}")
                        ma_scene.derniere_mise_a_jour = sa_scene.derniere_mise_a_jour
                        ma_scene.modifie_par = sa_scene.modifie_par
                        # print(f"et, après update : ma_scene : {ma_scene.derniere_mise_a_jour} / sa_scène : {sa_scene.derniere_mise_a_jour}")
                    elif verbal:
                        print("mais pas la même description !")
                    break


# personnage
class Personnage(ConteneurDeScene):
    def __init__(self, nom="personnage sans nom", concept="", driver="", description="", questions_ouvertes="",
                 sexe="i", pj: TypePerso = TypePerso.EST_PJ, orgaReferent="", pitchJoueur="", indicationsCostume="",
                 textesAnnexes="", url="",
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
        self.joueurs = {}
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
        # return self.pj == TypePerso.EST_PNJ_HORS_JEU
        # or self.pj == EST_PNJ_TEMPORAIRE or self.pj == EST_PNJ_INFILTRE or self.pj == EST_PNJ_PERMANENT
        return est_un_pnj(self.pj)

    def est_un_pj(self):
        # return self.pj == EST_PJ
        return est_un_pj(self.pj)

    def sommer_pip(self):
        return sum(role.sommer_pip() for role in self.roles)

    def string_type_pj(self):
        return string_type_pj(self.pj)

        # pip = 0
        # for role in self.roles:
        #     pip += role.sommer_pip()
        # return pip


# rôle
class Role:

    def __init__(self, conteneur: ConteneurDeScene, perso=None, nom="rôle sans nom", description="", pipi=0, pipr=0,
                 sexe="i",
                 pj: TypePerso = TypePerso.EST_PJ,
                 type_intrigue="", niveau_implication="", perimetre_intervention="", issu_dune_faction=False,
                 pip_globaux=0):
        self.conteneur = conteneur
        self.perso = perso
        self.nom = nom
        self.description = description
        try:
            self.pipr = int(pipr)
        except ValueError:
            self.pipr = 0

        try:
            self.pipi = int(pipi)
        except ValueError:
            self.pipi = 0

        try:
            self.pip_globaux = int(pip_globaux)
        except ValueError:
            self.pip_globaux = 0

        self.pip_total = 0
        self.sommer_pip()
        self.pj = pj
        self.sexe = sexe
        self.typeIntrigue = type_intrigue
        self.niveauImplication = niveau_implication
        self.scenes = set()
        self.perimetre_intervention = perimetre_intervention
        self.issu_dune_faction = issu_dune_faction

    def __str__(self):
        toReturn = ""
        toReturn += f"provenance : {self.conteneur.nom}" + "\n"
        toReturn += f"nom dans provenance : {self.nom}" + "\n"
        if self.perso is None:
            toReturn += "perso : aucun" + "\n"
        else:
            toReturn += f"perso : {self.perso.nom}" + "\n"
        toReturn += f"description : {self.description}" + "\n"
        # toReturn += "pipr : " + str(self.pipr) + "\n"
        # toReturn += "pipi : " + str(self.pipi) + "\n"
        toReturn += f"pj : {string_type_pj(self.pj)}" + "\n"
        # toReturn += "sexe : " + self.sexe + "\n"
        toReturn += f"typeIntrigue : {self.typeIntrigue}" + "\n"
        toReturn += f"niveauImplication : {self.niveauImplication}" + "\n"
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
    def associer_role_a_perso(self, role_a_associer, personnage, verbal=False):
        # pour chaque rôle qui fait partie des rôles de l'intrigue
        for role in self.rolesContenus.values():
            # si le personnage que l'on souhaite associer au rôle est déjà associé à un rôle dans l'intrigue
            if role.perso is personnage:
                # ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au
                # sein d'une même intrigue

                texteErreur = f"lors de la tentative d'associer le role " \
                              f"{role_a_associer.nom} au personnage {personnage.nom} (meilleur choix) : " \
                              f"celui-ci a déjà été automatiquement associé au rôle {role.nom} dans {self.nom}"
                self.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                      texteErreur,
                                      ErreurManager.ORIGINES.ASSOCIATION_AUTO
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
    def __init__(self, perso1, perso2, description_vue_par_1="Relation à définir", description_vue_par_2="",
                 reciproque=True):
        self.perso1 = perso1
        self.perso2 = perso2
        self.description_vue_par_1 = description_vue_par_1
        self.description_vue_par_2 = description_vue_par_2
        self.reciproque = reciproque

    def partenaire(self, perso):
        if perso is self.perso1:
            return self.perso2

        if perso is self.perso2:
            return self.perso1

        raise Exception("Personnage inconnu dans cette relation")


# Scènes
class Scene:
    def __init__(self, conteneur, titre, date="TBD", pitch="Pas de description simple", date_absolue: datetime = None,
                 description="Pas de description complète",
                 actif=True, resume="", niveau=3):
        self.conteneur = conteneur
        self.date = date  # stoquée sous la forme d'un nombre négatif représentant le nombre de jours entre le GN et
        # l'évènement
        self.date_absolue = date_absolue
        self.titre = titre
        self.pitch = pitch
        self.description = description
        self.actif = actif
        self.roles = set()
        self.nom_factions = set()  # des strings qui contiennent les noms des factions à embarquer
        self.infos = set()  # des strings qui contiennent les noms où rapatrier les infos
        self.niveau = niveau  # 1 : dans la chronologie globale,
        # 2, dans tous les personnages de l'intrigue (pour info, donc pour les autres)
        # 3 : personnages impactés uniquement
        # faut-il dire que role et personnages héritent l'un de l'autre? Ou bien d'un objet "protagoniste"?
        self.noms_roles_lus = None
        self.derniere_mise_a_jour = datetime.datetime.now()
        self.modifie_par = ""
        # print(f"Je viens de créer la scène {self.titre}, avec en entrée la date {date}")

    def get_date(self):
        return self.date

    def get_formatted_date(self, date_gn=None, jours_semaine=False):
        # print(f"debut du débug affichage dates pour la scène {self.titre}, clef de tri = {self.clef_tri(date_gn)}")
        # print(f"date relative = {self.date}")
        # print(f" date absolue sans prise en compte date gn : {self.get_date_absolue()}")
        # print(f"date absolue avec prise en compte date gn {self.get_date_absolue(date_gn)}")
        # print(f"date du gn = {date_gn}")

        date_absolue_calculee = self.get_date_absolue(date_du_jeu=date_gn)

        if date_absolue_calculee == datetime.datetime.min:
            # alors c'est qu'on a une  valeur par défaut => tenter le formattage il y a
            return self.get_formatted_il_y_a()

        months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
                  "novembre", "décembre"]

        if not jours_semaine:
            date_string = f"{date_absolue_calculee.day} {months[date_absolue_calculee.month - 1]} {date_absolue_calculee.year}"
        else:
            days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            date_string = f"{days[date_absolue_calculee.weekday()]} {date_absolue_calculee.day} {months[date_absolue_calculee.month - 1]} {date_absolue_calculee.year}"
        time_string = f"{date_absolue_calculee.hour}h{date_absolue_calculee.minute}"

        return f"{date_string}, {time_string}"

    def get_formatted_il_y_a(self):
        # print("date/type > {0}/{1}".format(self.date, type(self.date)))
        if type(self.date) == float or type(self.date) == int or str(self.date[1:]).isnumeric():
            if type(self.date) == str:
                ma_date = float(self.date[1:])
            else:
                ma_date = -1 * self.date

            if ma_date == 0:
                return "Il y a 0 jours"

            date_texte = 'Il y a '
            nb_annees = ma_date // 365
            nb_mois = (ma_date - nb_annees * 365) // 30.5
            nb_jours = ma_date - nb_annees * 365 - nb_mois * 30.5

            if nb_annees > 1:
                date_texte += str(nb_annees)[:-2] + " ans, "
            elif nb_annees == 1:
                date_texte += "1 an, "

            if nb_mois > 0:
                date_texte += str(nb_mois)[:-2] + " mois, "

            if nb_jours > 1:
                date_texte += str(nb_jours)[:-2] + " jours, "
            elif nb_jours > 0:
                date_texte += "1 jour, "
            return date_texte[0:-2]  # car meme dans le cadre de jours on a rajouté deux cars ;)

        else:
            # print("la date <{0}> n'est pas un nombre".format(self.date))
            return self.date

    def ajouter_role(self, role):
        self.roles.add(role)

    def str_pour_squelette(self, date_gn=None):
        to_return = ""

        to_return += f"titre scène : {self.titre} - date  : {self.get_formatted_date(date_gn)} \n"
        str_roles_persos = 'Roles (Perso) : '
        for role in self.roles:
            if role.perso is None:
                str_roles_persos += f"{role.nom} (pas de perso affecté) / "
            else:
                str_roles_persos += f" {role.nom} ({role.perso.nom}) / "
        to_return += f"roles  : {str_roles_persos[:-2]} \n"
        to_return += f"provenance : {self.conteneur.nom} \n"
        # to_return += f"dernière édition de la scène : {self.derniere_mise_a_jour} \n"
        to_return += f"dernières éditions : intrigue : {self.conteneur.lastFileEdit}  " \
                     f"/ scène : {self.derniere_mise_a_jour} \n"
        to_return += f"url intrigue : {self.conteneur.get_full_url()} \n"
        # to_return += f"pitch  : {self.pitch} \n"
        # to_return += f"description : \n {self.description} \n"
        to_return += f"\n {self.description} \n"

        # to_return += f"actif  : {self.actif} \n"
        return to_return

    def get_date_absolue(self, date_du_jeu=None):
        # print(f"pour la scène {self.titre} dans get_d_abs = date absolue = {self.date_absolue}, date = {self.date}")
        if self.date_absolue is not None:
            return self.date_absolue
        elif date_du_jeu is not None:
            try:
                float_date = float(self.date)
                date_absolue = date_du_jeu - datetime.timedelta(days=int(float_date) * -1)
                return date_absolue
            except ValueError:
                pass
        return datetime.datetime.min

    def get_date_jours(self):
        # print(f"Je suis dans get date jour et date = {self.date}, et son type est type{type(self.date)}")
        # if isinstance(self.date, float) or isinstance(self.date, int):
        #     return self.date
        # else:
        #     # return sys.minsize
        #     return sys.maxsize * -1 - 1
        try:
            return int(float(self.date))
        except ValueError:
            print(f"la date {self.date} n'est pas un nombre")
            return sys.maxsize * -1 - 1

    # renvoie une donnée de type [a, b, c] où a est la date absolue, b la date relative et c la date texte
    # en cas d'absence, complète avec des valeurs par défaut
    # en cas de comparaison, met le texte en premier, puis les dates en il y a, puis les dates absolues
    def clef_tri(self, date_gn=None):
        return [self.get_date_absolue(date_gn), self.get_date_jours(), str(self.date)]

    @staticmethod
    def trier_scenes(scenes_a_trier, date_gn=None):
        return sorted(scenes_a_trier, key=lambda scene: scene.clef_tri(date_gn))


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
                 association_auto: bool = False, dossiers_pj=None, dossiers_pnj=None, id_factions=None, date_gn=None):

        # création des objets nécessaires
        self.dictPJs = {}  # idgoogle, personnage
        self.dictPNJs = {}  # idgoogle, personnage
        self.factions = {}  # nom, Faction
        self.intrigues = {}  # clef : id google
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
        self.date_gn = None
        self.injecter_config(dossiers_intrigues, dossier_output, association_auto, dossiers_pj=dossiers_pj,
                             dossiers_pnj=dossiers_pnj, id_factions=id_factions, date_gn=date_gn)

    def injecter_config(self,
                        dossiers_intrigues, dossier_output, association_auto,
                        dossiers_pj=None, dossiers_pnj=None, id_factions=None, noms_pjs=None,
                        noms_pnjs=None, date_gn=None):
        # todo : injecter les noms des PJs et le dossier PNJ

        self.liste_noms_pjs = noms_pjs
        self.liste_noms_pnjs = noms_pnjs
        if isinstance(dossiers_intrigues, list):
            self.dossiers_intrigues = dossiers_intrigues
        else:
            self.dossiers_intrigues = [dossiers_intrigues]

        if dossiers_pj is None:
            self.dossiers_pjs = None
        elif isinstance(dossiers_pj, list):
            self.dossiers_pjs = dossiers_pj
        else:
            self.dossiers_pjs = [dossiers_pj]

        if dossiers_pnj is None:
            self.dossiers_pnjs = None
        elif isinstance(dossiers_pnj, list):
            self.dossiers_pnjs = dossiers_pnj
        else:
            self.dossiers_pnjs = [dossiers_pnj]
        self.id_factions = id_factions
        self.dossier_outputs_drive = dossier_output

        self.association_auto = association_auto
        self.date_gn = date_gn

    def lister_toutes_les_scenes(self):
        to_return = []
        for conteneur in list(self.dictPJs.values()) \
                         + list(self.dictPNJs.values()) \
                         + list(self.intrigues.values()):
            to_return.extend(iter(conteneur.scenes))
        return to_return

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
        return self.noms_pjs() if pj else self.noms_pnjs()
        # if pj:
        #     return self.noms_pjs()
        # else:
        #     return self.noms_pnjs()

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

    def associer_pjpnj_a_roles(self, pj: bool, seuilAlerte=70, verbal=False):
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

        # on crée un dictionnaire temporaire nom > pj pour faire les associations
        dict_noms_persos = {perso.nom: perso for perso in dict_reference.values()}

        # Associer les rôles sans passer par la case tableau d'association
        # pour les rôles issus des scènes dans les fiches de PJs
        for perso in dict_reference.values():
            # print(f"je suis en train de chercher des roles dans le pj {pj.nom}")
            # print(f"noms de roles trouvés : {pj.rolesContenus}")
            for role in perso.rolesContenus.values():
                if verbal:
                    print(f"je suis en train d'essayer d'associer le rôle {role.nom} issu du personnage {perso.nom}")
                score = process.extractOne(role.nom, noms_persos)
                if verbal:
                    print(f"Pour {role.nom} dans {role.conteneur.nom}, score = {score}")
                role.perso = dict_noms_persos[score[0]]
                role.perso.roles.add(role)

                if score[1] < seuilAlerte:
                    texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                   f"{role.nom} > perso : {score[0]} dans {perso.nom}"
                    perso.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                           texte_erreur,
                                           ErreurManager.ORIGINES.ASSOCIATION_AUTO)
                    if verbal:
                        # print(f"je paaaaaarle {score[1]}")
                        print(texte_erreur)

        # faire l'association dans les intrigues à partir du nom de l'intrigue
        # identifier la bonne fonction à appliquer
        critere = est_un_pj if pj else est_un_pnj

        # pour chaque role contenu dans chaque intrigue, retrouver le nom du pj correspondant
        for intrigue in self.intrigues.values():
            for role in intrigue.rolesContenus.values():
                if critere(role.pj):
                    # print(f"nom du role testé = {role.nom}")
                    score = process.extractOne(role.nom, noms_persos)
                    if verbal:
                        print(f"Pour {role.nom} dans {intrigue.nom}, score = {score}")
                    check = intrigue.associer_role_a_perso(role_a_associer=role, personnage=dict_noms_persos[score[0]],
                                                           verbal=verbal)

                    if score[1] < seuilAlerte:
                        texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                       f"{role.nom} > perso : {score[0]} dans {intrigue.nom}"
                        intrigue.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                                  texte_erreur,
                                                  ErreurManager.ORIGINES.ASSOCIATION_AUTO
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

    def rebuild_links(self, verbal=False):
        self.clear_all_associations()
        self.updateOldestUpdate()
        self.ajouter_roles_issus_de_factions(verbal=verbal)  # todo : à tester
        self.associer_pnj_a_roles(verbal=True)
        self.associer_pj_a_roles(verbal)
        self.trouver_roles_sans_scenes()

    def trouver_roles_sans_scenes(self, verbal=False, seuil=70):
        # nettoyer tous les fichiers erreurs:
        for intrigue in self.intrigues.values():
            intrigue.error_log.clear(ErreurManager.ORIGINES.PERSOS_SANS_SCENE)

        # pour chaque intrigue
        for intrigue in self.intrigues.values():

            # prendre les noms dans le tableau
            if len(intrigue.rolesContenus) == 0:
                continue
            noms_roles_dans_tableau_intrigue = [x.nom for x in intrigue.rolesContenus.values()
                                                if not x.issu_dune_faction]

            # prendre les noms dans les scènes
            tous_les_noms_lus_dans_scenes = []
            for scene in intrigue.scenes:
                if scene.noms_roles_lus is not None:
                    # comme on prend uniquement les roles lus, on exclut de facto les persos issus de faction
                    tous_les_noms_lus_dans_scenes += scene.noms_roles_lus
            tous_les_noms_lus_dans_scenes = [x.strip() for x in tous_les_noms_lus_dans_scenes]
            tous_les_noms_lus_dans_scenes = set(tous_les_noms_lus_dans_scenes)

            # pour chaque nom dans le tableau, lui chercher une correspondance dans les scènes
            for nom in noms_roles_dans_tableau_intrigue:
                score = process.extractOne(nom, tous_les_noms_lus_dans_scenes)
                # Si inférieur au seuil, alors l'ajouter aux noms sans scènes
                if score is not None and score[1] < seuil:
                    texte_erreur = f"[--] {nom} est dans le tableau des personnages mais dans aucune scène"
                    intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                      texte_erreur,
                                                      ErreurManager.ORIGINES.PERSOS_SANS_SCENE)
                    if verbal:
                        print(f"Warning : {texte_erreur}")

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
                        texte_erreur = f"la faction {nom_faction} " \
                                       f"a été associée à {score_faction[0]} " \
                                       f"à seulement {score_faction[1]}% de confiance"
                        intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                          texte_erreur,
                                                          ErreurManager.ORIGINES.FACTION)
                    ma_faction = self.factions[score_faction[0]]
                    # pour chaque personnage de la faction, on vérifie s'il a une correspondance
                    # dans les persos de la scène, en définissant un seuil d'acceptabilité
                    for personnage_dans_faction in ma_faction.personnages:
                        if verbal:
                            print(f"personnage_dans_faction, intrigue.rolesContenus.keys() ="
                                  f" {personnage_dans_faction.nom}, {intrigue.rolesContenus.keys()}")
                        score_role = process.extractOne(personnage_dans_faction.nom, intrigue.rolesContenus.keys())
                        if score_role[1] < seuil_reconciliation_role:
                            texte_info = f"{personnage_dans_faction.nom} " \
                                         f"a été ajouté via la faction {nom_faction} " \
                                         f"pour la scène {scene.titre} \n"
                            intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                              texte_info,
                                                              ErreurManager.ORIGINES.FACTION
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

    # utilisée pour préparer l'association roles/persos
    # l'idée est qu'avec la sauvegarde les associations restent, tandis que si les pj/pnj ont bougé ca peut tout changer
    # nettoie aussi toutes les erreurs qui peuvent apparaitre durant l'association,
    # pour que celles qui restent soient celles d'actualité
    def clear_all_associations(self):
        # for pj in self.dictPJs.values():
        #     pj.roles.clear()
        # for pnj in self.dictPNJs.values():
        #     pnj.roles.clear()
        for perso in list(self.dictPJs.values()) + list(self.dictPNJs.values()):
            perso.roles.clear()
            perso.error_log.clear(ErreurManager.ORIGINES.ASSOCIATION_AUTO)
            perso.error_log.clear(ErreurManager.ORIGINES.FACTION)

        for intrigue in self.intrigues.values():
            # intrigue.clear_error_log()
            for role in intrigue.rolesContenus.values():
                role.perso = None
            intrigue.error_log.clear(ErreurManager.ORIGINES.ASSOCIATION_AUTO)
            intrigue.error_log.clear(ErreurManager.ORIGINES.FACTION)
            intrigue.error_log.clear(ErreurManager.ORIGINES.PERSOS_SANS_SCENE)

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
        dict_actif = self.dictPJs if pj else self.dictPNJs

        # if pj:
        #     dict_actif = self.dictPJs
        # else:
        #     dict_actif = self.dictPNJs
        noms_lus = self.noms_pjpnjs(pj)
        print(f"noms lus = {noms_lus}")
        # pour chaque perso de ma liste :
        # SI son nom est dans les persos > ne rien faire
        # SINON, lui créer une coquille vide
        # if pj:
        #     valeur_pj = TypePerso.EST_PJ
        # else:
        #     valeur_pj = TypePerso.EST_PNJ_HORS_JEU
        valeur_pj = TypePerso.EST_PJ if pj else TypePerso.EST_PNJ_HORS_JEU

        persos_sans_correspondance = []
        for perso in noms_persos:
            if perso in noms_lus and verbal:
                print(f"le personnage {perso} a une correspondance dans les persos déjà présents")
            else:
                score_proche = process.extractOne(perso, noms_lus)
                # print(f"avant assicoation, {perso} correspond à {score_proche[0]} à {score_proche[1]}%")
                if score_proche is not None and score_proche[1] >= 75:
                    if verbal:
                        print(f"{perso} correspond à {score_proche[0]} à {score_proche[1]}%")
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
    def __init__(self, code="", description="", fourniPar="Inconnu", emplacementDebut="", specialEffect=""):
        self.description = description
        self.fourniParJoueur = fourniPar
        self.emplacementDebut = emplacementDebut
        self.specialEffect = specialEffect
        self.code = code
        self.inIntrigues = set()

    def avec_fx(self):
        return len(self.specialEffect) > 0


class ErreurManager:
    def __init__(self):
        self.erreurs = []

    class NIVEAUX(IntEnum):
        INFO = 10
        WARNING = 20
        ERREUR = 30

    class ORIGINES(IntEnum):
        SCENE = 1
        FACTION = 2
        ASSOCIATION_AUTO = 3
        PERSOS_SANS_SCENE = 4

    class ErreurAssociation:
        def __init__(self, niveau, texte, genere_par):
            self.niveau = niveau
            self.texte = texte
            self.origine = genere_par

        def __str__(self):
            if self.niveau == ErreurManager.NIVEAUX.ERREUR:
                prefixe = "Erreur : "
            elif self.niveau == ErreurManager.NIVEAUX.WARNING:
                prefixe = "Warning : "
            else:
                prefixe = "Info : "

            return prefixe + self.texte

    def nb_erreurs(self):
        return len(self.erreurs)

    def ajouter_erreur(self, niveau: NIVEAUX, message, origine: ORIGINES):
        self.erreurs.append(self.ErreurAssociation(niveau, message, origine))

    def __str__(self):
        return '\n'.join([str(erreur) for erreur in self.erreurs])

    # def clear(self, origine: ORIGINES = None):
    #     if origine is None:
    #         # dans ce cas, c'est qu'on veut TOUT effacer, par exemple car on va recréer le conteneur
    #         self.erreurs.clear()
    #     else:
    #         for erreur in self.erreurs:
    #             if erreur.origine == origine:
    #                 self.erreurs.remove(erreur)
    #     tab_err = [[err.niveau, err.texte, err.origine] for err in self.erreurs]
    #     print(f"erreurs après nettoyage = {tab_err}")
    def clear(self, origine: ORIGINES = None):
        if origine is None:
            # dans ce cas, c'est qu'on veut TOUT effacer, par exemple car on va recréer le conteneur
            self.erreurs.clear()
        else:
            temp = [erreur for erreur in self.erreurs if erreur.origine != origine]
            # temp = []
            # for erreur in self.erreurs:
            #     if erreur.origine != origine:
            #         temp.append(erreur)
            self.erreurs = temp

        # tab_err = [[err.niveau, err.texte, err.origine] for err in self.erreurs]
        # print(f"erreurs après nettoyage = {tab_err}")


# ######## a supprimer apres remise à niveau
#
#
# class ErreurAssociation:
#     def __init__(self, niveau, texte, genere_par):
#         self.niveau = niveau
#         self.texte = texte
#         self.origine = genere_par
#
#     def __str__(self):
#         if self.niveau == ErreurManager.NIVEAUX.ERREUR:
#             prefixe = "Erreur : "
#         elif self.niveau == ErreurManager.NIVEAUX.WARNING:
#             prefixe = "Warning : "
#         else:
#             prefixe = "Info : "
#
#         return prefixe + self.texte
#
#     class NIVEAUX(IntEnum):
#         INFO = 10
#         WARNING = 20
#         ERREUR = 30
#
#     class ORIGINES(IntEnum):
#         SCENE = 1
#         FACTION = 2
#         ASSOCIATION_AUTO = 3

class Evenement:
    def __init__(self,
                 code_evenement="",
                 referent="",
                 etat="",
                 intrigue_liee="",
                 lieu="",
                 date="",
                 heure_de_demarrage="",
                 declencheur="",
                 consequences_evenement="",
                 synopsis=""):
        self.code_evenement = code_evenement
        self.referent = referent
        self.etat = etat
        self.intrigue_liee = intrigue_liee
        self.lieu = lieu
        self.date = date
        self.heure_de_demarrage = heure_de_demarrage
        self.declencheur = declencheur
        self.consequences_evenement = consequences_evenement
        self.synopsis = synopsis
        self.objets = []
        self.interventions = []
        self.briefs_pnj = []
        self.infos_pj = []


class BriefPNJPourEvenement:
    def __init__(self, nom_pnj="", costumes_et_accessoires="", implication="", situation_de_depart=""):
        self.nom_pnj = nom_pnj
        self.pnj = None
        self.costumes_et_accessoires = costumes_et_accessoires
        self.implication = implication
        self.situation_de_depart = situation_de_depart


class InfoPJPourEvenement:
    def __init__(self, nom_pj="", infos_a_fournir=""):
        self.nom_pj = nom_pj
        self.pj = None
        self.infos_a_fournir = infos_a_fournir


#  lire les fiches > on lit le tableau > on met dans un dictionnaire > on utilise get pour prendre ce qui nous intéresse
#  les appeler à partir des intrigues dans un tableau 'scène nécessaure / onm évènement)

class Intervention:
    def __init__(self, jour=None, heure=None, description=""):
        self.jour = jour
        self.heure = heure
        self.pj_impliques = []
        self.pnj_impliques = []
        self.description = description
