import traceback

from unidecode import unidecode
import contextlib
import logging
import pickle
import datetime
from enum import IntEnum
import re

import dateparser
from fuzzywuzzy import process
import sys
from packaging import version

VERSION = "1.1.20230704"
ID_FICHIER_VERSION = "1FjW4URMWML_UX1Tw7SiJBaoOV4P7F_rKG9pmnOBjO4Q"


class TypePerso(IntEnum):
    EST_PNJ_HORS_JEU = 1
    EST_PNJ_TEMPORAIRE = 2
    EST_PNJ_PERMANENT = 3
    EST_PNJ_INFILTRE = 4
    EST_REROLL = 5
    EST_PJ = 6


def est_un_pnj(niveau_pj):
    return niveau_pj in [
        TypePerso.EST_PNJ_HORS_JEU,
        TypePerso.EST_PNJ_TEMPORAIRE,
        TypePerso.EST_PNJ_INFILTRE,
        TypePerso.EST_PNJ_PERMANENT,
    ]


def est_un_pj(niveau_pj):
    return niveau_pj == TypePerso.EST_PJ


def est_un_reroll(niveau_pj):
    return niveau_pj == TypePerso.EST_REROLL


def string_type_pj(type_pj: TypePerso):
    grille_pj = {TypePerso.EST_PJ: "PJ",
                 TypePerso.EST_REROLL: "Reroll",
                 TypePerso.EST_PNJ_INFILTRE: "PNJ Infiltré",
                 TypePerso.EST_PNJ_HORS_JEU: "PNJ Hors Jeu",
                 TypePerso.EST_PNJ_PERMANENT: "PNJ Permanent",
                 TypePerso.EST_PNJ_TEMPORAIRE: "PNJ Temporaire"}
    return grille_pj.get(type_pj, f"Type de PJ inconnu ({type_pj})")


# une superclasse qui représente un fichier qui content des scènes, avec les rôles associés
# donc y compris les propriétés du fichier où elle se trouve (notamment date de changement)
# Attention, personnage hérite de cette classe, et contient donc deu types de rôles :
# ceux qui sont liés aux personnes (roles)
# et la contenance de ceux qui sont associés à ses propres scènes (via cette classe, donc)
class ConteneurDeScene:
    def __init__(self, derniere_edition_fichier, last_processing, url):
        self.scenes = set()
        self.rolesContenus = {}  # nom, rôle
        self.error_log = ErreurManager()
        self.lastFileEdit = derniere_edition_fichier
        self.modifie_par = ""
        self.url = url
        self.nom = "Conteneur sans nom"

        self.lastProcessing = last_processing or datetime.datetime.now() - datetime.timedelta(days=500 * 365)

    def get_last_processing(self):
        return self.lastProcessing

    def set_last_processing(self, valeur):
        self.lastProcessing = valeur

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

    def get_dico_roles_avec_alias(self):
        to_return = {}
        for role in self.rolesContenus.values():
            to_return[role.nom] = role
            if role.has_alias():
                for alias in role.alias_dans_intrigue:
                    to_return[f"{role.nom} aka {alias}"] = role
                    to_return[alias] = role
        return to_return
        # todo : utiliser ce dico dans qui intrigues plutot qu'une liste de noms
        #  (et remonter dans les appels de fonctions)

    def get_noms_personnages_depuis_scenes(self):
        to_return = []
        for scene in self.scenes:
            to_return.extend([role.personnage.nom for role in scene.roles if role.personnage is not None])
        return list(set(to_return))

    def ajouter_scene(self, nom_scene):
        scene_a_ajouter = Scene(self, nom_scene)
        scene_a_ajouter.derniere_mise_a_jour = self.lastFileEdit
        self.scenes.add(scene_a_ajouter)
        return scene_a_ajouter

    def get_scenes_triees(self, date_gn=None):
        return Scene.trier_scenes(self.scenes, date_gn=date_gn)

    def clear(self):
        # retirer l'intrigue du GN > à faire au niveau de l'appel
        # casser toutes les relations role <> personnages
        roles_a_effacer = self.rolesContenus.values()
        for role in roles_a_effacer:
            # print(f"Role à dissocier  : {role.nom} de {role.personnage}")
            if role.personnage is not None:
                # debug_asso = [f"{r.nom} : {repr(r)} dans {r.conteneur.nom}" for r in role.personnage.roles]
                # print(f"debug : role à retirer = {role.nom} : {repr(role)}, personnage.roles = {debug_asso}")

                with contextlib.suppress(Exception):
                    role.personnage.roles.remove(role)
                # role.personnage.roles.remove(role)

                del role
        # self.roles.clear()

        # effacer toutes les scènes de l'intrigue
        self.scenes.clear()
        # print(f"intrigue effacée {self.nom}")
        self.error_log.clear()

    # def effacer_roles_issus_de_factions(self):
    #     roles_a_effacer = [role for role in self.rolesContenus.values() if role.issu_dune_faction]
    #     for role in roles_a_effacer:
    #         # print(f"Role à dissocier  : {role.nom} de {role.personnage}")
    #         if role.personnage is not None:
    #             debug_asso = [f"{r.nom} : {repr(r)} dans {r.conteneur.nom}" for r in role.personnage.roles]
    #             print(f"debug : role à retirer = {role.nom} : {repr(role)}, personnage.roles = {debug_asso}")
    #
    #             with contextlib.suppress(Exception):
    #                 role.personnage.roles.remove(role)
    #             # role.personnage.roles.remove(role)
    #
    #             del role
    # #todo : effacer les scènes, effacer les liens roles-scène, effacer les liens roles-conteneurs

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
                        # print(f"dernières mises à jour : ma_scene : {ma_scene.derniere_mise_a_jour} /
                        # sa_scène : {sa_scene.derniere_mise_a_jour}")
                        ma_scene.derniere_mise_a_jour = sa_scene.derniere_mise_a_jour
                        ma_scene.modifie_par = sa_scene.modifie_par
                        # print(f"et, après update : ma_scene : {ma_scene.derniere_mise_a_jour}
                        # / sa_scène : {sa_scene.derniere_mise_a_jour}")
                    elif verbal:
                        print("mais pas la même description !")
                    break


# personnage
class Personnage(ConteneurDeScene):
    def __init__(self, nom="personnage sans nom", concept="", driver="", description="", questions_ouvertes="",
                 sexe="i", pj: TypePerso = TypePerso.EST_PJ, orga_referent=None, pitch_joueur="",
                 indications_costume="",
                 textes_annexes="", url="", last_processing=None,
                 dates_clefs="", forced=False,
                 derniere_edition_fichier=0):
        # last_change = datetime.datetime(year=2000, month=1, day=1), retiré du constructeur
        super(Personnage, self).__init__(derniere_edition_fichier=derniere_edition_fichier,
                                         url=url,
                                         last_processing=last_processing
                                         )
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
        self.orga_referent = orga_referent if orga_referent is not None else ""
        self.interpretes = {}
        self.pitchJoueur = pitch_joueur
        self.indicationsCostume = indications_costume
        self.factions = []  # todo : supprimer
        self.groupes = []
        self.datesClefs = dates_clefs
        self.textesAnnexes = textes_annexes
        self.forced = forced
        self.commentaires = []
        self.informations_evenements = set()
        self.intervient_comme = set()

    def clear(self):
        for role in self.roles:
            role.personnage = None
        self.roles.clear()

    def clear_roles_hors_factions(self):
        to_clear = [role for role in self.roles if not role.issu_dune_faction]
        for role in to_clear:
            self.roles.remove(role)
        # print(f"debug : apres avoir retiré les roles non issus de factions, mes roles contenaient : "
        #       f"{[r.nom for r in self.roles]}")

    def clear_roles_issus_de_factions(self):
        to_clear = [role for role in self.roles if role.issu_dune_faction]
        for role in to_clear:
            self.roles.remove(role)
        # print(f"debug : apres avoir retiré les roles issus de factions, mes roles contenaient : "
        #       f"{[r.nom for r in self.roles]}")

    def ajouter_role(self, r):
        self.roles.add(r)

    def ajouter_commentaires(self, commentaires: list):
        self.commentaires.extend(commentaires)

    # def __str__(self):
    #     return "nom personnage : " + self.nom

    def get_type_from_roles(self):
        tous_les_types = [role.pj for role in self.roles] + \
                         [TypePerso.EST_PNJ_HORS_JEU] if self.est_un_pnj() else [TypePerso.EST_PJ]
        if len(self.intervient_comme) + len(self.informations_evenements) > 0:
            tous_les_types.append(TypePerso.EST_PNJ_TEMPORAIRE)
        return max(tous_les_types)

    def string_type_personnage(self):
        return string_type_pj(self.get_type_from_roles())

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
        to_return += f"orgaReferent = {self.orga_referent} \n"
        to_return += f"interprète(s) = {self.interpretes.values()} \n"
        to_return += f"pitchJoueur = {self.pitchJoueur} \n"
        to_return += f"indicationsCostume = {self.indicationsCostume} \n"
        # to_return += f"factions = {self.factions} \n"
        to_return += f"textesAnnexes = {self.textesAnnexes} \n"
        return to_return

    def est_un_pnj(self):
        # return self.pj == TypePerso.EST_PNJ_HORS_JEU
        # or self.pj == EST_PNJ_TEMPORAIRE or self.pj == EST_PNJ_INFILTRE or self.pj == EST_PNJ_PERMANENT
        return est_un_pnj(self.pj)

    def est_un_pj(self):
        # return self.pj == EST_PJ
        return est_un_pj(self.pj)

    def sommer_pip_perso(self):
        return sum(role.sommer_pip() for role in self.roles)

    def get_tableau_pips(self):
        return [role.sommer_pip() for role in self.roles if role.sommer_pip() != 0]

    # def string_type_pj(self):
    #     return string_type_pj(self.pj)

    def toutes_les_apparitions(self):
        toutes = [role.conteneur.nom for role in self.roles]
        return ', '.join(toutes)

    def str_recap_intrigues(self):
        tab_intrigues = []
        for role in self.roles:
            if isinstance(role.conteneur, Personnage):
                continue

            dict_tmp = {
                'nom_conteneur': role.conteneur.nom,
                'url_conteneur': role.conteneur.url,
                'description': role.description,
                'pips': role.sommer_pip(),
            }
            tab_intrigues.append(dict_tmp)

        tab_intrigues = sorted(tab_intrigues, key=lambda x: x['pips'], reverse=True)

        to_return = "Implications dans les intrigues : \n"
        for intrigue in tab_intrigues:
            to_return += f"{intrigue['nom_conteneur']} ({intrigue['url_conteneur']}) \n"
            to_return += f"{intrigue['pips']} points \n"
            to_return += f"{intrigue['description']} \n\n"

        return to_return

    def str_relations(self):
        to_return = ""
        for role in self.roles:
            for relation in role.relations:
                roles_dans_relation, description, est_reciproque = relation.trouver_partenaires(role)
                for role_associe in roles_dans_relation:
                    if role_associe.personnage is None:
                        to_return += f"En relation avec le rôle {role_associe} (sans perso) >> " \
                                     f"{description}"
                    else:
                        to_return += f"En relation avec {role_associe.personnage.nom} >> " \
                                     f"{description}"
                    to_return += "\n" if est_reciproque else "(non réciproque) \n"
        return to_return

    def str_interventions(self):
        to_return = [f"{intervention.implication} "
                     f"dans {intervention.evenement.nom_evenement}"
                     for intervention in self.intervient_comme
                     ]
        return '\n'.join(to_return)

    @staticmethod
    def perso_depuis_dico(dict_perso: dict):
        to_return = Personnage()
        for key in dict_perso:
            key_propre = unidecode(key).replace(" ", "_").lower()
            # print(f"debug : key = {key}, keypropre = {key_propre}, dict_perso[key] = {dict_perso[key]}")
            # if key_propre == "nom" and len(dict_perso[key])==1:
            #         print("debug : erreur : persona vec un nom incompréhensible trouvé")
            #         traceback.print_stack()
            if hasattr(to_return, key_propre):
                setattr(to_return, key_propre, dict_perso[key])
            elif key_propre.startswith("interprete"):
                session = key[len("interprete"):].strip()
                to_return.interpretes[session] = dict_perso[key]
        return to_return


