import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from reconfort_io import (
    ErreurFichier,
    charger_armoire,
    charger_carte,
    charger_dictionnaire,
    charger_scenario,
)

CARTE_BASE = {
    "format": "robot-reconfort/carte", 
    "version": 1, 
    "nom": "appartement_01",
    "dimensions": {"hauteur": 3, "largeur": 3},
    "legende": {"#": "mur", ".": "libre", "R": "depart du robot", "A": "armoire", "D": "dictionnaire", "P": "resident"},
    "grille": [
        "R.P",
        ".A.",
        "#D#"
    ],
    "depart_robot": [0, 0],
    "armoire": {"position": [1, 1]},
    "dictionnaire": {"position": [2, 1]},
    "residents": [{"id": "R1", "nom": "Camille", "position": [0, 2]}]
}

ARMOIRE_BASE = {
    "format": "robot-reconfort/armoire", 
    "version": 1, 
    "nom": "armoire_test",
    "emotions": ["joie", "tristesse"], 
    "intensites": ["faible"],
    "casier_depart": [0, 0],
    "casiers": [
        {"ligne": 0, "colonne": 0, "emotion": "joie", "intensite": "faible", "objet": "tisane"},
        {"ligne": 0, "colonne": 1, "emotion": "tristesse", "intensite": "faible", "objet": "mouchoirs"}
    ]
}

DICTIONNAIRE_BASE = {
    "format": "robot-reconfort/dictionnaire", 
    "version": 1, 
    "nom": "dict_test",
    "emotions": ["joie", "tristesse"], 
    "intensites": ["faible"],
    "entrees": [
        {"formes": ["heureux", "sourire"], "emotion": "joie", "intensite": "faible"},
        {"formes": ["pleure", "cafard"], "emotion": "tristesse", "intensite": "faible"}
    ]
}

SCENARIO_BASE = {
    "format": "robot-reconfort/scenario", 
    "version": 1, 
    "nom": "scenario_01",
    "carte": "appartement_01", 
    "armoire": "armoire_test",
    "demandes": [
        {"numero": 1, "resident": "R1", "message": "Je suis heureux"}
    ]
}


