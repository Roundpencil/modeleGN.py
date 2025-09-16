import os
import configparser
from datetime import datetime
from typing import Iterable, Optional

def creer_configparser(dict_config: dict) -> configparser.ConfigParser:
    """
    Construit un ConfigParser conforme à la doc MAGnet à partir du dict produit par `creer_dict_config`.
    Points clés couverts :
      - Sections [Essentiels] / [Optionnels]
      - Paramètres répétables avec suffixes libres (_XXXX) pour *toutes* les familles listées par la doc
      - Nommage exact des préfixes : prefixe_intrigues / prefixe_evenements / prefixe_objets / prefixe_PJ / prefixe_PNJ
      - Conservation du cas (optionxform = str)
      - Ecriture conditionnelle des Optionnels seulement s'ils existent
    """
    cfg = configparser.ConfigParser()
    cfg.optionxform = str  # conserver la casse des clés (prefixe_PJ, prefixe_PNJ, etc.)
    cfg.add_section('Essentiels')
    cfg.add_section('Optionnels')

    # ----------- ESSENTIELS -----------
    # dossier de sortie
    if dict_config.get('dossier_output'):
        cfg.set('Essentiels', 'dossier_output_squelettes_pjs', str(dict_config['dossier_output']))

    # mode_association: 0 ou 1
    if 'mode_association' in dict_config and dict_config['mode_association'] is not None:
        ma = dict_config['mode_association']
        val = _coerce_mode_association(ma)
        cfg.set('Essentiels', 'mode_association', str(val))

    # nom_fichier_sauvegarde (essentiel)
    if dict_config.get('nom_fichier_sauvegarde'):
        cfg.set('Essentiels', 'nom_fichier_sauvegarde', str(dict_config['nom_fichier_sauvegarde']))

    # id_dossier_intrigues (+ variantes suffixées)
    _write_repeatable_options(
        cfg, dict_config,
        section='Essentiels',
        values_key='dossiers_intrigues',
        names_key='nom_dossiers_intrigues',
        base_option='id_dossier_intrigues'
    )

    # ----------- OPTIONNELS -----------
    # nom_fichier_sauvegarde (local) -> on ne peut écrire que le nom, pas le chemin
    if dict_config.get('dossier_local_fichier_sauvegarde'):
        basename = os.path.basename(str(dict_config['dossier_local_fichier_sauvegarde'])) or '.'
        cfg.set('Optionnels', 'nom_fichier_sauvegarde', basename)

    # Blocs répétables (suffixes libres) : PJs, PNJs, Evénements, Objets, Factions
    _write_repeatable_options(cfg, dict_config, 'Optionnels', 'dossiers_pjs',         'nom_dossiers_pjs',         'id_dossier_pjs')
    _write_repeatable_options(cfg, dict_config, 'Optionnels', 'dossiers_pnjs',        'nom_dossiers_pnjs',        'id_dossier_pnjs')
    _write_repeatable_options(cfg, dict_config, 'Optionnels', 'dossiers_evenements',  'nom_dossiers_evenements',  'id_dossier_evenements')
    _write_repeatable_options(cfg, dict_config, 'Optionnels', 'dossiers_objets',      'nom_dossiers_objets',      'id_dossier_objets')
    # La doc précise que "les mêmes règles s’appliquent" pour id_factions -> répétable aussi
    _write_repeatable_options(cfg, dict_config, 'Optionnels', 'id_factions',          'nom_id_factions',          'id_factions')

    # Fichiers/IDs simples
    if dict_config.get('id_pjs_et_pnjs'):
        cfg.set('Optionnels', 'id_pjs_et_pnjs', str(dict_config['id_pjs_et_pnjs']))

    if dict_config.get('fichier_noms_pnjs'):
        cfg.set('Optionnels', 'nom_fichier_pnjs', str(dict_config['fichier_noms_pnjs']))

    # noms_persos : CSV (ancienne méthode)
    if 'liste_noms_pjs' in dict_config and dict_config['liste_noms_pjs'] is not None:
        v = dict_config['liste_noms_pjs']
        csv_val = ', '.join(map(str, v)) if isinstance(v, (list, tuple)) else str(v)
        cfg.set('Optionnels', 'noms_persos', csv_val)

    # date_gn : conserver la chaîne si on l'a ; sinon ISO
    if dict_config.get('date_gn'):
        v = dict_config['date_gn']
        cfg.set('Optionnels', 'date_gn', v.strftime('%Y-%m-%d') if isinstance(v, datetime) else str(v))

    # Préfixes (noms exacts selon la doc)
    _maybe_set(cfg, 'Optionnels', 'prefixe_intrigues',  dict_config.get('prefixe_intrigues'))
    _maybe_set(cfg, 'Optionnels', 'prefixe_evenements', dict_config.get('prefixe_evenements'))
    _maybe_set(cfg, 'Optionnels', 'prefixe_objets',     dict_config.get('prefixe_objets'))
    # attention : clés exactes demandées par la doc
    _maybe_set(cfg, 'Optionnels', 'prefixe_PJ',         dict_config.get('prefixe_PJs')  or dict_config.get('prefixe_PJ'))
    _maybe_set(cfg, 'Optionnels', 'prefixe_PNJ',        dict_config.get('prefixe_PNJs') or dict_config.get('prefixe_PNJ'))

    # Dossier archive
    _maybe_set(cfg, 'Optionnels', 'id_dossier_archive', dict_config.get('id_dossier_archive'))

    return cfg