# rôle
class Role:

    def __init__(self, conteneur: ConteneurDeScene = None, personnage=None, nom="rôle sans nom", description="", pipi=0,
                 pipr=0,
                 genre="i",
                 pj: TypePerso = TypePerso.EST_PJ,
                 type_intrigue="", niveau_implication="", perimetre_intervention="", issu_dune_faction=False,
                 pip_globaux=0, affectation="", alias_dans_intrigue=None):
        self.conteneur = conteneur
        self.personnage = personnage
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
        self.sexe = genre
        self.typeIntrigue = type_intrigue
        self.niveauImplication = niveau_implication
        self.scenes = set()
        self.perimetre_intervention = perimetre_intervention
        self.issu_dune_faction = issu_dune_faction
        self.relations = set()
        self.briefs_pnj_pour_evenement = {}  # evenement, brief
        self.infos_pj_pour_evenement = {}  # evenement, brief
        self.interventions = {}  # evenement, intervention
        self.affectation = affectation
        self.alias_dans_intrigue = alias_dans_intrigue

    def __str__(self):
        to_return = ""
        to_return += f"provenance : {self.conteneur.nom}" + "\n"
        to_return += f"nom dans provenance : {self.nom}" + "\n"
        if self.personnage is None:
            to_return += "personnage : aucun" + "\n"
        else:
            to_return += f"personnage : {self.personnage.nom}" + "\n"
        to_return += f"description : {self.description}" + "\n"
        # to_return += "pipr : " + str(self.pipr) + "\n"
        # to_return += "pipi : " + str(self.pipi) + "\n"
        to_return += f"pj : {string_type_pj(self.pj)}" + "\n"
        # to_return += "sexe : " + self.sexe + "\n"
        to_return += f"typeIntrigue : {self.typeIntrigue}" + "\n"
        to_return += f"niveauImplication : {self.niveauImplication}" + "\n"
        return to_return

    def has_alias(self):
        return self.alias_dans_intrigue is not None

    def get_noms_role(self):
        return self.nom

    def get_nom_et_alias(self):
        to_return = f"{self.nom}"
        if self.alias_dans_intrigue:
            for alias in self.alias_dans_intrigue:
                to_return += f"- aka {alias}"

        return to_return

    def get_nom_affectation(self):
        return self.affectation

    def str_avec_perso(self):
        return f"{self.nom} ({self.personnage.nom})" if self.personnage is not None \
            else f"{self.nom} (pas de personnage associé)"

    def ajouter_a_scene(self, scene_a_ajouter):
        self.scenes.add(scene_a_ajouter)
        scene_a_ajouter.roles.add(self)

    def est_un_pnj(self):
        return est_un_pnj(self.pj)

    def est_un_pj(self):
        return est_un_pj(self.pj)

    def est_un_reroll(self):
        return est_un_reroll(self.pj)

    def sommer_pip(self):
        # print(f"je suis en train de sommer {self.nom}")
        self.pip_total = int(self.pip_globaux) + int(self.pipi) + int(self.pipr)
        return self.pip_total


# intrigue
class Intrigue(ConteneurDeScene):

    def __init__(self, url="", nom="intrigue sans nom", description="Description à écrire", pitch="pitch à écrire",
                 questions_ouvertes="", notes="", resolution="", orga_referent="", timeline="", questionnaire=None,
                 last_processing=None,
                 derniere_edition_fichier=0):
        super(Intrigue, self).__init__(derniere_edition_fichier=derniere_edition_fichier, url=url,
                                       last_processing=last_processing)
        self.nom = nom
        self.description = description
        self.pitch = pitch
        self.questions_ouvertes = questions_ouvertes
        self.questionnaire = questionnaire or []
        self.notes = notes
        self.resolution = resolution
        self.orga_referent = orga_referent
        # self.dateModification = datetime.datetime.now() #seul usage dans le projet d'après l'inspecteur, je vire
        # self.url = url
        self.timeline = timeline
        # if last_processing is None:
        #     last_processing = datetime.datetime.now() - datetime.timedelta(days=500 * 365)
        # self.lastProcessing = last_processing

        self.lastFileEdit = derniere_edition_fichier
        self.objets = set()
        self.commentaires = []
        self.codes_evenements_raw = []
        self.evenements = set()

    def __str__(self):
        return self.nom

    def clear(self):
        # retirer l'intrigue du GN > à faire au niveau de l'appel
        super().clear()

        # se séparer de tous les objets
        for objet in self.objets:
            # objet.inIntrigues.remove(self)
            objet.intrigue = None
        # self.objets.clear()

    def ajouter_commentaires(self, commentaires: list):
        self.commentaires.extend(commentaires)

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
            if role.personnage is personnage:
                # ALORs retourner -1 : il est impossible qu'un personnage soit associé à deux rôles différents au
                # sein d'une même intrigue

                texte_erreur = f"lors de la tentative d'associer le role " \
                               f"{role_a_associer.nom} au personnage {personnage.nom} (meilleur choix) : " \
                               f"celui-ci a déjà été automatiquement associé au rôle {role.nom} dans {self.nom}"
                self.add_to_error_log(ErreurManager.NIVEAUX.ERREUR,
                                      texte_erreur,
                                      ErreurManager.ORIGINES.ASSOCIATION_AUTO
                                      )

                if verbal:  # et si on a demandé à ce que la fonction raconte sa vie, on détaille
                    print(texte_erreur)
                return -1
        role_a_associer.personnage = personnage
        # au passage on update le niveau de personnage (surtout utile pour les PNJs), en prenant toujours le max
        # supprimé et remplacé par une méthode dynamique : cela créait un problème si l'intrigue qui
        # définissait le niveau supérieur disparaissant
        # personnage.pj = max(personnage.pj, role_a_associer.pj)
        personnage.roles.add(role_a_associer)
        return 0


# relations
class Relation:
    def __init__(self):
        self.persos_vue_relation = {}  # personnage - voit la relation comme
        self.est_reciproque = True

    @staticmethod
    def creer_relation_bilaterale(perso_a: Role, perso_b: Role, description_a, description_b=None):
        to_return = Relation()
        to_return.persos_vue_relation = {
            perso_a: description_a,
            perso_b: description_a if description_b is None or len(description_b) < 1 else description_b

        }
        to_return.est_reciproque = description_b is None or len(description_b) < 1
        return to_return

    @staticmethod
    def creer_relation_multilaterale(persos: list[Role], description):
        to_return = Relation()
        for perso in persos:
            to_return.persos_vue_relation[perso] = description
        return to_return

    def trouver_partenaires(self, mon_role: Role):
        return [role for role in self.persos_vue_relation if role != mon_role], \
            self.persos_vue_relation[mon_role], \
            self.est_reciproque


