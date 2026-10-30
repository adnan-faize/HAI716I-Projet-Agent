"""
Décision de l'agent.

Lecture et analyse du dictionnaire
Fouille de l'armoire
"""

from __future__ import annotations

from typing import Any

from reconfort_io import normaliser
from roue import RouePlutchick


class Decision:


    def __init__(self, roue: RouePlutchick | None = None):
        self.roue = roue or RouePlutchick()

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
