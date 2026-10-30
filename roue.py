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
    pass


    