# Scènes
class Scene:
    def __init__(self, conteneur, titre, date="TBD", pitch="Pas de description simple", date_absolue: datetime = None,
                 description="Pas de description complète",
                 actif=True):
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
        # faut-il dire que role et personnages héritent l'un de l'autre? Ou bien d'un objet "protagoniste"?
        self.noms_roles_lus = None
        self.derniere_mise_a_jour = datetime.datetime.now()
        self.modifie_par = ""
        # print(f"Je viens de créer la scène {self.titre}, avec en entrée la date {date}")

    def get_date(self):
        return self.date

    def effacer_roles_issus_de_factions(self):
        # print(f"debug : {self.titre} avant effaçage de mes roles, j'avais : {list(self.roles)} ")
        roles_a_effacer = [r for r in self.roles if r.issu_dune_faction]
        for role in roles_a_effacer:
            self.roles.remove(role)
        # print(f"debug : {self.titre} apès effaçage de mes roles, j'ai : {list(self.roles)} ")

    def get_liste_noms_roles(self):
        return [r.nom for r in self.roles]

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
            date_string = f"{date_absolue_calculee.day} {months[date_absolue_calculee.month - 1]} " \
                          f"{date_absolue_calculee.year}"
        else:
            days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            date_string = f"{days[date_absolue_calculee.weekday()]} " \
                          f"{date_absolue_calculee.day} " \
                          f"{months[date_absolue_calculee.month - 1]} " \
                          f"{date_absolue_calculee.year}"
        time_string = f"{date_absolue_calculee.hour}h{date_absolue_calculee.minute}"

        return f"{date_string}, {time_string}"

    def get_formatted_il_y_a(self):
        # print("date/type > {0}/{1}".format(self.date, type(self.date)))
        if (
                type(self.date) != float
                and type(self.date) != int
                and not str(self.date[1:]).isnumeric()
        ):
            # print("la date <{0}> n'est pas un nombre".format(self.date))
            return self.date

        ma_date = float(self.date[1:]) if type(self.date) == str else -1 * self.date

        if ma_date == 0:
            return "Il y a 0 jours"

        date_texte = 'Il y a '
        nb_annees = ma_date // 365
        nb_mois = (ma_date - nb_annees * 365) // 30.5
        nb_jours = ma_date - nb_annees * 365 - nb_mois * 30.5

        if nb_annees > 1:
            date_texte += f"{str(nb_annees)[:-2]} ans, "
        elif nb_annees == 1:
            date_texte += "1 an, "

        if nb_mois > 0:
            date_texte += f"{str(nb_mois)[:-2]} mois, "

        if nb_jours > 1:
            date_texte += f"{str(nb_jours)[:-2]} jours, "
        elif nb_jours > 0:
            date_texte += "1 jour, "
        return date_texte[:-2]  # car meme dans le cadre de jours on a rajouté deux cars ;)

    def ajouter_role(self, role):
        self.roles.add(role)

    def str_pour_squelette(self, date_gn=None):
        to_return = ""

        to_return += f"titre scène : {self.titre} - date  : {self.get_formatted_date(date_gn)} \n"
        str_roles_persos = 'Roles (Perso) : '
        for role in self.roles:
            if role.personnage is None:
                str_roles_persos += f"{role.nom} (pas de personnage affecté) / "
                print(f"$$$$$$$$$$$ J'ai trouvé un role sans perso = {role.nom} "
                      f"dans la scene {self.titre} / {self.conteneur.nom} "
                      f"est_il est factionneux ? {role.issu_dune_faction}")
            else:
                str_roles_persos += f" {role.get_nom_et_alias()} ({role.personnage.nom}) / "
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
            with contextlib.suppress(ValueError):
                float_date = float(self.date)
                date_absolue = date_du_jeu - datetime.timedelta(days=int(float_date) * -1)
                return date_absolue
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
            logging.debug(f"la date {self.date} n'est pas un nombre")
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
    def __init__(self, nom: str = "faction sans nom"):
        self.nom = nom
        self.personnages = set()
        # self.infos_pour_evenements = set()

    def __str__(self):
        list_perso = self.get_noms_persos()
        return f"Faction {self.nom} avec les personnages {list_perso}"

    def get_noms_persos(self):
        return [p.nom for p in self.personnages]


