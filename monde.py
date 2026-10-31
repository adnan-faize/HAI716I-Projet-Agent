from planification import DIRECTIONS


class ActionIllegale(Exception):
    """
    Le robot a tenté une action que la réalite interdit.
    Si elle est levée, c'est qu'il y a un bug dans l'agent.
    """


# Ce que le robot peut percevoir sur une case.
# Le symbole 'depart du robot' de la legende est une case libre comme une autre.
TRADUCTION_LEGENDE = {
    "mur"            : "mur",
    "libre"          : "libre",
    "depart du robot": "libre",
    "armoire"        : "armoire",
    "dictionnaire"   : "dictionnaire",
    "resident"       : "resident",
}


class Monde:
    def __init__(self, carte, armoire = None):
        self._grille = carte["grille"]
        self._types = {
            symbole: TRADUCTION_LEGENDE[nom]
            for symbole, nom in carte["legende"].items()
        }

        self.hauteur = carte["dimensions"]["hauteur"]
        self.largeur = carte["dimensions"]["largeur"]

        self.position_robot = tuple(carte["depart_robot"])
        self.objet_porte = None          # le robot porte au plus un objet

        # Positions utiles pour verifier les actions
        self.position_armoire = tuple(carte["armoire"]["position"])
        self.position_dictionnaire = tuple(carte["dictionnaire"]["position"])
        self.position_residents = {
            r["id"]: tuple(r["position"])
            for r in carte["residents"]
        }

        if armoire is not None:
            self.hauteur_armoire = len(armoire.get("intensites", ["faible", "moyenne", "forte"]))
            self.largeur_armoire = len(armoire.get("emotions", ["joie", "confiance", "peur", "surprise", "tristesse", "degout", "colere", "anticipation"]))
            self.position_selecteur = list(armoire.get("casier_depart", [1, 0]))
            self.casiers = {
                (c["ligne"], c["colonne"]): c.get("objet")
                for c in armoire.get("casiers", [])
            }
        else:
            self.hauteur_armoire = 3
            self.largeur_armoire = 8
            self.position_selecteur = [1, 0]
            self.casiers = {}

    # ------------------------------------------------------------------ #
    # Lecture de la grille (privee : le nom commence par _)
    # ------------------------------------------------------------------ #

    def _type_case(self, case):
        """Type reel d'une case. En dehors de la grille, on repond "mur"."""
        ligne, colonne = case
        if not (0 <= ligne < self.hauteur and 0 <= colonne < self.largeur):
            return "mur"
        symbole = self._grille[ligne][colonne]
        return self._types[symbole]

    def _case_dans_direction(self, direction):
        """La case voisine du robot dans la direction donnee."""
        dl, dc = DIRECTIONS[direction]
        ligne, colonne = self.position_robot
        return (ligne + dl, colonne + dc)

    def _est_adjacent(self, cible):
        """Vrai si le robot est sur une case orthogonalement voisine de cible."""
        ligne, colonne = self.position_robot
        cl, cc = cible
        return abs(ligne - cl) + abs(colonne - cc) == 1

    # ------------------------------------------------------------------ #
    # Perception
    # ------------------------------------------------------------------ #

    def percevoir(self):
        """Ce que le robot voit : le type de ses 4 voisines, rien de plus.

            {"N": "mur", "S": "libre", "E": "armoire", "O": "libre"}
        """
        return {direction: self._type_case(self._case_dans_direction(direction))
                for direction in DIRECTIONS}

    def contenu_casier(self) -> str | None:
        """Contenu de l'objet dans le casier devant lequel se trouve le selecteur,
        uniquement si le robot est adjacent a l'armoire. None sinon.
        """
        if not self._est_adjacent(self.position_armoire):
            return None
        return self.casiers.get(tuple(self.position_selecteur))

    # ------------------------------------------------------------------ #
    # Actions (enonce, section 3.4)
    # ------------------------------------------------------------------ #

    def avancer(self, direction):
        """AVANCER : la case visee doit etre libre."""
        if direction not in DIRECTIONS:
            raise ActionIllegale(f"direction inconnue : {direction!r}")
        cible = self._case_dans_direction(direction)
        if self._type_case(cible) != "libre":
            raise ActionIllegale(
                f"AVANCER {direction} depuis {self.position_robot} : "
                f"la case {cible} est '{self._type_case(cible)}'")
        self.position_robot = cible

    def consulter(self):
        """CONSULTER : le robot doit etre a cote du dictionnaire."""
        if not self._est_adjacent(self.position_dictionnaire):
            raise ActionIllegale(
                f"CONSULTER depuis {self.position_robot} : "
                f"pas a cote du dictionnaire {self.position_dictionnaire}")

    def chercher(self, direction: str) -> None:
        """CHERCHER : deplace le selecteur d'un cran.
        Le robot doit etre a cote de l'armoire.
        Les colonnes bouclent modulo largeur_armoire. Les lignes ne bouclent pas.
        """
        if not self._est_adjacent(self.position_armoire):
            raise ActionIllegale(
                f"CHERCHER depuis {self.position_robot} : "
                f"pas a cote de l'armoire {self.position_armoire}"
            )
        if direction not in DIRECTIONS:
            raise ActionIllegale(f"direction inconnue : {direction!r}")

        l, c = self.position_selecteur[0], self.position_selecteur[1]
        if direction == "N":
            if l == 0:
                raise ActionIllegale("CHERCHER N depuis la ligne 0 est illegal (ne boucle pas)")
            self.position_selecteur[0] = l - 1
        elif direction == "S":
            if l == self.hauteur_armoire - 1:
                raise ActionIllegale("CHERCHER S depuis la derniere ligne est illegal (ne boucle pas)")
            self.position_selecteur[0] = l + 1
        elif direction == "E":
            self.position_selecteur[1] = (c + 1) % self.largeur_armoire
        elif direction == "O":
            self.position_selecteur[1] = (c - 1) % self.largeur_armoire

    def prendre(self, objet):
        """PRENDRE : a cote de l'armoire, les mains vides.
        (Le binome ajoutera : le casier courant doit contenir cet objet.)"""
        if not self._est_adjacent(self.position_armoire):
            raise ActionIllegale(
                f"PRENDRE depuis {self.position_robot} : "
                f"pas a cote de l'armoire {self.position_armoire}")
        if self.objet_porte is not None:
            raise ActionIllegale(
                f"PRENDRE : le robot porte deja '{self.objet_porte}'")
        self.objet_porte = objet

    def donner(self, id_resident, objet):
        """DONNER : a cote du bon resident, en portant cet objet."""
        if id_resident not in self.position_residents:
            raise ActionIllegale(f"resident inconnu : {id_resident!r}")
        if not self._est_adjacent(self.position_residents[id_resident]):
            raise ActionIllegale(
                f"DONNER depuis {self.position_robot} : "
                f"pas a cote du resident {id_resident}")
        if self.objet_porte != objet:
            raise ActionIllegale(
                f"DONNER '{objet}' : le robot porte {self.objet_porte!r}")
        self.objet_porte = None
