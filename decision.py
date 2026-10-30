"""
Décisions de l'agent.

Lecture et analyse du dictionnaire
Fouille de l'armoire
"""

from __future__ import annotations

from typing import Any

from reconfort_io import normaliser
from roue import RouePlutchik


class Decision:
    def __init__(self, roue: RouePlutchik | None = None):
        self.roue = roue or RouePlutchik()

    @staticmethod
    def analyser_message(dictionnaire: dict[str, Any], message: str) -> tuple[str, str] | None:
        """
            Lit émotion et intensite dans le dic selon la sec 6.1
            1. normalise le message
            2. parcourt les mots de gauche à droite
            3. premier mot donne la réponse ; si aucun mot -> emotion indeterminee (None)
        """
        formes_connues: dict[str, tuple[str, str]] = {}
        for entree in dictionnaire.get("entrees", []):
            emotion = entree["emotion"]
            intensite = entree["intensite"]
            for forme in entree.get("formes", []):
                formes_connues[forme] = (emotion, intensite)

        mots = normaliser(message)
        for mot in mots:
            if mot in formes_connues:
                return formes_connues[mot]
        return None

    def preparer_candidats_armoire(self, emotion: str, intensite: str) -> list[dict[str, Any]]:
        return self.roue.candidats_repli(emotion, intensite)

    def chemin_selecteur(self, act_pos, target_pos) -> list[str]:
        return self.roue.deplacement_selecteur(act_pos, target_pos)