class GN:
    def __init__(self, dict_config=None, ma_version="0.0.0"):
        # def __init__(self,
        #              dossiers_intrigues, dossier_output: str, mode_association=None,
        #              dossiers_pj=None, dossiers_pnj=None, dossiers_evenements=None,
        #              dossiers_objets=None,
        #              id_factions=None, date_gn=None,
        #              id_pjs_et_pnjs=None, fichier_pnjs=None, ma_version="0.0.0"):

        # création des objets nécessaires
        if dict_config is None:
            dict_config = {}
        # self.dictPJs = {}  # idgoogle, personnage
        # self.dictPNJs = {}  # idgoogle, personnage
        self.personnages = {}  # idgoogle, personnage
        self.factions = {}  # nom, Faction
        self.intrigues = {}  # clef : id google
        self.evenements = {}  # clef : id google
        self.objets_de_reference = {}  # clef : id google

        # todo : est-ce que ces variables servent à quelque chose?
        self.oldestUpdateIntrigue = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatePJ = None  # contient al dernière date d'update d'une intrigue dans le GN
        self.oldestUpdatedIntrigue = ""  # contient l'id de la dernière intrigue updatée dans le GN
        self.oldestUpdatedPJ = ""  # contient l'id du dernier PJ updaté dans le GN

        # injection des paramètres du fichier de config
        # self.association_auto = None  # Ne pas utiliser, paramètres à supprimer
        # self.id_factions = None
        # self.dossiers_pnjs = None
        # self.dossiers_pjs = None
        # self.dossier_outputs_drive = None
        # self.dossiers_intrigues = None
        # self.dossiers_objets = None
        # self.dossiers_evenements = None
        # self.date_gn = None
        # self.id_pjs_et_pnjs = None
        # self.fichier_pnjs = None
        # # self.liste_noms_pjs = None
        # # self.liste_noms_pnjs = None
        # self.mode_association = None
        self.version = ma_version

        self.dict_config = dict_config or {}

        # corriger et ajuster le dictionnaire de config
        self.dict_config['mode_association'] = self.dict_config.get('mode_association', self.ModeAssociation.AUTO)

        for dossier in ['dossiers_intrigues',
                        'dossiers_pjs',
                        'dossiers_pnjs',
                        'dossiers_evenements',
                        'dossiers_objets']:
            if not isinstance(self.dict_config.get(dossier, []), list):
                self.dict_config[dossier] = [self.dict_config[dossier]]

        # self.injecter_config(dossiers_intrigues, dossier_output, mode_association, dossiers_pj=dossiers_pj,
        #                      dossiers_evenements=dossiers_evenements, dossiers_objets=dossiers_objets,
        #                      dossiers_pnj=dossiers_pnj, id_factions=id_factions, date_gn=date_gn,
        #                      id_pjs_et_pnjs=id_pjs_et_pnjs, fichier_pnjs=fichier_pnjs)

    def get_dossier_outputs_drive(self):
        return self.dict_config['dossier_output']

    def get_date_gn(self):
        return self.dict_config.get('date_gn', None)

    def get_id_factions(self):
        return self.dict_config.get('id_factions', None)

    def get_id_dossier_archive(self):
        return self.dict_config.get('id_dossier_archive', None)

    def get_dossiers_pnjs(self):
        return self.dict_config.get('dossiers_pnjs', None)

    def get_dossiers_pjs(self):
        return self.dict_config.get('dossiers_pjs', None)

    def get_dossiers_intrigues(self):
        return self.dict_config.get('dossiers_intrigues', None)

    def get_dossiers_objets(self):
        return self.dict_config.get('dossiers_objets', None)

    def get_dossiers_evenements(self):
        return self.dict_config.get('dossiers_evenements', None)

    def get_id_pjs_et_pnjs(self):
        return self.dict_config.get('id_pjs_et_pnjs', None)

    def get_mode_association(self):
        return self.dict_config['mode_association']

    def get_fichier_pnjs(self):
        return self.dict_config.get('fichier_noms_pnjs', None)

    def get_liste_noms_pjs(self):
        return self.dict_config.get('liste_noms_pjs', None)

    def get_prefixe_intrigues(self):
        return self.dict_config['prefixe_intrigues']

    def get_prefixe_evenements(self):
        return self.dict_config['prefixe_evenements']

    def get_prefixe_pjs(self):
        return self.dict_config['prefixe_PJs']

    def get_prefixe_pnjs(self):
        return self.dict_config['prefixe_PNJs']

    def get_prefixe_objets(self):
        return self.dict_config['prefixe_objets']

    class ModeAssociation(IntEnum):
        AUTO = 0
        MANUEL_VIA_FICHES = 1

    # def injecter_config(self,
    #                     dossiers_intrigues, dossier_output, mode_association=None,
    #                     dossiers_pj=None, dossiers_pnj=None, dossiers_evenements=None, dossiers_objets=None,
    #                     id_factions=None,
    #                     date_gn=None, id_pjs_et_pnjs=None, fichier_pnjs=None):
    #
    #     mode_association = mode_association if mode_association is not None else self.ModeAssociation.AUTO
    #     self.mode_association = mode_association
    #     self.id_pjs_et_pnjs = id_pjs_et_pnjs
    #     self.fichier_pnjs = fichier_pnjs
    #     # # self.liste_noms_pjs = liste_noms_pjs
    #     # self.liste_noms_pnjs = noms_pnjs
    #     if isinstance(dossiers_intrigues, list):
    #         self.dossiers_intrigues = dossiers_intrigues
    #     else:
    #         self.dossiers_intrigues = [dossiers_intrigues]
    #
    #     if dossiers_pj is None:
    #         self.dossiers_pjs = None
    #     elif isinstance(dossiers_pj, list):
    #         self.dossiers_pjs = dossiers_pj
    #     else:
    #         self.dossiers_pjs = [dossiers_pj]
    #
    #     if dossiers_pnj is None:
    #         self.dossiers_pnjs = None
    #     elif isinstance(dossiers_pnj, list):
    #         self.dossiers_pnjs = dossiers_pnj
    #     else:
    #         self.dossiers_pnjs = [dossiers_pnj]
    #
    #     if dossiers_evenements is None:
    #         self.dossiers_evenements = None
    #     elif isinstance(dossiers_evenements, list):
    #         self.dossiers_evenements = dossiers_evenements
    #     else:
    #         self.dossiers_evenements = [dossiers_evenements]
    #
    #     if dossiers_objets is None:
    #         self.dossiers_objets = None
    #     elif isinstance(dossiers_objets, list):
    #         self.dossiers_objets = dossiers_objets
    #     else:
    #         self.dossiers_objets = [dossiers_objets]
    #
    #     self.id_factions = id_factions
    #     self.dossier_outputs_drive = dossier_output
    #
    #     self.date_gn = date_gn

    def get_dict_pj(self):
        return {key: self.personnages[key] for key in self.personnages if self.personnages[key].est_un_pj()}

    def get_dict_pnj(self):
        return {key: self.personnages[key] for key in self.personnages if self.personnages[key].est_un_pnj()}

    def lister_toutes_les_scenes(self):
        to_return = []
        for conteneur in list(self.personnages.values()) + list(self.intrigues.values()):
            to_return.extend(iter(conteneur.scenes))
        return to_return

    def ajouter_faction(self, faction: Faction):
        self.factions[faction.nom] = faction

    # def rechercher_faction(self, nom: str) -> Faction:
    #     if nom in self.factions:
    #         return self.factions[nom]
    #     else:
    #         raise ValueError(f"La faction {nom} n'a pas été trouvée")

    def effacer_personnages_forces(self):
        for key_personnage in list(self.personnages.keys()):
            # print(f"personnage = {self.dictPJs[key_personnage].nom}, forced = {self.dictPJs[key_personnage].forced}")
            if self.personnages[key_personnage].forced:
                perso = self.personnages.pop(key_personnage)
                perso.clear()

    # permet de mettre à jour la date d'intrigue la plus ancienne
    # utile pour la serialisation : google renvoie les fichiers dans l'ordre de dernière modif
    # Tant que les modifs dans google sont postérieures à la date de dernière modif > les prendre en compte
    # Après > arréter
    def update_oldest_update(self):
        if pairesDatesIdIntrigues := {
            intrigue.lastProcessing: intrigue.url
            for intrigue in self.intrigues.values()
        }:
            self.oldestUpdateIntrigue = min(pairesDatesIdIntrigues.keys())
            self.oldestUpdatedIntrigue = pairesDatesIdIntrigues[self.oldestUpdateIntrigue]

        if pairesDatesIdPJ := {
            pj.lastProcessing: pj.url for pj in self.personnages.values() if pj.est_un_pj()
        }:
            self.oldestUpdatePJ = min(pairesDatesIdPJ.keys())
            # print(f"oldestdate pj : {self.oldestUpdatePJ} ")
            self.oldestUpdatedPJ = pairesDatesIdPJ[self.oldestUpdatePJ]

    def save(self, filename):
        with open(filename, "wb") as filehandler:
            pickle.dump(self, filehandler)

    def noms_pjs(self):
        # return self.dictPJs.keys()
        return [x.nom for x in self.personnages.values() if x.est_un_pj()]

    def noms_pnjs(self):
        return [x.nom for x in self.personnages.values() if x.est_un_pnj()]

    def noms_personnages(self):
        return [x.nom for x in self.personnages.values()]

    def noms_pjpnjs(self, pj: bool):
        return self.noms_pjs() if pj else self.noms_pnjs()
        # if pj:
        #     return self.liste_noms_pjs()
        # else:
        #     return self.noms_pnjs()

    def associer_pnj_a_roles(self, seuil_alerte=70, verbal=False):
        self.associer_pjpnjrerolls_a_roles(pj="pnj", seuil_alerte=seuil_alerte, verbal=verbal)

    def associer_pj_a_roles(self, seuil_alerte=70, verbal=False):
        self.associer_pjpnjrerolls_a_roles(pj="pj", seuil_alerte=seuil_alerte, verbal=verbal)

    def associer_reroll_a_roles(self, seuil_alerte=70, verbal=False):
        self.associer_pjpnjrerolls_a_roles(pj="reroll", seuil_alerte=seuil_alerte, verbal=verbal)

    def associer_pjpnjrerolls_a_roles(self, pj: str, seuil_alerte=70, verbal=False):
        logging.debug(f"Début de l'association automatique des rôles aux persos. PJ = {pj}")

        if pj == "pj":
            dict_reference = self.get_dict_pj()
            critere_des_roles = est_un_pj
        elif pj == "pnj":
            dict_reference = self.get_dict_pnj()
            critere_des_roles = est_un_pnj
        elif pj == "reroll":
            dict_reference = self.get_dict_pnj()
            critere_des_roles = est_un_reroll
        else:
            raise ValueError(
                f"type pj inconnu : {pj}. Le paramètrea attendu est 'pj', 'pnj', ou 'reroll'.")

        if verbal:
            print(f"pj? {pj}, noms persos = {dict_reference.keys()}")

        # on crée un dictionnaire temporaire nom > pj pour faire les associations
        dict_noms_persos = {perso.nom: perso for perso in dict_reference.values()}

        # Associer les rôles sans passer par la case tableau d'association
        # pour les rôles issus des scènes dans les fiches de PJs
        self.associer_roles_issus_de_pj(dict_noms_persos, dict_reference, seuil_alerte, verbal)

        # faire l'association dans les intrigues à partir du nom de l'intrigue
        # on crée une focntion pour choisir sur quelle valeur on fera les associations
        def nom_association(role: Role):
            if self.get_mode_association() == GN.ModeAssociation.AUTO:
                return role.nom
            if self.get_mode_association() == GN.ModeAssociation.MANUEL_VIA_FICHES:
                return role.affectation
            print("Erreur de mode association")
            return -1

        logging.debug(f"debut de l'association pour {pj}")
        self.associer_roles_issus_dintrigues(dict_noms_persos, nom_association, critere_des_roles, seuil_alerte, verbal)

        logging.debug("Fin de l'association automatique des rôles aux persos")

    def associer_roles_issus_dintrigues(self, dict_noms_persos, nom_association, critere_des_roles, seuil_alerte,
                                        verbal):
        noms_persos = list(dict_noms_persos.keys())

        logging.debug(f"liste des noms sur lesquels sera basée l'association {noms_persos}")
        # pour chaque role contenu dans chaque intrigue, retrouver le nom du pj correspondant
        for intrigue in self.intrigues.values():
            for role in intrigue.rolesContenus.values():
                # on cherche les persos qui correspondent au critère,
                # mais aussi qui ne viennent pas d'une faction : ceux-ci arrivent déjà associés
                if critere_des_roles(role.pj) and not role.issu_dune_faction and len(nom_association(role)) > 1:
                    # print(f"nom du role testé = {role.nom}")
                    # print(f"debug : nom assocaition = {repr(nom_association(role))} pour {repr(role.nom)}")
                    # print(f"debug : nom assoce / noms = {nom_association(role)} / {noms_persos}")
                    score = process.extractOne(nom_association(role), noms_persos)
                    if verbal:
                        print(f"Rôles issus d'intrigues - Pour {nom_association(role)} "
                              f"dans {intrigue.nom}, score = {score}")
                    intrigue.associer_role_a_perso(role_a_associer=role, personnage=dict_noms_persos[score[0]],
                                                   verbal=verbal)

                    if score[1] < seuil_alerte:
                        texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                       f"{nom_association(role)} > personnage : {score[0]} dans {intrigue.nom}"
                        intrigue.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                                  texte_erreur,
                                                  ErreurManager.ORIGINES.ASSOCIATION_AUTO
                                                  )
                        if verbal:
                            # print(f"je paaaaaarle {score[1]}")
                            print(texte_erreur)

    def associer_roles_issus_de_pj(self, dict_noms_persos, dict_reference, seuil_alerte,
                                   verbal):
        noms_persos = list(dict_noms_persos.keys())
        for perso in dict_reference.values():
            # print(f"je suis en train de chercher des roles dans le pj {pj.nom}")
            # print(f"noms de roles trouvés : {pj.rolesContenus}")
            for role in perso.rolesContenus.values():
                if verbal:
                    print(f"je suis en train d'essayer d'associer le rôle {role.nom} issu du personnage {perso.nom}")
                score = process.extractOne(role.nom, noms_persos)
                if verbal:
                    print(f"Rôles issus de pjs - Pour {role.nom} dans {role.conteneur.nom}, score = {score}")
                role.personnage = dict_noms_persos[score[0]]
                role.personnage.roles.add(role)

                if score[1] < seuil_alerte:
                    texte_erreur = f"Association ({score[1]}) - nom rôle : " \
                                   f"{role.nom} > personnage : {score[0]} dans {perso.nom}"
                    perso.add_to_error_log(ErreurManager.NIVEAUX.WARNING,
                                           texte_erreur,
                                           ErreurManager.ORIGINES.ASSOCIATION_AUTO)
                    if verbal:
                        # print(f"je paaaaaarle {score[1]}")
                        print(texte_erreur)

    @staticmethod
    def load(filename, dict_config: dict = None, update_version: bool = True):
        mon_fichier = open(filename, 'rb')
        gn = pickle.load(mon_fichier)
        # on vérifie si la version du Gn est différente de celle du GN, et on update si nécessaire
        if update_version and (
                not hasattr(gn, "version")
                or version.parse(gn.version) < version.parse(VERSION)
        ):
            gn.mettre_a_jour_champs()

        # on met à jour le dictionnaire de configuration s'il est fourni
        if dict_config:
            gn.dict_config = dict_config

        return gn

    # apres une importation recrée
    # tous les liens entre les PJs,
    # les PNJs
    # et les fonctions d'accélération de ré-importations

    def rebuild_links(self, verbal=False):
        self.clear_all_associations()
        self.update_oldest_update()
        self.ajouter_roles_issus_de_factions()
        self.associer_pnj_a_roles()
        self.associer_pj_a_roles()
        self.associer_reroll_a_roles()
        self.ajouter_roles_issues_des_factions_dans_evenement()
        self.associer_pjs_a_evenements()
        self.associer_pnjs_a_evenements()
        self.lier_les_evenements_aux_intrigues()
        self.identifier_incoherences_scenes_evenements()
        self.lier_et_completer_les_objets()
        self.trouver_roles_sans_scenes()

    def lier_et_completer_les_objets(self):
        dict_code_objet_reference = {o.code_objet: o for o in self.objets_de_reference.values()}
        for intrigue in self.intrigues.values():
            for i, objet in enumerate(intrigue.objets):
                code = objet.code.strip()
                # si il y a un code, on vérifie si on a une fiche
                #   si oui, on les associe
                #   sinon, on crée un emplacement
                # si il n'y a pas de code, on crée une fiche dédiée avec un faux code
                if code == "":
                    code = f"objet sans code - I{intrigue.nom.split('-')[0].strip()}-{i}"

                mon_objet = dict_code_objet_reference.get(code)
                if mon_objet is None:
                    url = f"{code}_imported"
                    mon_objet = ObjetDeReference(id_url=url, ajoute_via_forcage=True, code_objet=code)
                    dict_code_objet_reference[code] = mon_objet
                    self.objets_de_reference[url] = mon_objet

                mon_objet.objets_dans_intrigues.add(objet)
        for evenement in self.evenements.values():
            for i, objet in enumerate(evenement.objets):
                code = objet.code.strip()
                # si il y a un code, on vérifie si on a une fiche
                #   si oui, on les associe
                #   sinon, on crée un emplacement
                # si il n'y a pas de code, on crée une fiche dédiée avec un faux code
                if code == "":
                    # code = f"objet sans code - {evenement.nom.split('-')[0].strip()}-{i}"
                    pattern = r'^[A-Za-z]?\d+\s*-(\s*\d+\s*-)?'
                    code = f"objet sans code - E" \
                           f"{re.search(pattern, evenement.nom_evenement)[0][:-1].strip()}" \
                           f"-{i}"

                mon_objet = dict_code_objet_reference.get(code)
                if mon_objet is None:
                    url = f"{code}_imported"
                    mon_objet = ObjetDeReference(id_url=url, ajoute_via_forcage=True, code_objet=code)
                    dict_code_objet_reference[code] = mon_objet
                    self.objets_de_reference[url] = mon_objet

                mon_objet.objets_dans_evenements.add(objet)

    def identifier_incoherences_scenes_evenements(self):
        for intrigue in self.intrigues.values():
            # liste_noms_pjs = [role.personnage.nom
            #                   for role in intrigue.rolesContenus.values() if role.personnage is not None]
            liste_noms_pjs = intrigue.get_noms_personnages_depuis_scenes()
            for evenement in intrigue.evenements:
                liste_noms_evt = [pj.pj.nom for pj in evenement.pjs_concernes_evenement.values() if pj.pj is not None]
                if liste_warnings := [
                    nom for nom in liste_noms_evt if nom not in liste_noms_pjs
                ]:
                    texte_warning = (f"les personnages suivants sont dans un évènement, "
                                     f"mais dans aucune scène de l'intrigue d'origine : "
                                     f"{', '.join(liste_warnings)}")
                    evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                            texte_warning,
                                                            ErreurManager.ORIGINES.ANALYSE_EVENEMENT)

    def ajouter_roles_issues_des_factions_dans_evenement(self, seuil_faction=80):
        # pour chaque faction dans chaque évènement :
        # prendre tous les noms dans la faction
        # ajouter une info_pj pour chaque membre de la faction

        noms_factions = list(self.factions.keys())
        for evenement in self.evenements.values():
            for info_faction in evenement.infos_factions:
                score = process.extractOne(info_faction.nom_faction, noms_factions)
                if score[1] < seuil_faction:
                    texte_erreur = f"La faction ({score[0]}) a été associée au nom lu {info_faction.nom_faction} " \
                                   f"dans l'évènement {evenement.nom_evenement} " \
                                   f"avec une confiance de {score[1]}%"
                    evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                            texte_erreur,
                                                            ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS
                                                            )
                faction_cible = self.factions[score[0]]
                for personnage in faction_cible.personnages:
                    info_a_ajouter = PJConcerneEvenement(personnage.nom,
                                                         infos_a_fournir=info_faction.infos_a_fournir,
                                                         evenement=evenement)
                    evenement.pjs_concernes_evenement[personnage.nom] = info_a_ajouter

    def associer_pjs_a_evenements(self, seuil_nom_roles: int = 80):
        dict_noms_persos = {pj.nom: pj for pj in self.get_dict_pj().values()}
        liste_noms_persos = list(dict_noms_persos.keys())
        for evenement in self.evenements.values():
            for pj_informe in evenement.pjs_concernes_evenement.values():
                score = process.extractOne(pj_informe.nom_pj, liste_noms_persos)
                if score[1] < seuil_nom_roles:
                    texte_erreur = f"Le nom ({pj_informe.nom_pj}) a été associé au personnage {score[0]} " \
                                   f"dans l'évènement {evenement.nom_evenement} " \
                                   f"avec une confiance de {score[1]}%"
                    evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                            texte_erreur,
                                                            ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS
                                                            )
                pj_cible = dict_noms_persos[score[0]]
                pj_cible.informations_evenements.add(pj_informe)
                pj_informe.pj = pj_cible

    def associer_pnjs_a_evenements(self, seuil_nom_roles=80):
        dict_noms_persos = {pnj.nom: pnj for pnj in self.get_dict_pnj().values()}
        liste_noms_persos = list(dict_noms_persos.keys())
        for evenement in self.evenements.values():
            for intervenant in evenement.intervenants_evenement.values():
                score = process.extractOne(intervenant.nom_pnj, liste_noms_persos)
                if score[1] < seuil_nom_roles:
                    texte_erreur = f"Le nom ({intervenant.nom_pnj}) a été associé au personnage {score[0]} " \
                                   f"dans l'évènement {evenement.nom_evenement} " \
                                   f"avec une confiance de {score[1]}%"
                    evenement.erreur_manager.ajouter_erreur(ErreurManager.NIVEAUX.WARNING,
                                                            texte_erreur,
                                                            ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS
                                                            )
                pnj_cible = dict_noms_persos[score[0]]
                pnj_cible.intervient_comme.add(intervenant)
                intervenant.pnj = pnj_cible

    def lier_les_evenements_aux_intrigues(self):
        dict_ref_evenement = {evt.code_evenement: evt for evt in self.evenements.values()}
        for intrigue in self.intrigues.values():
            for code_evt in intrigue.codes_evenements_raw:
                mon_evenement = dict_ref_evenement.get(code_evt)
                if mon_evenement is None:
                    texte_erreur = f"impossible de trouver une fiche évènement pour le code {code_evt}"
                    intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.ERREUR,
                                                      texte_erreur,
                                                      ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS
                                                      )
                    continue
                intrigue.evenements.add(mon_evenement)
                mon_evenement.intrigue = intrigue
                # print(f"debug : intrigue : {intrigue.nom}, code evenement : {code_evt}")

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
    # si oui (indice de confiance suffisant) > ne rien faire
    # si non > ajouter un nouveau role avec une propriété issu_dune_faction= true
    def ajouter_roles_issus_de_factions(self, seuil_nom_faction=85, seuil_reconciliation_role=80, verbal: bool = False):
        # lire toutes les scènes pours trouver les factions
        for intrigue in self.intrigues.values():
            for scene in intrigue.scenes:
                # identification de la faction à convoquer, en rapprochant son nom de ceux enregistrés
                for nom_faction in scene.nom_factions:
                    # quand on trouve une faction on cherche dans le GN le bon nom
                    logging.debug(f"nom_faction, self.factions = {nom_faction}, {self.factions.keys()}")
                    score_faction = process.extractOne(nom_faction, self.factions.keys())
                    logging.debug(f"score_faction = {score_faction}")
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

                        if len(scene.roles) > 1:
                            noms_roles_dans_scene = scene.get_liste_noms_roles()
                            score_role = process.extractOne(personnage_dans_faction.nom, noms_roles_dans_scene)
                            # print(f"debug : scene : {scene.titre} / {noms_roles_dans_scene} / {score_role}")
                            if score_role[1] >= seuil_reconciliation_role:
                                # dans ce cas, le role est déjà présent dans la scène, ne rien faire
                                continue

                        # du coup on est dans le cas ou on n'a pas trouvé le rôle :
                        # il faut ajouter un nouveau role, issu d'une faction
                        texte_info = f"{personnage_dans_faction.nom} " \
                                     f"a été ajouté via la faction {nom_faction} " \
                                     f"pour la scène {scene.titre} \n"
                        intrigue.error_log.ajouter_erreur(ErreurManager.NIVEAUX.INFO,
                                                          texte_info,
                                                          ErreurManager.ORIGINES.FACTION
                                                          )

                        # ajouter un nouveau role dans l'intrigue avec personnage_dans_faction = true
                        # et réaliser l'association
                        role_a_ajouter = Role(intrigue,
                                              nom=personnage_dans_faction.nom,
                                              description=f"Role ajouté via la faction {nom_faction}",
                                              issu_dune_faction=True,
                                              personnage=personnage_dans_faction
                                              )
                        personnage_dans_faction.roles.add(role_a_ajouter)

                        # l'ajouter à la scène
                        role_a_ajouter.ajouter_a_scene(scene)

    # utilisée pour préparer l'association roles/persos
    # l'idée est qu'avec la sauvegarde les associations restent, tandis que si les pj/pnj ont bougé ca peut tout changer
    # nettoie aussi toutes les erreurs qui peuvent apparaitre durant l'association,
    # pour que celles qui restent soient celles d'actualité
    def clear_all_associations(self):
        # nettoyer les factions

        # casser toutes les associations entre les persos issus de factions et leurs personnages
        tous_les_roles = self.lister_tous_les_roles()
        for role in tous_les_roles:
            if role.issu_dune_faction and role.personnage is not None:
                role.personnage.roles.remove(role)
                role.personnage = None

        # oter les persos issus de fation de toutes les scènes
        toutes_scene = self.lister_toutes_les_scenes()
        for scene in toutes_scene:
            scene.effacer_roles_issus_de_factions()

        for perso in self.lister_tous_les_persos():
            perso.clear_roles_hors_factions()
            # perso.roles.clear()
            perso.error_log.clear(ErreurManager.ORIGINES.ASSOCIATION_AUTO)
            perso.error_log.clear(ErreurManager.ORIGINES.FACTION)

        for intrigue in self.intrigues.values():
            # intrigue.clear_error_log()
            for role in intrigue.rolesContenus.values():
                if not role.issu_dune_faction:
                    role.personnage = None
            # intrigue.effacer_roles_issus_de_factions()

            intrigue.error_log.clear(ErreurManager.ORIGINES.ASSOCIATION_AUTO)
            intrigue.error_log.clear(ErreurManager.ORIGINES.FACTION)
            intrigue.error_log.clear(ErreurManager.ORIGINES.PERSOS_SANS_SCENE)
            intrigue.error_log.clear(ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS)

        for evenement in list(self.evenements.values()):
            evenement.erreur_manager.clear(ErreurManager.ORIGINES.ASSOCIATION_EVENEMENTS)
            evenement.erreur_manager.clear(ErreurManager.ORIGINES.ANALYSE_EVENEMENT)

        for intrigue in self.intrigues.values():
            for evenement in intrigue.evenements:
                evenement.intrigue = None
            intrigue.evenements.clear()

        objets = list(self.objets_de_reference.values())
        for objet_de_reference in objets:
            # print(f"debug : objref : {objet_de_reference} /"
            #       f" {objet_de_reference.ajoute_via_forcage} /"
            #       f" {objet_de_reference.id_url}")
            if objet_de_reference.ajoute_via_forcage:
                objet_de_reference.clear()
                self.objets_de_reference.pop(objet_de_reference.id_url)

    def forcer_import_pjs(self, dicts_pjs_lus: list[dict], suffixe="_imported", verbal=False):
        return self.forcer_import_pjpnjs(dicts_perso_lu=dicts_pjs_lus, pj=True, suffixe=suffixe, verbal=verbal)

    def forcer_import_pnjs(self, dicts_pnjs_lus: list[dict], suffixe="_imported", verbal=False):
        return self.forcer_import_pjpnjs(dicts_perso_lu=dicts_pnjs_lus, pj=False, suffixe=suffixe, verbal=verbal)

    def forcer_import_pjpnjs(self, dicts_perso_lu: list[dict], pj: bool, suffixe="_imported", verbal=False):
        """
        Force l'importation des personnages sans fiche à partir d'une liste de dictionnaires.

        Cette méthode vérifie si les personnages sont déjà présents dans la liste des personnages actifs,
        sinon elle crée une nouvelle instance de la classe Personnage avec les données minimales et l'ajoute
        à la liste des personnages actifs. Le nom du personnage importé est ajouté à la liste des noms présents
        pour se souvenir qu'il a été généré.

        Args:
            dicts_perso_lu (list[dict]): Liste de dictionnaires représentant les personnages à importer.
            pj (bool): Indique si les personnages sont des PJs (True) ou des PNJs (False).
            suffixe (str, optional): Un suffixe à ajouter au nom du personnage lors de l'importation. Par défaut "_imported".
            verbal (bool, optional): Si True, imprime des messages détaillant le processus d'importation. Par défaut False.

        Returns:
            None
        """
        # on commence par reconstruire la table des référents et l'ajuster si nécessaire
        # if table_orgas_referent is None:
        #     table_orgas_referent = []
        #
        # if len(noms_persos) > len(table_orgas_referent):
        #     table_orgas_referent.extend([None] * (len(noms_persos) - len(table_orgas_referent)))
        #     # table_orgas_referent = [None for _ in range(len(noms_persos))]
        logging.debug("début de l'ajout des personnages sans fiche")
        # nomsLus = [x.nom for x in self.dictPJs.values()]

        # if pj:
        #     dict_actif = self.dictPJs
        # else:
        #     dict_actif = self.dictPNJs
        noms_deja_presents = self.noms_pjpnjs(pj)
        logging.debug(f"noms présents avant forçage dans le GN = {noms_deja_presents} pour pj = {pj}")
        # pour chaque personnage de ma liste :
        # SI son nom est dans les persos > ne rien faire
        # SINON, lui créer une coquille vide

        valeur_pj = TypePerso.EST_PJ if pj else TypePerso.EST_PNJ_HORS_JEU

        for dict_perso in dicts_perso_lu:
            if 'pj' not in dict_perso:
                dict_perso['pj'] = valeur_pj

            nom_perso = dict_perso["Nom"]
            # for nom_perso, orga_referent in zip(dicts_perso_lu, table_orgas_referent):
            # print(f"personnage zippé = {nom_perso}, orgazippé = {orga_referent}")
            if nom_perso in noms_deja_presents and verbal:
                print(f"le personnage {nom_perso} a une correspondance dans les persos déjà présents")
            else:
                score_proche = process.extractOne(nom_perso, noms_deja_presents)
                # print(f"avant association, {personnage} correspond à {score_proche[0]} à {score_proche[1]}%")
                if score_proche is not None and score_proche[1] >= 75:
                    if verbal:
                        print(f"{nom_perso} correspond à {score_proche[0]} à {score_proche[1]}%")
                    # donc on ne fait rien
                else:
                    if verbal:
                        print(f"{nom_perso} a été créé (coquille vide)")
                    # self.personnages[nom_perso + suffixe] = Personnage(nom=nom_perso,
                    #                                                    pj=valeur_pj,
                    #                                                    forced=True,
                    #                                                    orga_referent=dict_perso.get("Orga référent", None)
                    #                                                    )
                    self.personnages[nom_perso + suffixe] = Personnage.perso_depuis_dico(dict_perso)
                    # on met son nom en clef pour se souvenir qu'il a été généré

    def lister_tous_les_persos(self):
        return list(self.personnages.values())

    def lister_tous_les_roles(self):
        tous_les_roles = []
        for scene in self.lister_toutes_les_scenes():
            tous_les_roles.extend(scene.roles)
        return tous_les_roles

    # def mettre_a_jour_champs(self):
    # # mise à jour des formats de date et des factions
    # if not hasattr(self, 'factions'):
    #     self.factions = {}
    # # if not hasattr(self, 'id_factions'):
    # #     self.id_factions = None
    # if hasattr(self, 'liste_noms_pjs'):
    #     delattr(self, 'liste_noms_pjs')
    # if hasattr(self, 'liste_noms_pnjs'):
    #     delattr(self, 'liste_noms_pnjs')
    # # if not hasattr(self, 'id_pjs_et_pnjs'):
    # #     self.id_pjs_et_pnjs = None
    # if not hasattr(self, 'evenements'):
    #     self.evenements = {}
    # # if not hasattr(self, 'dossiers_evenements'):
    # #     self.dossiers_evenements = []
    # # if hasattr(self, 'dossier_evenements'):
    # #     delattr(self, 'dossier_evenements')
    # if not hasattr(self, 'objets'):
    #     self.objets = {}
    # if hasattr(self, 'association_auto'):
    #     delattr(self, 'association_auto')
    # # if not hasattr(self, 'mode_association'):
    # #     self.mode_association = self.ModeAssociation.AUTO
    # if hasattr(self, 'dictPJs') and hasattr(self, 'dictPNJs'):
    #     self.personnages = self.dictPJs | self.dictPNJs
    #     delattr(self, 'dictPJs')
    #     delattr(self, 'dictPNJs')
    # if not hasattr(self, 'version'):
    #     self.version = VERSION
    # if hasattr(self, 'date_self'):
    #     delattr(self, 'date_self')
    # if hasattr(self, 'association_auto'):
    #     delattr(self, 'association_auto')
    # if hasattr(self, 'id_factions'):
    #     delattr(self, 'id_factions')
    # if hasattr(self, 'dossiers_pnjs'):
    #     delattr(self, 'dossiers_pnjs')
    # if hasattr(self, 'dossiers_pjs'):
    #     delattr(self, 'dossiers_pjs')
    # if hasattr(self, 'dossier_outputs_drive'):
    #     delattr(self, 'dossier_outputs_drive')
    # if hasattr(self, 'dossiers_intrigues'):
    #     delattr(self, 'dossiers_intrigues')
    # if hasattr(self, 'dossiers_objets'):
    #     delattr(self, 'dossiers_objets')
    # if hasattr(self, 'dossiers_evenements'):
    #     delattr(self, 'dossiers_evenements')
    # if hasattr(self, 'date_gn'):
    #     delattr(self, 'date_gn')
    # if hasattr(self, 'id_pjs_et_pnjs'):
    #     delattr(self, 'id_pjs_et_pnjs')
    # if hasattr(self, 'fichier_pnjs'):
    #     delattr(self, 'fichier_pnjs')
    # if hasattr(self, 'mode_association'):
    #     delattr(self, 'mode_association')
    # if not hasattr(self, 'dict_config'):
    #     self.dict_config = None
    #
    # for scene in self.lister_toutes_les_scenes():
    #     if not hasattr(scene, 'date_absolue'):
    #         scene.date_absolue = None
    #     # print(f"la scène {scene.titre}, dateba absolue = {scene.date_absolue}")
    #     if hasattr(scene, 'niveau'):
    #         delattr(scene, 'niveau')
    #
    # for intrigue in self.intrigues.values():
    #     for objet in intrigue.objets:
    #         if not hasattr(objet, 'code'):
    #             objet.code = ""
    #         if hasattr(objet, 'rfid'):
    #             delattr(objet, 'rfid')
    #         if hasattr(objet, 'commentaires'):
    #             delattr(objet, 'commentaires')
    #         if hasattr(objet, 'objet_de_reference'):
    #             delattr(objet, 'objet_de_reference')
    #         if not hasattr(objet, 'intrigue'):
    #             objet.intrigue = None
    #         if hasattr(objet, 'inIntrigues'):
    #             if len(objet.inIntrigues) > 0:
    #                 objet.intrigue = list(objet.inIntrigues)[0]
    #             delattr(objet, 'inIntrigues')
    #
    #     if not hasattr(intrigue, 'commentaires'):
    #         intrigue.commentaires = []
    #     if not hasattr(intrigue, 'codes_evenements_raw'):
    #         intrigue.codes_evenements_raw = []
    #     if not hasattr(intrigue, 'evenements'):
    #         intrigue.evenements = set()
    #     if not hasattr(intrigue, 'questionnaire'):
    #         intrigue.questionnaire = []
    #     if isinstance(intrigue.questionnaire, str):
    #         intrigue.questionnaire = []
    #
    # # for conteneur in list(self.dictPJs.values()) + list(self.dictPNJs.values()) + list(self.intrigues.values()):
    # #     for role in conteneur.rolesContenus.values():
    # for role in self.lister_tous_les_roles():
    #     print(f"clefs (2) pour {role.nom} = {vars(role).keys()}")
    #     if not hasattr(role, 'affectation'):
    #         role.affectation = ""
    #     if hasattr(role, 'perimetreIntervention'):
    #         if not hasattr(role, 'perimetre_intervention'):
    #             role.perimetre_intervention = role.perimetreIntervention
    #         delattr(role, 'perimetreIntervention')
    #         # print(f"PerimetreIntervention supprimé pour {role.nom}")
    #
    #     if hasattr(role, 'perimetre_Intervention'):
    #         if not hasattr(role, 'perimetre_intervention'):
    #             role.perimetre_intervention = role.perimetre_Intervention
    #         delattr(role, 'perimetre_Intervention')
    #     if not hasattr(role, 'relations'):
    #         role.relations = set()
    #     if not hasattr(role, 'personnage'):
    #         if hasattr(role, 'perso'):
    #             role.personnage = role.perso
    #             delattr(role, 'perso')
    #         else:
    #             role.personnage = None
    #     if not hasattr(role, 'affectation'):
    #         role.affectation = None
    #
    # for scene in self.lister_toutes_les_scenes():
    #     if not hasattr(scene, 'infos'):
    #         scene.infos = set()
    #
    # # for pnj in self.dictPNJs.values():
    # #     if not hasattr(pnj, 'commentaires'):
    # #         pnj.commentaires = []
    # #
    # # for pj in self.dictPJs.values():
    # #     if not hasattr(pj, 'commentaires'):
    # #         pj.commentaires = []
    #
    # for p in self.personnages.values():
    #     if not hasattr(p, 'commentaires'):
    #         p.commentaires = []
    #
    # for evenement in self.evenements.values():
    #     for intervention in evenement.interventions:
    #         if not hasattr(intervention, "liste_pnjs_impliques"):
    #             intervention.liste_pnjs_impliques = set()
    #
    #         if not hasattr(intervention, 'liste_pjs_impliques'):
    #             intervention.liste_pjs_impliques = set()
    #
    #         if hasattr(intervention, 'noms_pj_impliques'):
    #             intervention.noms_pjs_impliques = intervention.pj_impliques
    #             delattr(intervention, 'pj_impliques')
    #
    #     if not hasattr(evenement, 'objets'):
    #         evenement.objets = set()
    #     if not hasattr(evenement, 'heure_de_fin'):
    #         evenement.heure_de_fin = ""
    #
    # # for pj in self.dictPJs:
    # #     if pj in self.dictPNJs:
    # #         self.dictPJs.pop(pj)
    # #         print(f"le personnage {self.dictPJs[pj].name} a été retiré car c'était un pnj")
    #
    # for personnage in list(self.personnages.values()):
    #     if not hasattr(personnage, 'informations_evenements'):
    #         personnage.informations_evenements = set()
    #     if not hasattr(personnage, 'intervient_comme'):
    #         personnage.intervient_comme = set()
    #     if hasattr(personnage, 'factions'):
    #         personnage.groupes = []
    #         personnage.groupes.extend(personnage.factions)
    #         delattr(personnage, 'factions')
    #     if hasattr(personnage, "orgaReferent"):
    #         personnage.orga_referent = personnage.orgaReferent
    #         delattr(personnage, "orgaReferent")
    #
    # for objet_de_reference in self.objets.values():
    #     if not hasattr(objet_de_reference, 'ajoute_via_forcage'):
    #         objet_de_reference.ajoute_via_forcage = True
    #
    #     if not hasattr(objet_de_reference, 'objets_dans_evenements'):
    #         objet_de_reference.objets_dans_evenements = set()

    def mettre_a_jour_champs(self):
        # nouvelle méthode : déclaration du dictionnaire de renommage
        renommages = {GN:
                          {'objets': 'objets_de_reference'},
                      Personnage:
                          {"orgaReferent": "orga_referent",
                           "joueurs": "interpretes"},
                      Intrigue:
                          {'orgaReferent': 'orga_referent'},
                      Intervention:
                          {'heure': 'heure_debut'}
                      }

        # déclaration de la méthode de mise à jour
        def maj_classe(objet_a_maj):
            reference = vars(type(objet_a_maj)())
            current = vars(objet_a_maj)
            # mettre à jour les noms si dans le dictionnaire il y a un nom correspondant
            if dict_renommage := renommages.get(type(objet_a_maj)):
                print(f"debug : dict_renommage :  {dict_renommage}")
                for old_attr, new_attr in dict_renommage.items():
                    if hasattr(objet_a_maj, old_attr):
                        valeur_cible = current[old_attr]
                        print(f"debug : l'objet {type(objet_a_maj)} a bien un champ {old_attr} qui vaut {valeur_cible}")
                        setattr(objet_a_maj, new_attr, valeur_cible)
                        delattr(objet_a_maj, old_attr)
            # ajouter les nouveaux champs
            for ref_attr, ref_value in reference.items():
                if not hasattr(objet_a_maj, ref_attr):
                    setattr(objet_a_maj, ref_attr, ref_value)
            # supprimer les champs superflus
            old_attrs = list(current.keys())
            for old_attr in old_attrs:
                if old_attr not in reference:
                    delattr(objet_a_maj, old_attr)

        # parcours de toutes les classes pour mettre à jour les Objets

        maj_classe(self)

        for personnage in self.personnages.values():
            maj_classe(personnage)
            for role in personnage.roles:
                maj_classe(role)

        for faction in self.factions.values():
            maj_classe(faction)

        for intrigue in self.intrigues.values():
            maj_classe(intrigue)

        for evenement in self.evenements.values():
            maj_classe(evenement)
            for intervention in evenement.interventions:
                maj_classe(intervention)

        for objet in self.objets_de_reference.values():
            maj_classe(objet)

        self.version = VERSION


