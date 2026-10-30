"""calcul du plus court chemin dans une grille (BFS).
ce fichier ne sait rien de l'appartement reel il recoit seulement :
  - une case de depart
  - un ensemble de cases d'arrivee
  - une fonction qui dit si une case est traversable
  - les dimensions de la grille
"""

from collections import deque   # une file efficace (ajout a droite, retrait a gauche)

# Pour chaque direction : de combien on bouge en (ligne, colonne).
# La ligne 0 est en HAUT de la grille, donc aller au nord = ligne - 1.
DIRECTIONS = {
    "N": (-1, 0),   # une ligne plus haut
    "S": (1, 0),    # une ligne plus bas
    "E": (0, 1),    # une colonne a droite
    "O": (0, -1),   # une colonne a gauche
}


def voisins(case, hauteur, largeur):
    """Renvoie la liste des cases voisines de `case` qui sont DANS la grille.
    on ne verifie pas ici si ce sont des murs : ce n'est pas le role de
    cette fonction on verifie seulement qu'on ne sort pas des bords.
    """
    ligne, colonne = case
    resultat = []
    for dl, dc in DIRECTIONS.values():
        nouvelle_ligne = ligne + dl
        nouvelle_colonne = colonne + dc
        dans_la_grille = (0 <= nouvelle_ligne < hauteur
                          and 0 <= nouvelle_colonne < largeur)
        if dans_la_grille:
            resultat.append((nouvelle_ligne, nouvelle_colonne))
    return resultat


def plus_court_chemin(depart, arrivees, est_traversable, hauteur, largeur):
    
    # cas particulier: on est deja arrive, chemin de 0 pas.
    if depart in arrivees:
        return [depart]

    #prédécesseur :celui qui vient avant 
    predecesseur = {depart: None} 
    # pa file des cases a explorer. premier entré premier sorti(file d attente):
    file = deque([depart])

    while file:                              # tant qu'il reste des cases a explorer
        courant = file.popleft()             # on prend la PLUS ANCIENNE

        for voisin in voisins(courant, hauteur, largeur):
            if voisin in predecesseur:       # deja vue: on l'ignore,
                continue                     # sinon on tournerait en rond
            if not est_traversable(voisin):  # mur: on ne passe pas
                continue

            predecesseur[voisin] = courant   # on retient d'ou on vient

            if voisin in arrivees:           # trouve ! c'est forcement le plus court
                return reconstruire_chemin(predecesseur, voisin)

            file.append(voisin)              # a explorer plus tard (en fin de file)

    # La file est vide et on n'a jamais touche une arrivee :
    # aucun chemin n'existe.
    return None


def reconstruire_chemin(predecesseur, arrivee):
    """remonte les predecesseurs depuis l'arrivee jusqu'au depart.
    on obtient le chemin a l'envers (arrivee -> depart) donc on le
    retourne a la fin.
    """
    chemin = [arrivee]
    while predecesseur[chemin[-1]] is not None:   # tant qu'on n'est pas au depart
        chemin.append(predecesseur[chemin[-1]])   # on ajoute la case precedente
    chemin.reverse()                              # remettre dans le bon sens
    return chemin


def direction_entre(case_a, case_b):
    """renvoie la direction ("N", "S", "E" ou "O") pour aller de case_a
    a case_b qui doivent etre voisines, utile pour transformer le
    premier pas du chemin en action AVANCER.
    """
    dl = case_b[0] - case_a[0]
    dc = case_b[1] - case_a[1]
    for nom, deplacement in DIRECTIONS.items():
        if deplacement == (dl, dc):
            return nom
    raise ValueError(f"{case_a} et {case_b} ne sont pas voisines")


# ---------------------------------------------------------------------------
# Petit essai quand on lance ce fichier directement : python planification.py
# (ce bloc ne s'execute PAS quand un autre fichier fait "import planification")
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Mini-grille de l'annexe B.3 de l'enonce.
    grille = [
        "######",
        "#R.#.#",
        "#.#..#",
        "#...##",
        "######",
    ]

    def est_libre(case):
        ligne, colonne = case
        return grille[ligne][colonne] != "#"

    chemin = plus_court_chemin((1, 1), {(1, 4)}, est_libre, 5, 6)
    print("chemin :", chemin)
    print("nombre de pas :", len(chemin) - 1)          # attendu : 7
    print("premier pas :", direction_entre(chemin[0], chemin[1]))  # attendu : S