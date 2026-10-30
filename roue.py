"""
Roue de Plutchick et repli de l'amoire

Armoire : 8 clonnes (emotions) - 3 lignes (intensités)
Colonnes bouclent ; lignes ne bouclent pas (0 -> faible, 1 -> moyen, 2 -> fort)
"""

EMOTIONS = [
    "joie",
    "confiance",
    "peur",
    "surprise",
    "tristesse",
    "degout",
    "colere",
    "anticipation",
]

INTENSITES = ["faible", "moyenne", "forte"]

RANG_INTENSITE = { nom : i for i, nom in enumerate(INTENSITES) }
INDICE_EMOTION = { nom : i for i, nom in enumerate(EMOTIONS) }


class RouePlutchick:
    def __init__(self, emotions: list[str] | None = None, intensites: list[str] | None = None):
        self.emotions = emotions or list(EMOTIONS)
        self.intensites = intensites or list(INTENSITES)
        self.nb_emotions = len(self.emotions)
        self.nb_intensites = len(self.intensites)
        self.idx_emotion = { nom : i for i, nom in enumerate(self.emotions) }
        self.idx_intensite = { nom : i for i, nom in enumerate(self.intensites) }

    def distance(self, emotion1: str, emotion2: str) -> int:
        """Distancec cyclique entre deux emotions sur la roue (0 à 4)"""
        c1 = self.idx_emotion[emotion1]
        c2 = self.idx_emotion[emotion2]
        ecart = abs(c1 - c2)
        return min(ecart, self.nb_emotions - ecart)

    
