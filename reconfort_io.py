"""
Base de code fournie -- projet "Robot de reconfort".

Ce module fait DEUX choses, et rien d'autre :

  1. lire les quatre fichiers d'entree (carte, dictionnaire, armoire,
     scenario) ;
  2. construire et exporter le fichier de trace attendu a la sortie.

Tout le reste du projet -- perception, carte mentale, planification de
chemin, consultation du dictionnaire, fouille de l'armoire, boucle de
decision -- est a votre charge. Ne cherchez pas ces fonctions ici : elles
n'y sont pas, et c'est volontaire.

Vous avez le droit de modifier ce fichier. Vous avez surtout le devoir de
le comprendre : les verifications faites ici sont minimales (voir la
section "Ce qui n'est PAS verifie" plus bas), et les validations
manquantes font partie du travail demande.

Python 3.9+. Aucune dependance externe.
"""

from __future__ import annotations

import json
import unicodedata
from collections.abc import Sequence
from pathlib import Path
from typing import Any

__all__ = [
    "ErreurFichier",
    "Trace",
    "charger_armoire",
    "charger_carte",
    "charger_dictionnaire",
    "charger_scenario",
    "normaliser",
]

VERSION_ATTENDUE = 1


class ErreurFichier(Exception):
    """Fichier d'entree absent, illisible, ou d'un type inattendu."""

# ---------------------------------------------------------------------------
# Helpeurs de validation
# ---------------------------------------------------------------------------

def _verifier_champs(donnees: dict, champs_attendus: dict[str, type]) -> None:
    """Verifie la presence et le type des champs obligatoires a la racine."""
    for champ, type_attendu in champs_attendus.items():
        if champ not in donnees:
            raise ErreurFichier(f"Champ obligatoire manquant : '{champ}'")
        if not isinstance(donnees[champ], type_attendu):
            raise ErreurFichier(
                f"Champ '{champ}' de type {type(donnees[champ]).__name__}, "
                f"attendu {type_attendu.__name__}"
            )


def _verifier_limites(pos: list[int], hauteur: int, largeur: int, nom: str) -> None:
    """Verifie qu'une position (ligne, colonne) est dans les limites de la carte."""
    if not isinstance(pos, list) or len(pos) != 2:
        raise ErreurFichier(f"{nom} doit etre une liste de deux entiers (ligne, colonne)")
    ligne, colonne = pos
    if not isinstance(ligne, int) or not isinstance(colonne, int):
        raise ErreurFichier(f"{nom} doit etre une liste de deux entiers (ligne, colonne)")
    if not (0 <= ligne < hauteur) or not (0 <= colonne < largeur):
        raise ErreurFichier(
            f"{nom} {pos} hors limites de la carte "
            f"(hauteur={hauteur}, largeur={largeur})"
        )


# ---------------------------------------------------------------------------
# Vérifications spécifiques par fichier
# ---------------------------------------------------------------------------

def _verifier_carte(donnees: dict) -> None:
    _verifier_champs(donnees, {
        "nom": str,
        "dimensions": dict,
        "legende": dict,
        "grille": list,
        "depart_robot": list,
        "armoire": dict,
        "dictionnaire": dict,
        "residents": list
    })

    h = donnees["dimensions"].get("hauteur")
    l = donnees["dimensions"].get("largeur")
    if not isinstance(h, int) or not isinstance(l, int):
        raise ErreurFichier("dimensions doit contenir des entiers 'hauteur' et 'largeur'")

    grille = donnees["grille"]
    if len(grille) != h:
        raise ErreurFichier(f"grille doit avoir {h} lignes, trouve {len(grille)}")
    for i, ligne in enumerate(grille):
        if len(ligne) != l:
            raise ErreurFichier(f"Grille non rectangulaire : ligne {i} de la grille doit avoir {l} colonnes, trouve {len(ligne)}")

    inv_legende = {v: k for k, v in donnees["legende"].items()}

    entites = [
        ("depart du robot", donnees["depart_robot"]),
        ("armoire", donnees["armoire"].get("position")),
        ("dictionnaire", donnees["dictionnaire"].get("position"))
    ]

    for nom_entite, pos in entites:
        symbole = inv_legende.get(nom_entite)
        if not symbole:
            raise ErreurFichier(f"Legende manquante pour l'entite '{nom_entite}'")
        _verifier_limites(pos, h, l, nom_entite)
        if grille[pos[0]][pos[1]] != symbole:
            raise ErreurFichier(
                f"Position de l'entite '{nom_entite}' {pos} ne correspond pas "
                f"a la grille (symbole attendu '{symbole}', trouve '{grille[pos[0]][pos[1]]}')"
            )

    sym_res = inv_legende.get("resident")
    if not sym_res:
        raise ErreurFichier("Legende manquante pour l'entite 'resident'")

    ids_vus = set()
    for res in donnees["residents"]:
        r_id = res.get("id")
        r_pos = res.get("position")
        if not r_id:
            raise ErreurFichier(f"Resident sans id : {res}")
        if r_id in ids_vus:
            raise ErreurFichier(f"Resident duplique avec id {r_id!r}")
        ids_vus.add(r_id)

        _verifier_limites(r_pos, h, l, f"resident {r_id}")
        if grille[r_pos[0]][r_pos[1]] != sym_res:
            raise ErreurFichier(
                f"Position du resident {r_id} {r_pos} ne correspond pas "
                f"a la grille (symbole attendu '{sym_res}', trouve '{grille[r_pos[0]][r_pos[1]]}')"
            )


