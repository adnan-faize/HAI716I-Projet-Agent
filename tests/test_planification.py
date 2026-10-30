"""
test sur une petite grille ecrite a la main, un chemin dont vous connaissez
la longueur".
    python -m unittest discover -s tests -v
"""

import unittest

from planification import (
    direction_entre,
    plus_court_chemin,
    voisins,
)

def fabriquer_est_traversable(grille):
    #transforme une grille ecrite a la main (liste de textes) en fonction :case -> True/False, comme celle que fournira le robot
    def est_traversable(case):
        ligne, colonne = case
        return grille[ligne][colonne] != "#"
    return est_traversable

# Mini-grille de l'annexe B.3 : depart (1,1), cible (1,4), 7 pas connus.
GRILLE_ANNEXE = [
    "######",
    "#..#.#",
    "#.#..#",
    "#...##",
    "######",
]


class TestVoisins(unittest.TestCase):

    def test_case_au_milieu_a_quatre_voisines(self):
        self.assertEqual(voisins((1, 1), 5, 6),
                         [(0, 1), (2, 1), (1, 2), (1, 0)])

    def test_coin_n_a_que_deux_voisines(self):
        # le nord et l'ouest sortent de la grille
        self.assertEqual(voisins((0, 0), 5, 6), [(1, 0), (0, 1)])

    def test_coin_oppose(self):
        self.assertEqual(voisins((4, 5), 5, 6), [(3, 5), (4, 4)])


class TestPlusCourtChemin(unittest.TestCase):

    def test_chemin_de_l_annexe_fait_7_pas(self):
        """LE test obligatoire : longueur connue a l'avance."""
        chemin = plus_court_chemin((1, 1), {(1, 4)},
                                   fabriquer_est_traversable(GRILLE_ANNEXE),
                                   5, 6)
        self.assertEqual(len(chemin) - 1, 7)
        self.assertEqual(chemin[0], (1, 1))    # commence au depart
        self.assertEqual(chemin[-1], (1, 4))   # finit a la cible

    def test_chemin_ne_passe_jamais_par_un_mur(self):
        est_traversable = fabriquer_est_traversable(GRILLE_ANNEXE)
        chemin = plus_court_chemin((1, 1), {(1, 4)}, est_traversable, 5, 6)
        for case in chemin:
            self.assertTrue(est_traversable(case), f"{case} est un mur")

    def test_chaque_pas_va_vers_une_case_voisine(self):
        chemin = plus_court_chemin((1, 1), {(1, 4)},
                                   fabriquer_est_traversable(GRILLE_ANNEXE),
                                   5, 6)
        for a, b in zip(chemin, chemin[1:]):
            # leve une erreur si a et b ne sont pas voisines
            direction_entre(a, b)

    def test_ligne_droite_sans_obstacle(self):
        grille = [
            ".....",
        ]
        chemin = plus_court_chemin((0, 0), {(0, 4)},
                                   fabriquer_est_traversable(grille), 1, 5)
        self.assertEqual(chemin, [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])

    def test_piece_ouverte_donne_le_plus_court(self):
        """Dans une piece vide il existe des milliers de chemins.
        Ce test echoue si on utilise une PILE au lieu d'une FILE :
        le parcours en profondeur trouve un chemin, mais trop long."""
        piece = [
            ".....",
            ".....",
            ".....",
            ".....",
            ".....",
        ]
        est_traversable = fabriquer_est_traversable(piece)
        chemin = plus_court_chemin((2, 2), {(2, 4)}, est_traversable, 5, 5)
        self.assertEqual(len(chemin) - 1, 2)
        chemin = plus_court_chemin((4, 0), {(0, 4)}, est_traversable, 5, 5)
        self.assertEqual(len(chemin) - 1, 8)

    def test_deja_arrive_donne_zero_pas(self):
        chemin = plus_court_chemin((2, 2), {(2, 2)},
                                   fabriquer_est_traversable(GRILLE_ANNEXE),
                                   5, 6)
        self.assertEqual(chemin, [(2, 2)])

    def test_plusieurs_arrivees_prend_la_plus_proche(self):
        # comme les cases autour de l'armoire : on veut la plus proche
        grille = [
            ".......",
        ]
        chemin = plus_court_chemin((0, 2), {(0, 0), (0, 6)},
                                   fabriquer_est_traversable(grille), 1, 7)
        self.assertEqual(chemin[-1], (0, 0))   # 2 pas, contre 4 vers (0,6)
        self.assertEqual(len(chemin) - 1, 2)

    def test_cible_emmuree_donne_none(self):
        grille = [
            ".....",
            ".###.",
            ".#.#.",
            ".###.",
            ".....",
        ]
        chemin = plus_court_chemin((0, 0), {(2, 2)},
                                   fabriquer_est_traversable(grille), 5, 5)
        self.assertIsNone(chemin)


class TestDirectionEntre(unittest.TestCase):

    def test_quatre_directions(self):
        self.assertEqual(direction_entre((1, 1), (0, 1)), "N")
        self.assertEqual(direction_entre((1, 1), (2, 1)), "S")
        self.assertEqual(direction_entre((1, 1), (1, 2)), "E")
        self.assertEqual(direction_entre((1, 1), (1, 0)), "O")

    def test_cases_non_voisines_leve_une_erreur(self):
        with self.assertRaises(ValueError):
            direction_entre((1, 1), (3, 1))


if __name__ == "__main__":
    unittest.main()