class TestReconfortIO(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def ecrire_json(self, nom_fichier: str, donnees: dict) -> Path:
        chemin = self.dir_path / nom_fichier
        chemin.write_text(json.dumps(donnees), encoding="utf-8")
        return chemin

    # --- TESTS CARTE ---
    def test_carte_valide(self):
        chemin = self.ecrire_json("carte.json", CARTE_BASE)
        donnees = charger_carte(chemin)
        self.assertEqual(donnees["nom"], "appartement_01")

    def test_carte_grille_non_rectangulaire(self):
        carte = deepcopy(CARTE_BASE)
        carte["grille"][1] = ".A" # Plus court que les autres
        chemin = self.ecrire_json("carte.json", carte)
        with self.assertRaisesRegex(ErreurFichier, "grille non rectangulaire"):
            charger_carte(chemin)

    def test_carte_dimensions_incoherentes(self):
        carte = deepcopy(CARTE_BASE)
        carte["dimensions"]["hauteur"] = 10 # Fausse hauteur
        chemin = self.ecrire_json("carte.json", carte)
        with self.assertRaisesRegex(ErreurFichier, "hauteur de grille annoncee"):
            charger_carte(chemin)

    def test_carte_symbole_inattendu(self):
        carte = deepcopy(CARTE_BASE)
        carte["depart_robot"] = [0, 1] # En (0,1) c'est un '.', pas un 'R'
        chemin = self.ecrire_json("carte.json", carte)
        with self.assertRaisesRegex(ErreurFichier, "symbole de depart inattendu"):
            charger_carte(chemin)

    def test_carte_resident_hors_limite(self):
        carte = deepcopy(CARTE_BASE)
        carte["residents"][0]["position"] = [9, 9] # Hors grille
        chemin = self.ecrire_json("carte.json", carte)
        with self.assertRaisesRegex(ErreurFichier, "hors de la grille"):
            charger_carte(chemin)

    def test_carte_resident_doublon(self):
        carte = deepcopy(CARTE_BASE)
        # Ajout d'un 2ème résident avec le même ID 'R1'
        carte["residents"].append({"id": "R1", "nom": "Hugo", "position": [0, 2]})
        chemin = self.ecrire_json("carte.json", carte)
        with self.assertRaisesRegex(ErreurFichier, "en double detecte"):
            charger_carte(chemin)

    # --- TESTS ARMOIRE ---
    def test_armoire_valide(self):
        chemin = self.ecrire_json("armoire.json", ARMOIRE_BASE)
        charger_armoire(chemin)

    def test_armoire_casier_depart_hors_limite(self):
        armoire = deepcopy(ARMOIRE_BASE)
        armoire["casier_depart"] = [5, 5]
        chemin = self.ecrire_json("armoire.json", armoire)
        with self.assertRaisesRegex(ErreurFichier, "casier_depart hors des dimensions"):
            charger_armoire(chemin)

    def test_armoire_casier_doublon(self):
        armoire = deepcopy(ARMOIRE_BASE)
        # Le deuxième casier est mis à la même position que le premier
        armoire["casiers"][1]["ligne"] = 0
        armoire["casiers"][1]["colonne"] = 0
        chemin = self.ecrire_json("armoire.json", armoire)
        with self.assertRaisesRegex(ErreurFichier, "casier en double"):
            charger_armoire(chemin)

    def test_armoire_etiquette_incoherente(self):
        armoire = deepcopy(ARMOIRE_BASE)
        # On dit que le casier à la colonne 0 (joie) est de la tristesse
        armoire["casiers"][0]["emotion"] = "tristesse"
        chemin = self.ecrire_json("armoire.json", armoire)
        with self.assertRaisesRegex(ErreurFichier, "l'etiquette emotion 'tristesse' ne correspond pas a la colonne 0"):
            charger_armoire(chemin)

    # --- TESTS DICTIONNAIRE ---
    def test_dictionnaire_valide(self):
        chemin = self.ecrire_json("dict.json", DICTIONNAIRE_BASE)
        charger_dictionnaire(chemin)

    def test_dictionnaire_emotion_inconnue(self):
        dico = deepcopy(DICTIONNAIRE_BASE)
        dico["entrees"][0]["emotion"] = "colere" # Non déclaré dans 'emotions'
        chemin = self.ecrire_json("dict.json", dico)
        with self.assertRaisesRegex(ErreurFichier, "emotion inconnue dans les entrees : colere"):
            charger_dictionnaire(chemin)

    def test_dictionnaire_mot_doublon(self):
        dico = deepcopy(DICTIONNAIRE_BASE)
        # Le mot "pleure" est ajouté dans la catégorie joie
        dico["entrees"][0]["formes"].append("pleure")
        chemin = self.ecrire_json("dict.json", dico)
        with self.assertRaisesRegex(ErreurFichier, "present dans plusieurs entrees"):
            charger_dictionnaire(chemin)

    # --- TESTS SCENARIO ---
    def test_scenario_valide(self):
        chemin = self.ecrire_json("scenario.json", SCENARIO_BASE)
        charger_scenario(chemin)

    def test_scenario_mauvaise_carte(self):
        scenario = deepcopy(SCENARIO_BASE)
        scenario["carte"] = "mauvaise_carte"
        chemin = self.ecrire_json("scenario.json", scenario)
        with self.assertRaisesRegex(ErreurFichier, "incompatible avec la carte"):
            charger_scenario(chemin)

    def test_scenario_resident_inconnu(self):
        scenario = deepcopy(SCENARIO_BASE)
        scenario["demandes"][0]["resident"] = "R99" # N'existe pas sur CARTE_BASE
        chemin = self.ecrire_json("scenario.json", scenario)
        with self.assertRaisesRegex(ErreurFichier, "adressee a un resident absent"):
            charger_scenario(chemin)


if __name__ == '__main__':
    unittest.main()
