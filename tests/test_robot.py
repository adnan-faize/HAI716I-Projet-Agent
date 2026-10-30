"""
  n°2  la replanification : un mur decouvert en route change le trajet ;
  n°7  le cas inaccessible : un resident mure, sur une grille minuscule.
    python -m unittest discover -s tests -v
"""

import unittest

from monde import Monde
from robot import Robot

LEGENDE = {"#": "mur", ".": "libre", "R": "depart du robot",
           "A": "armoire", "D": "dictionnaire", "P": "resident"}


def fabriquer_carte(grille, residents):
    """Construit une carte a partir d'une grille dessinee a la main.
    Les positions de R, A et D sont retrouvees automatiquement."""
    positions = {}
    for l, texte in enumerate(grille):
        for c, symbole in enumerate(texte):
            positions[symbole] = [l, c]
    return {
        "dimensions": {"hauteur": len(grille), "largeur": len(grille[0])},
        "legende": LEGENDE,
        "grille": grille,
        "depart_robot": positions["R"],
        "armoire": {"position": positions["A"]},
        "dictionnaire": {"position": positions["D"]},
        "residents": [{"id": rid, "nom": rid, "position": pos}
                      for rid, pos in residents.items()],
    }


def sans_grille(carte):
    """Copie de la carte SANS le champ grille : ce que le robot a le droit
    de voir. Si Robot essayait de lire la grille, il planterait."""
    return {cle: valeur for cle, valeur in carte.items() if cle != "grille"}


class TestCarteMentale(unittest.TestCase):

    def test_le_robot_fonctionne_sans_la_grille(self):
        carte = fabriquer_carte(["#####",
                                 "#R.A#",
                                 "#D.P#",
                                 "#####"], {"R1": [2, 3]})
        robot = Robot(sans_grille(carte))       # ne doit PAS lever KeyError
        self.assertEqual(robot.position, (1, 1))

    def test_au_depart_aucun_mur_n_est_connu(self):
        carte = fabriquer_carte(["#####",
                                 "#R.A#",
                                 "#D.P#",
                                 "#####"], {"R1": [2, 3]})
        robot = Robot(sans_grille(carte))
        self.assertNotIn("mur", robot.carte_mentale.values())
        self.assertTrue(robot.est_traversable((0, 0)))   # inconnu = libre

    def test_memoriser_enregistre_les_quatre_voisines(self):
        carte = fabriquer_carte(["#####",
                                 "#R.A#",
                                 "#D.P#",
                                 "#####"], {"R1": [2, 3]})
        robot = Robot(sans_grille(carte))
        robot.memoriser({"N": "mur", "S": "dictionnaire",
                         "E": "libre", "O": "mur"})
        self.assertEqual(robot.carte_mentale[(0, 1)], "mur")
        self.assertEqual(robot.carte_mentale[(1, 0)], "mur")
        self.assertFalse(robot.est_traversable((0, 1)))
        self.assertTrue(robot.est_traversable((1, 2)))


class TestReplanification(unittest.TestCase):
    """Test obligatoire n°2."""

    # C'est la mini-grille de l'annexe B.3, avec le resident en (1,4).
    #        colonne 0 1 2 3 4 5
    # ligne 0        # # # # # #
    # ligne 1        # R . # P #     le mur en (1,3) est INVISIBLE au depart
    # ligne 2        # . # . . #
    # ligne 3        # . . . # #
    # ligne 4        # A D # # #
    # ligne 5        # # # # # #
    GRILLE = ["######",
              "#R.#P#",
              "#.#..#",
              "#...##",
              "#AD###",
              "######"]

    def setUp(self):
        carte = fabriquer_carte(self.GRILLE, {"R1": [1, 4]})
        self.monde = Monde(carte)
        self.robot = Robot(sans_grille(carte))
        self.resident = (1, 4)

    def test_le_premier_plan_va_tout_droit(self):
        # Sans rien connaitre, le robot croit pouvoir aller en (1,3) : 2 pas.
        plan = self.robot.planifier(self.resident)
        self.assertEqual(plan, [(1, 1), (1, 2), (1, 3)])

    def test_le_mur_decouvert_change_le_trajet(self):
        trajet = []
        arrive = self.robot.aller_vers(
            self.monde, self.resident,
            journaliser=lambda pos, d, perception: trajet.append(d))

        self.assertTrue(arrive)
        # le mur (1,3) a ete decouvert et memorise
        self.assertEqual(self.robot.carte_mentale[(1, 3)], "mur")
        # le robot a fini a cote du resident, en passant par le bas
        self.assertEqual(self.robot.position, (2, 4))
        # le trajet reel est bien plus long que les 2 pas du premier plan
        self.assertGreater(len(trajet), 2)
        # il est d'abord parti vers l'est, puis a fait demi-tour
        self.assertEqual(trajet[0], "E")
        self.assertIn("O", trajet)

    def test_la_position_du_robot_suit_le_simulateur(self):
        self.robot.aller_vers(self.monde, self.resident)
        self.assertEqual(self.robot.position, self.monde.position_robot)


class TestInaccessible(unittest.TestCase):
    """Test obligatoire n°7 : un resident mure."""

    #        colonne 0 1 2 3 4 5 6
    # ligne 0        # # # # # # #
    # ligne 1        # R . A # P #     P entoure de murs
    # ligne 2        # D . . # # #
    # ligne 3        # # # # # # #
    GRILLE = ["#######",
              "#R.A#P#",
              "#D..###",
              "#######"]

    def test_resident_mure_est_declare_inaccessible(self):
        carte = fabriquer_carte(self.GRILLE, {"R1": [1, 5]})
        monde = Monde(carte)
        robot = Robot(sans_grille(carte))

        arrive = robot.aller_vers(monde, (1, 5))   # ne doit pas boucler

        self.assertFalse(arrive)

    def test_les_autres_cibles_restent_accessibles(self):
        carte = fabriquer_carte(self.GRILLE, {"R1": [1, 5]})
        monde = Monde(carte)
        robot = Robot(sans_grille(carte))
        robot.aller_vers(monde, (1, 5))            # echec...
        # ...mais le robot peut toujours aller au dictionnaire
        self.assertTrue(robot.aller_vers(monde, (2, 1)))


if __name__ == "__main__":
    unittest.main()