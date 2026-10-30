""" ce que le robot sait et comment il decide ou aller.
"""

from planification import DIRECTIONS, direction_entre, plus_court_chemin


class Robot:

    def __init__(self, carte, armoire):
        self.hauteur = carte["dimensions"]["hauteur"]
        self.largeur = carte["dimensions"]["largeur"]
        self.position = tuple(carte["depart_robot"])

        self.position_armoire = tuple(carte["armoire"]["position"])
        self.position_dictionnaire = tuple(carte["dictionnaire"]["position"])
        self.position_residents = {r["id"]: tuple(r["position"])
                                   for r in carte["residents"]}

        #  la carte mentale 
    
        self.carte_mentale = {}
        self.carte_mentale[self.position] = "libre"      # il est dessus
        self.carte_mentale[self.position_armoire] = "armoire"
        self.carte_mentale[self.position_dictionnaire] = "dictionnaire"
        for case in self.position_residents.values():
            self.carte_mentale[case] = "resident"

        if armoire is not None:
            self.position_selecteur = list(armoire.get("casier_depart", [1,0]))
        else:
            self.position_selecteur = [1,0]
        self.memoire_armoire = {}

        self.objet_main = None

    #--------------- Memoire

    def memoriser(self, perception):
        #inscrit les 4 voisines percues dans la carte mentale.
        #perception = {"N": "mur", "S": "libre", "E": "libre", "O": "mur"}

        ligne, colonne = self.position
        for direction, type_case in perception.items():
            dl, dc = DIRECTIONS[direction]
            case = (ligne + dl, colonne + dc)
            # hors de la grille : inutile de le retenir, le BFS n'y va jamais
            if 0 <= case[0] < self.hauteur and 0 <= case[1] < self.largeur:
                self.carte_mentale[case] = type_case

    def est_traversable(self, case):
        #hypothése optimiste: une case inconnue est supposee libre

        return self.carte_mentale.get(case, "libre") == "libre"

    #----------- Decision

    def cases_autour(self, cible):
        """les cases ou le robot doit se placer pour interagir avec `cible`
        (les 4 voisines, dans la grille). le BFS ecartera celles qui
        sont des murs."""
        ligne, colonne = cible
        resultat = set()
        for dl, dc in DIRECTIONS.values():
            l, c = ligne + dl, colonne + dc
            if 0 <= l < self.hauteur and 0 <= c < self.largeur:
                resultat.add((l, c))
        return resultat

    def planifier(self, cible):
        #Plus court chemin sur la carte mentale jusqu'a cote de `cible`
        return plus_court_chemin(self.position, self.cases_autour(cible),
                                 self.est_traversable,
                                 self.hauteur, self.largeur)

    def prochaine_direction(self, cible):
        #decide du prochain pas vers `cible`.

       
        chemin = self.planifier(cible)
        if chemin is None:
            return None
        if len(chemin) == 1:                 # on est deja sur une case d'arrivee
            return "ARRIVE"
        return direction_entre(chemin[0], chemin[1])

    # ----La boucle : percevoir -> memoriser -> decider -> agir

    def aller_vers(self, monde, cible, journaliser=None):
        """deplace le robot jusqu'a cote de `cible`, un pas a la fois,
    
        """
        limite = 4 * self.hauteur * self.largeur * self.hauteur * self.largeur

        for _ in range(limite):
            perception = monde.percevoir()               # 1. percevoir
            self.memoriser(perception)                   # 2. memoriser
            direction = self.prochaine_direction(cible)  # 3. decider (BFS)

            if direction == "ARRIVE":
                return True
            if direction is None:
                return False

            if journaliser is not None:
                journaliser(self.position, direction, perception)
            monde.avancer(direction)                     # 4. agir
            dl, dc = DIRECTIONS[direction]               #    et mettre a jour
            self.position = (self.position[0] + dl,      #    sa propre position
                             self.position[1] + dc)

        raise RuntimeError(f"aller_vers {cible} : le robot tourne en rond")