def _verifier_armoire(donnees: dict) -> None:
    _verifier_champs(donnees, {
        "nom": str,
        "emotions": list,
        "intensites": list,
        "casier_depart": list,
        "casiers": list
    })

    emotions = donnees["emotions"]
    intensites = donnees["intensites"]
    hauteur_armoire = len(intensites)
    largeur_armoire = len(emotions)

    _verifier_limites(donnees["casier_depart"], hauteur_armoire, largeur_armoire, "casier_depart")

    positions_vues = set()

    for casier in donnees["casiers"]:
        ligne = casier.get("ligne")
        colonne = casier.get("colonne")
        emotion = casier.get("emotion")
        intensite = casier.get("intensite")

        if ligne is None or colonne is None or emotion is None or intensite is None:
            raise ErreurFichier(f"Casier incomplet : {casier}")

        pos = [ligne, colonne]
        _verifier_limites(pos, hauteur_armoire, largeur_armoire, "casier")

        if (ligne, colonne) in positions_vues:
            raise ErreurFichier(f"Casier duplique a la position {pos}")
        positions_vues.add((ligne, colonne))

        if emotions[colonne] != emotion:
            raise ErreurFichier(
                f"Emotion du casier {pos} ({emotion}) ne correspond pas "
                f"a la colonne {colonne} de la liste d'emotions ({emotions[colonne]})"
            )
        if intensites[ligne] != intensite:
            raise ErreurFichier(
                f"Intensite du casier {pos} ({intensite}) ne correspond pas "
                f"a la ligne {ligne} de la liste d'intensites ({intensites[ligne]})"
            )


def _verifier_dictionnaire(donnees: dict) -> None:
    _verifier_champs(donnees, {
        "nom": str,
        "emotions": list,
        "intensites": list,
        "entrees": list
    })

    emotions_connues = set(donnees["emotions"])
    intensites_connues = set(donnees["intensites"])
    mots_vus = set()

    for entree in donnees["entrees"]:
        emotion = entree.get("emotion")
        intensite = entree.get("intensite")
        formes = entree.get("formes", [])

        if emotion not in emotions_connues:
            raise ErreurFichier(f"Emotion inconnue dans dictionnaire : {emotion!r}")
        if intensite not in intensites_connues:
            raise ErreurFichier(f"Intensite inconnue dans dictionnaire : {intensite!r}")

        for mot in formes:
            if mot in mots_vus:
                raise ErreurFichier(f"Mot duplique dans dictionnaire : {mot!r}")
            mots_vus.add(mot)