# if hasattr(personnage, "orgaReferent"):
#     personnage.orga_referent = personnage.orgaReferent
#     delattr(personnage, "orgaReferent")


# objets

class Objet:
    def __init__(self, code="", description="", fourni_par="Inconnu", emplacement_debut="", special_effect=""):
        self.description = description
        self.fourniParJoueur = fourni_par
        self.emplacementDebut = emplacement_debut
        self.specialEffect = special_effect
        self.code = code
        self.inIntrigues = set()  # ne pas utiliser, ici pour des besoins de rétro-compatibilité
        self.intrigue = None
        # self.objet_de_reference=None

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
        ASSOCIATION_EVENEMENTS = 5
        CHRONO_EVENEMENT = 6
        LECTURE_EVENEMENT = 7
        ANALYSE_EVENEMENT = 8

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
        return len([e for e in self.erreurs if e.niveau >= ErreurManager.NIVEAUX.WARNING])

    def ajouter_erreur(self, niveau: NIVEAUX, message, origine: ORIGINES):
        self.erreurs.append(self.ErreurAssociation(niveau, message, origine))

    def __str__(self):
        return '\n'.join([str(erreur) for erreur in self.erreurs])

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


class Evenement:
    def __init__(
            self,
            id_url="",
            nom_evenement="",
            code_evenement="",
            referent="",
            etat="",
            intrigue_liee="",
            lieu="",
            date="",
            heure_de_demarrage="",
            heure_de_fin="",
            declencheur="",
            consequences_evenement="",
            synopsis="",
            derniere_edition_date=None,
            derniere_edition_par=""
    ):
        self.nom_evenement = nom_evenement
        self.id_url = id_url
        self.derniere_edition_date = derniere_edition_date
        self.derniere_edition_par = derniere_edition_par
        self.code_evenement = code_evenement
        self.referent = referent
        self.etat = etat
        self.intrigue_liee = intrigue_liee
        self.lieu = lieu
        self.date = date
        self.heure_de_demarrage = heure_de_demarrage
        self.heure_de_fin = heure_de_fin
        self.declencheur = declencheur
        self.consequences_evenement = consequences_evenement
        self.synopsis = synopsis
        #         self.objets = []
        self.interventions = []
        self.intervenants_evenement = {}  # nom, intervenant
        self.pjs_concernes_evenement = {}  # nom, pj_concerné
        self.infos_factions = []
        if derniere_edition_date is None:
            derniere_edition_date = datetime.datetime.now() - datetime.timedelta(days=500 * 365)
        self.lastProcessing = derniere_edition_date
        self.erreur_manager = ErreurManager()
        self.intrigue = None
        self.objets = set()

    def get_last_processing(self):
        return self.lastProcessing

    def set_last_processing(self, valeur):
        self.lastProcessing = valeur

    def get_noms_pnjs(self):
        return list(self.intervenants_evenement.keys())

    def get_noms_pjs(self):
        return list(self.pjs_concernes_evenement.keys())

    def clear(self):
        # casser toutes les relations intervenants <> persos
        intervenants_a_nettoyer = self.intervenants_evenement.values()
        for intervenant in intervenants_a_nettoyer:
            if intervenant.pnj is not None:
                intervenant.pnj.intervient_comme.remove(intervenant)
            del intervenant

        # casser toutes les relations pj_concernés <> persos
        for pj_concerne in self.pjs_concernes_evenement.values():
            if pj_concerne.pj is not None:
                pj_concerne.pj.informations_evenements.remove(pj_concerne)
            del pj_concerne

        # effacer toutes les interventions de l'évènement
        # for intervention in self.interventions:
        #     del intervention
        self.interventions.clear()


