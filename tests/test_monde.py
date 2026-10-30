"""
    py -m unittest discover -s tests -v
"""

import unittest

from monde import ActionIllegale, Monde

#            colonne 0 1 2 3 4
# ligne 0            # # # # #
# ligne 1            # R . A #      R = depart (1,1), A = armoire (1,3)
# ligne 2            # . . . #
# ligne 3            # D # P #      D = dictionnaire (3,1), P = resident (3,3)
# ligne 4            # # # # #
CARTE = {
    "dimensions": {"hauteur": 5, "largeur": 5},
    "legende": {"#": "mur", ".": "libre", "R": "depart du robot",
                "A": "armoire", "D": "dictionnaire", "P": "resident"},
    "grille": [
        "#####",
        "#R.A#",
        "#...#",
        "#D#P#",
        "#####",
    ],
    "depart_robot": [1, 1],
    "armoire": {"position": [1, 3]},
    "dictionnaire": {"position": [3, 1]},
    "residents": [{"id": "R1", "nom": "Camille", "position": [3, 3]}],
}


class TestPerception(unittest.TestCase):

    def test_perception_au_depart(self):
        monde = Monde(CARTE)
        self.assertEqual(monde.percevoir(),
                         {"N": "mur", "S": "libre", "E": "libre", "O": "mur"})

    def test_perception_voit_l_armoire(self):
        monde = Monde(CARTE)
        monde.avancer("E")                                  # robot en (1,2)
        self.assertEqual(monde.percevoir()["E"], "armoire")

    def test_perception_voit_dictionnaire_et_resident(self):
        monde = Monde(CARTE)
        monde.avancer("S")                                  # (2,1)
        self.assertEqual(monde.percevoir()["S"], "dictionnaire")
        monde.avancer("E")
        monde.avancer("E")                                  # (2,3)
        self.assertEqual(monde.percevoir()["S"], "resident")

    def test_hors_grille_est_un_mur(self):
        carte = dict(CARTE, grille=["R.", ".."], depart_robot=[0, 0],
                     dimensions={"hauteur": 2, "largeur": 2},
                     armoire={"position": [1, 1]},
                     dictionnaire={"position": [1, 1]}, residents=[])
        perception = Monde(carte).percevoir()
        self.assertEqual(perception["N"], "mur")
        self.assertEqual(perception["O"], "mur")


class TestAvancer(unittest.TestCase):

    def test_avancer_sur_case_libre_deplace_le_robot(self):
        monde = Monde(CARTE)
        monde.avancer("S")
        self.assertEqual(monde.position_robot, (2, 1))

    def test_avancer_dans_un_mur_est_refuse(self):
        monde = Monde(CARTE)
        with self.assertRaises(ActionIllegale):
            monde.avancer("N")
        self.assertEqual(monde.position_robot, (1, 1))     # n'a pas bouge

    def test_avancer_sur_un_meuble_est_refuse(self):
        monde = Monde(CARTE)
        monde.avancer("E")                                  # (1,2)
        with self.assertRaises(ActionIllegale):
            monde.avancer("E")                              # armoire en (1,3)


class TestActions(unittest.TestCase):

    def test_consulter_loin_du_dictionnaire_est_refuse(self):
        monde = Monde(CARTE)                                # (1,1)
        with self.assertRaises(ActionIllegale):
            monde.consulter()

    def test_consulter_a_cote_du_dictionnaire(self):
        monde = Monde(CARTE)
        monde.avancer("S")                                  # (2,1), a cote de D
        monde.consulter()                                   # ne leve rien

    def test_prendre_loin_de_l_armoire_est_refuse(self):
        monde = Monde(CARTE)                                # (1,1) : 2 cases
        with self.assertRaises(ActionIllegale):
            monde.prendre("couverture")

    def test_on_ne_porte_qu_un_objet(self):
        monde = Monde(CARTE)
        monde.avancer("E")
        monde.prendre("couverture")
        with self.assertRaises(ActionIllegale):
            monde.prendre("tisane")

    def test_livraison_complete(self):
        monde = Monde(CARTE)
        monde.avancer("E")                                  # (1,2) a cote de A
        monde.prendre("couverture")
        self.assertEqual(monde.objet_porte, "couverture")
        monde.avancer("S")
        monde.avancer("E")                                  # (2,3) a cote de R1
        monde.donner("R1", "couverture")
        self.assertIsNone(monde.objet_porte)                # mains vides

    def test_donner_loin_du_resident_est_refuse(self):
        monde = Monde(CARTE)
        monde.avancer("E")
        monde.prendre("couverture")                         # (1,2) : trop loin
        with self.assertRaises(ActionIllegale):
            monde.donner("R1", "couverture")

    def test_donner_le_mauvais_objet_est_refuse(self):
        monde = Monde(CARTE)
        monde.avancer("E")
        monde.prendre("couverture")
        monde.avancer("S")
        monde.avancer("E")                                  # a cote de R1
        with self.assertRaises(ActionIllegale):
            monde.donner("R1", "tisane")


if __name__ == "__main__":
    unittest.main()