def _verifier_scenario(donnees: dict) -> None:
    pass # TODO


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def _lire_json(chemin: str | Path, format_attendu: str) -> dict[str, Any]:
    """Lit un fichier JSON UTF-8 et verifie son en-tete."""
    chemin = Path(chemin)
    try:
        texte = chemin.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErreurFichier(f"fichier introuvable : {chemin}") from None
    except UnicodeDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas encode en UTF-8 (octet {err.start})"
        ) from None
    except OSError as err:
        raise ErreurFichier(f"{chemin} illisible : {err}") from None

    try:
        donnees = json.loads(texte)
    except json.JSONDecodeError as err:
        raise ErreurFichier(
            f"{chemin} n'est pas un JSON valide : {err.msg} "
            f"(ligne {err.lineno}, colonne {err.colno})"
        ) from None

    if not isinstance(donnees, dict):
        raise ErreurFichier(
            f"{chemin} : la racine doit etre un objet JSON, "
            f"pas {type(donnees).__name__}"
        )

    format_trouve = donnees.get("format")
    if format_trouve != format_attendu:
        raise ErreurFichier(
            f"{chemin} : format attendu '{format_attendu}', "
            f"trouve {format_trouve!r}"
        )

    version = donnees.get("version")
    if version != VERSION_ATTENDUE:
        raise ErreurFichier(
            f"{chemin} : version {VERSION_ATTENDUE} attendue, trouve {version!r}"
        )

    if format_attendu == "robot-reconfort/carte":
        _verifier_carte(donnees)
    elif format_attendu == "robot-reconfort/dictionnaire":
        _verifier_dictionnaire(donnees)
    elif format_attendu == "robot-reconfort/armoire":
        _verifier_armoire(donnees)
    elif format_attendu == "robot-reconfort/scenario":
        _verifier_scenario(donnees)
    
    return donnees


def charger_carte(chemin: str | Path) -> dict[str, Any]:
    """Charge un fichier carte. Voir l'enonce, section 5.1."""
    return _lire_json(chemin, "robot-reconfort/carte")


def charger_dictionnaire(chemin: str | Path) -> dict[str, Any]:
    """Charge un fichier dictionnaire. Voir l'enonce, section 5.2."""
    return _lire_json(chemin, "robot-reconfort/dictionnaire")


def charger_armoire(chemin: str | Path) -> dict[str, Any]:
    """Charge un fichier armoire. Voir l'enonce, section 5.3."""
    return _lire_json(chemin, "robot-reconfort/armoire")


def charger_scenario(chemin: str | Path) -> dict[str, Any]:
    """Charge un fichier scenario. Voir l'enonce, section 5.4."""
    return _lire_json(chemin, "robot-reconfort/scenario")


# ---------------------------------------------------------------------------
# Normalisation des messages
# ---------------------------------------------------------------------------

def normaliser(texte: str) -> list[str]:
    """Decoupe un message en mots comparables au dictionnaire.

    Minuscules, accents retires, decoupage sur tout ce qui n'est pas une
    lettre. C'est exactement la regle de l'enonce, section 6.1 ;
    reimplementez-la vous-meme si vous travaillez dans un autre langage.

        >>> normaliser("Je suis TERRIFIEE, vraiment !")
        ['je', 'suis', 'terrifiee', 'vraiment']
    """
    decompose = unicodedata.normalize("NFD", texte.lower())
    sans_accents = "".join(
        c for c in decompose if unicodedata.category(c) != "Mn"
    )
    mots: list[str] = []
    courant: list[str] = []
    for caractere in sans_accents:
        if caractere.isalpha():
            courant.append(caractere)
        elif courant:
            mots.append("".join(courant))
            courant = []
    if courant:
        mots.append("".join(courant))
    return mots


# ---------------------------------------------------------------------------
# Ecriture de la trace
# ---------------------------------------------------------------------------

ACTIONS = ("AVANCER", "CONSULTER", "CHERCHER", "PRENDRE", "DONNER", "ATTENDRE")
DIRECTIONS = ("N", "S", "E", "O")
REPLIS = ("aucun", "intensite", "voisine_1", "voisine_2")