class IntervenantEvenement:
    def __init__(self, nom_pnj, evenement: Evenement, costumes_et_accessoires="", implication="",
                 situation_de_depart=""):
        self.nom_pnj = nom_pnj
        self.pnj = None
        self.costumes_et_accessoires = costumes_et_accessoires
        self.implication = implication
        self.situation_de_depart = situation_de_depart
        self.evenement = evenement
        self.interventions = set()

    def str_avec_perso(self):
        return f"{self.nom_pnj} ({self.pnj.nom})" if self.pnj is not None \
            else f"{self.nom_pnj} (pas de personnage associé)"

    def str_pour_squelette(self):
        return f"Pour l'évènement {self.evenement.code_evenement}  : \n" \
               f"\t costume : {self.costumes_et_accessoires} \n " \
               f"\t implication : {self.implication} \n " \
               f"\t commence : {self.situation_de_depart}"


class PJConcerneEvenement:
    def __init__(self, nom_pj, evenement: Evenement, infos_a_fournir=""):
        self.nom_pj = nom_pj
        self.pj = None
        self.infos_a_fournir = infos_a_fournir
        self.evenement = evenement

    def str_avec_perso(self):
        return f"{self.nom_pj} ({self.pj.nom})" if self.pj is not None \
            else f"{self.nom_pj} (pas de personnage associé)"

    def str_pour_squelette(self):
        return f"Pour l'évènement {self.evenement.code_evenement} : {self.infos_a_fournir}"


