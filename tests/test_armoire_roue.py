import unittest

from roue import RouePlutchik


class TestDeplacementSelecteur(unittest.TestCase):
    def setUp(self) -> None:
        self.roue = RouePlutchik()

    def test_bouclage_colonne_7_vers_0(self): # (test bouclage)
        trajet = self.roue.deplacement_selecteur([1, 7], [1, 0])
        self.assertEqual(trajet, ["E"])

    def test_bouclage_colonne_0_vers_7(self): # (test bouclage)
        trajet = self.roue.deplacement_selecteur([1, 0], [1, 7])
        self.assertEqual(trajet, ["O"])

    def test_exemples_annexe_c3(self):
        self.assertEqual(self.roue.deplacement_selecteur([1, 0], [1, 4]), ["E", "E", "E", "E"])
        self.assertEqual(self.roue.deplacement_selecteur([2, 7], [0, 1]), ["N", "N", "E", "E"])
        self.assertEqual(self.roue.deplacement_selecteur([1, 0], [2, 6]), ["S", "O", "O"])


class TestRegleRepli(unittest.TestCase):
    def setUp(self):
        self.roue = RouePlutchik()

    def test_casier_exact_garni_donne_repli_aucun(self):
        candidats = self.roue.candidats_repli("tristesse", "moyenne")
        premier = candidats[0]
        self.assertEqual(premier["casier"], [1, 4])
        self.assertEqual(premier["emotion"], "tristesse")
        self.assertEqual(premier["intensite"], "moyenne")
        self.assertEqual(premier["repli"], "aucun")
    
    def test_repli_intensite_quand_casier_exact_vide(self):
        candidats = self.roue.candidats_repli("tristesse", "moyenne")
        deuxieme = candidats[1]
        troisieme = candidats[2]
        self.assertEqual(deuxieme["emotion"], "tristesse")
        self.assertEqual(deuxieme["repli"], "intensite")
        self.assertEqual(troisieme["emotion"], "tristesse")
        self.assertEqual(troisieme["repli"], "intensite")
    
    def test_colonne_entiere_vide_repli_sur_voisine(self):
        # Annexe C.5 : surprise / forte ; toute surprise vide
        candidats = self.roue.candidats_repli("surprise", "forte")
        # Rang 1 a 3 : surprise (repli aucun, puis intensite)
        self.assertEqual(candidats[0]["emotion"], "surprise")
        self.assertEqual(candidats[1]["emotion"], "surprise")
        self.assertEqual(candidats[2]["emotion"], "surprise")
        # Rang 4 : premier voisin sur la roue a distance 1
        rang_4 = candidats[3]
        self.assertEqual(rang_4["casier"], [2, 4])
        self.assertEqual(rang_4["emotion"], "tristesse")
        self.assertEqual(rang_4["intensite"], "forte")
        self.assertEqual(rang_4["repli"], "voisine_1")
        # Rang 5 : deuxieme voisin sur la roue (anti-horaire)
        rang_5 = candidats[4]
        self.assertEqual(rang_5["casier"], [2, 2])
        self.assertEqual(rang_5["emotion"], "peur")
        self.assertEqual(rang_5["intensite"], "forte")
        self.assertEqual(rang_5["repli"], "voisine_1")
    
    def test_exactement_15_candidats_a_distance_inferieure_ou_egale_a_2(self):
        candidats = self.roue.candidats_repli("joie", "faible")
        self.assertEqual(len(candidats), 15)
        distances = {c["distance"] for c in candidats}
        self.assertEqual(distances, {0, 1, 2})
        # Aucune emotion a distance 3 ou 4 n'est presente
        self.assertNotIn(3, distances)
        self.assertNotIn(4, distances)        


if __name__ == '__main__':
    unittest.main()
