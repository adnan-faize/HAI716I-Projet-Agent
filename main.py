"""
Entrypoint du projet

python3 main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>
"""

import sys
from pathlib import Path

import reconfort_io as rio
from robot import Robot


class Agent:
    def __init__(self, carte, armoire, dictionnaire, nom_carte, nom_scenario):
        self.dictionnaire = dictionnaire
        self.armoire = armoire
        self.robot = Robot(carte, armoire)

    def resoudre_scenario(self, monde, demandes, visuel = False):
        for demande in demandes:
            num = demande["numero"]
            res_id = demande["resident"]
            message = demande["message"]

            if visuel:
                print("="*60)
                print(f"Demande {num} pour {res_id} : {message!r}")
                print("="*60)


def resoudre_scenario():
    pass


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]

    if len(args) != 4:
        print("Usage : python main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>", file=sys.stderr)
        return 2

    chemin_carte, chemin_scenario, dossier_donnees, chemin_trace = args
    chemin_carte = Path(chemin_carte)
    chemin_scenario = Path(chemin_scenario)
    dossier_donnees = Path(dossier_donnees)
    chemin_trace = Path(chemin_trace)

    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario, carte=carte)
        dictionnaire = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
        armoire = rio.charger_armoire(dossier_donnees / f"{scenario.get("armoire")}.json")
    except rio.ErreurFichier as err:
        print(f"Erreur de donnees : {err}", file=sys.stderr)
        return 1
    except Exception as err:  # noqa: BLE001
        print(f"Erreur inattendue : {err}", file=sys.stderr)
        return 1

    print(f"carte        : {carte['nom']} "
          f"{carte['dimensions']['hauteur']}x{carte['dimensions']['largeur']}, "
          f"{len(carte['residents'])} residents")
    print(f"scenario     : {scenario['nom']}, "
          f"{len(scenario['demandes'])} demandes")
    print(f"dictionnaire : {len(dictionnaire['entrees'])} entrees")
    print(f"armoire      : {armoire['nom']}, "
          f"{len(armoire['casiers'])} casiers")
    print()
    print(f"depart robot   : {carte['depart_robot']}")
    print(f"armoire        : {carte['armoire']['position']}")
    print(f"dictionnaire   : {carte['dictionnaire']['position']}")
    print(f"casier depart  : {armoire['casier_depart']}")

    trace = rio.Trace(nom_carte=carte["nom"], nom_scenario=scenario["nom"], equipe=["FAIZE Adnan", "SELMI Eya"])


    resoudre_scenario()
    
    trace.ecrire(chemin_trace)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