# ----------------- Helpers -----------------

def _maybe_set(cfg: configparser.ConfigParser, section: str, key: str, value: Optional[str]) -> None:
    if value is not None:
        cfg.set(section, key, str(value))

def _coerce_mode_association(ma) -> int:
    """Accepte int, enum-like (avec .value), ou str ; renvoie 0/1 (défaut 9 si hors spec)."""
    try:
        return int(getattr(ma, 'value', ma))
    except (TypeError, ValueError):
        s = str(ma).strip()
        return int(s[0]) if s and s[0].isdigit() else 9

def _as_list(x) -> Optional[list]:
    if x is None:
        return None
    if isinstance(x, (list, tuple)):
        return list(x)
    return [x]

def _write_repeatable_options(
    cfg: configparser.ConfigParser,
    dict_config: dict,
    section: str,
    values_key: str,
    names_key: str,
    base_option: str
) -> None:
    """
    Ecrit une série d'options répétables dans `section`, à partir de :
      - values_key : liste des valeurs (ex: ['id1','id2',...])
      - names_key  : liste des noms d'options d'origine (ex: ['id_dossier_pjs_emeric', ...])
                     ou uniquement des suffixes libres (ex: ['_emeric','_pierre']) si tu préfères.
      - base_option: nom de base (ex: 'id_dossier_pjs')
    Règles :
      - si `names_key` n'est pas fourni ou longueur ≠ valeurs, on génère: base_option (si 1 valeur)
        sinon base_option_1, base_option_2, ...
      - si `names_key` contient des noms complets (commençant par base_option) on les prend tels quels ;
        si `names_key` ne contient que des suffixes, on préfixe avec base_option.
    """
    vals = _as_list(dict_config.get(values_key))
    if not vals:
        return

    raw_names = _as_list(dict_config.get(names_key))
    names: Iterable[str]

    if raw_names and len(raw_names) == len(vals):
        normed = []
        for nm in raw_names:
            nm = str(nm)
            if nm.startswith(base_option):
                normed.append(nm)
            else:
                # autoriser de fournir juste un suffixe ('_emeric' ou 'emeric')
                if nm.startswith('_'):
                    normed.append(base_option + nm)
                else:
                    normed.append(f"{base_option}_{nm}")
        names = normed
    else:
        # Génération simple et stable
        names = [base_option] if len(vals) == 1 else [f"{base_option}_{i+1}" for i in range(len(vals))]

    for name, value in zip(names, vals):
        if value is not None:
            cfg.set(section, name, str(value))