class Trace:
    """Accumule les pas et les livraisons, puis ecrit le fichier de sortie.

    Utilisation typique :

        trace = Trace(nom_carte="appartement_01",
                      nom_scenario="scenario_01",
                      equipe=["Dupont", "Martin"])
        ...
        trace.ajouter_pas(demande=1, position=(6, 1), casier=(1, 0),
                          action="AVANCER", argument="E",
                          perception={"N": "libre", "S": "mur",
                                      "E": "libre", "O": "mur"})
        ...
        trace.ajouter_livraison(demande=1, resident="R1",
                                emotion="tristesse", intensite="moyenne",
                                casier_choisi=(1, 4), repli="aucun",
                                objet="couverture", succes=True)
        trace.ecrire("sorties/trace_01.json")
    """

    def __init__(
        self,
        nom_carte: str,
        nom_scenario: str,
        equipe: Sequence[str] | None = None,
    ) -> None:
        self.nom_carte = nom_carte
        self.nom_scenario = nom_scenario
        self.equipe: list[str] = list(equipe or [])
        self.pas: list[dict[str, Any]] = []
        self.livraisons: list[dict[str, Any]] = []

    # -- pas ---------------------------------------------------------------

    def ajouter_pas(
        self,
        demande: int | None,
        position: Sequence[int],
        casier: Sequence[int],
        action: str,
        argument: str | None = None,
        perception: dict[str, str] | None = None,
        contenu_casier: str | None = None,
        commentaire: str | None = None,
    ) -> None:
        """Enregistre un pas de simulation.

        `position`  : couple (ligne, colonne) du robot AVANT l'action.
        `casier`    : couple (ligne, colonne) du selecteur dans l'armoire,
                      AVANT l'action.
        `perception`: ce que le robot voit depuis sa position, sous la forme
                      d'un dictionnaire des quatre directions vers "mur",
                      "libre", "armoire", "dictionnaire" ou "resident".
        `contenu_casier` : l'objet du casier courant, quand le robot est
                      devant l'armoire et peut donc le voir ; None sinon.
        """
        if action not in ACTIONS:
            raise ValueError(
                f"action inconnue {action!r} (attendu : {', '.join(ACTIONS)})"
            )
        if action in ("AVANCER", "CHERCHER") and argument not in DIRECTIONS:
            raise ValueError(
                f"{action} attend une direction parmi {DIRECTIONS}, "
                f"pas {argument!r}"
            )
        self.pas.append({
            "t": len(self.pas),
            "demande": demande,
            "position": [int(position[0]), int(position[1])],
            "casier": [int(casier[0]), int(casier[1])],
            "action": action,
            "argument": argument,
            "perception": dict(perception) if perception else None,
            "contenu_casier": contenu_casier,
            "commentaire": commentaire,
        })

    # -- livraisons --------------------------------------------------------

    def ajouter_livraison(
        self,
        demande: int,
        resident: str,
        emotion: str | None,
        intensite: str | None,
        casier_choisi: Sequence[int] | None,
        repli: str,
        objet: str | None,
        succes: bool,
        motif_echec: str | None = None,
    ) -> None:
        """Enregistre l'issue d'une demande, reussie ou non.

        En cas d'echec, `succes` vaut False et `motif_echec` explique
        pourquoi en une chaine courte (par exemple "resident inaccessible",
        "armoire vide", "emotion indeterminee").
        """
        if repli not in REPLIS:
            raise ValueError(
                f"repli inconnu {repli!r} (attendu : {', '.join(REPLIS)})"
            )
        if not succes and not motif_echec:
            raise ValueError("un echec doit etre accompagne d'un motif_echec")
        self.livraisons.append({
            "demande": int(demande),
            "resident": resident,
            "emotion": emotion,
            "intensite": intensite,
            "casier_choisi": ([int(casier_choisi[0]), int(casier_choisi[1])]
                              if casier_choisi is not None else None),
            "repli": repli,
            "objet": objet,
            "pas_utilises": sum(1 for p in self.pas if p["demande"] == demande),
            "succes": bool(succes),
            "motif_echec": motif_echec,
        })

    # -- export ------------------------------------------------------------

    def en_dictionnaire(self) -> dict[str, Any]:
        reussies = sum(1 for l in self.livraisons if l["succes"])
        return {
            "format": "robot-reconfort/trace",
            "version": VERSION_ATTENDUE,
            "carte": self.nom_carte,
            "scenario": self.nom_scenario,
            "equipe": self.equipe,
            "pas": self.pas,
            "livraisons": self.livraisons,
            "resume": {
                "demandes": len(self.livraisons),
                "reussies": reussies,
                "echecs": len(self.livraisons) - reussies,
                "pas_total": len(self.pas),
            },
        }

    def ecrire(self, chemin: str | Path) -> Path:
        """Ecrit la trace en JSON UTF-8 indente. Cree le dossier au besoin."""
        chemin = Path(chemin)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(
            json.dumps(self.en_dictionnaire(), ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
        return chemin