class InfoFactionsPourEvenement:
    def __init__(self, nom_faction, evenement: Evenement, infos_a_fournir=""):
        self.nom_faction = nom_faction
        # self.faction = None
        self.infos_a_fournir = infos_a_fournir
        self.evenement = evenement


class ObjetDansEvenement:
    def __init__(self, code: str, description: str, commence: str, termine: str, evenement: Evenement):
        self.code = code
        self.description = description
        self.commence = commence
        self.termine = termine
        self.evenement = evenement


#  lire les fiches > on lit le tableau > on met dans un dictionnaire > on utilise get pour prendre ce qui nous intéresse
#  les appeler à partir des intrigues dans un tableau 'scène nécessaure / onm évènement)

def _heure_formattee(heure, defaut_si_ko=None):
    try:
        date_obj = dateparser.parse(heure)
        return date_obj.strftime("%Hh%M")
    except Exception:
        return "00h00" if defaut_si_ko is None else heure


class Intervention:
    def __init__(self, evenement: Evenement = None, jour=None, heure_debut=None, heure_fin=None, description=""):
        self.jour = jour
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.liste_intervenants = []
        self.liste_pjs_concernes = []
        self.description = description
        self.evenement = evenement

    def heure_debut_formattee(self, defaut_si_ko=None):
        # try:
        #     date_obj = dateparser.parse(self.heure_debut)
        #     return date_obj.strftime("%Hh%M")
        # except Exception:
        #     return "00h00" if defaut_si_ko is None else self.heure_debut
        return _heure_formattee(self.heure_debut, defaut_si_ko)

    def heure_fin_formattee(self, defaut_si_ko=None):
        # try:
        #     date_obj = dateparser.parse(self.heure_debut)
        #     return date_obj.strftime("%Hh%M")
        # except Exception:
        #     return "00h00" if defaut_si_ko is None else self.heure_debut
        return _heure_formattee(self.heure_fin, defaut_si_ko)

    def jour_formatte(self):
        return f"J{self.jour}" if self.jour.isdigit() else self.jour


