"""
Roue de Plutchick et repli de l'amoire

Armoire : 8 clonnes (emotions) - 3 lignes (intensités)
Colonnes bouclent ; lignes ne bouclent pas (0 -> faible, 1 -> moyen, 2 -> fort)
"""

from typing import Any

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

INDICE_EMOTION = { nom : i for i, nom in enumerate(EMOTIONS) }
RANG_INTENSITE = { nom : i for i, nom in enumerate(INTENSITES) }


class RouePlutchick:
    def __init__(self, emotions: list[str] | None = None, intensites: list[str] | None = None):
        self.emotions = emotions or list(EMOTIONS)
        self.intensites = intensites or list(INTENSITES)
        self.nb_emotions = len(self.emotions)
        self.nb_intensites = len(self.intensites)
        self.idx_emotion = { nom : i for i, nom in enumerate(self.emotions) }
        self.rang_intensite = { nom : i for i, nom in enumerate(self.intensites) }

    def distance(self, emotion1: str, emotion2: str) -> int:
        """Distancec cyclique entre deux emotions sur la roue (0 à 4)"""
        c1 = self.idx_emotion[emotion1]
        c2 = self.idx_emotion[emotion2]
        ecart = abs(c1 - c2)
        return min(ecart, self.nb_emotions - ecart)

    def candidats_repli(self, emotion: str, intensite: str) -> list[dict[str, Any]]:
        """
            trie les 15 casiers candidats :
            1. distance cyclique croissante
            2. ecart d'intensite croissant
            3. intensite plus faible d'abord
            4. sens horaire avant sens anti-horaire
        """
        c_ref = self.idx_emotion[emotion]
        r_ref = self.rang_intensite[intensite]

        candidats = []
        for c in range(self.nb_emotions):
            e_nom = self.emotions[c]
            d = self.distance(emotion, e_nom)
            if d > 2: continue
            for r in range(self.nb_intensites):
                i_nom = self.intensites[r]
                ecart_int = abs(r_ref - r)
                rang_int = r

                if d == 0:
                    sens = 0
                    repli = "aucun" if r == r_ref else "intensite"
                else:
                    if (c_ref + d) % self.nb_emotions == c:
                        sens = 0 # horaire
                    else:
                        sens = 1 # anti-horaire
                    repli = f"voisine_{d}"

                cle_tri = (d, ecart_int, rang_int, sens)
                candidats.append({
                    "ligne": r,
                    "colonne": c,
                    "casier": [r,c],
                    "emotion": e_nom,
                    "intensite": i_nom,
                    "repli": repli,
                    "distance": d,
                    "_cle": cle_tri,
                })

        candidats.sort(key=lambda x: x["_cle"])
        for c in candidats:
            del c["_cle"]
        return candidats

    def deplacement_selecteur(self, depart, arrivee) -> list[str]:
        """
        """
        return []