class Commentaire:
    def __init__(self, texte: str, auteur: str, destinataires: list[str]):
        self.texte = texte
        self.auteur = auteur
        self.destinataires = set(destinataires)


class ObjetDeReference:
    def __init__(
            self,
            id_url="",
            nom_objet="",
            code_objet="",
            referent="",
            utilite="",
            budget="",
            effets_speciaux="",
            recommandations="",
            materiaux="",
            description="",
            derniere_edition_date=None,
            derniere_edition_par="",
            ajoute_via_forcage=False,
            last_processing=None
    ):
        self.id_url = id_url
        self.nom_objet = nom_objet
        self.code_objet = code_objet
        self.referent = referent
        self.utilite = utilite
        self.budget = budget
        self.recommandations = recommandations
        self.materiaux = materiaux
        self.description = description
        self.derniere_edition_date = derniere_edition_date
        self.derniere_edition_par = derniere_edition_par
        self.objets_dans_intrigues = set()
        self.objets_dans_evenements = set()
        self.ajoute_via_forcage = ajoute_via_forcage
        self.effets_speciaux = effets_speciaux
        self.last_processing = last_processing or datetime.datetime.now() - datetime.timedelta(days=500 * 365)

    def get_last_processing(self):
        return self.last_processing

    def set_last_processing(self, valeur):
        self.last_processing = valeur

    def clear(self):
        for objet in self.objets_dans_intrigues:
            objet.objet_de_reference = None
        for objet in self.objets_dans_evenements:
            objet.objet_de_reference = None
        self.objets_dans_intrigues.clear()
        self.objets_dans_evenements.clear()

    def get_full_url(self):
        return f"https://docs.google.com/document/d/{self.id_url}"
