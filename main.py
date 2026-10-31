"""
Entrypoint du projet

python3 main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>
"""

import sys
from pathlib import Path
from typing import Any

import reconfort_io as rio
from monde import ActionIllegale, Monde
from robot import Robot


def afficher_grille(monde: Monde, robot: Robot, demandes_actions: list[tuple[str, list[str]]] | None = None, is_finished: bool = False):
    print("\033[u\033[J", end="") # restore cursor (\033[u) and clear everything below it (\033[J)
    l_r, c_r = robot.position
    for l in range(robot.hauteur):
        ligne = []
        for c in range(robot.largeur):
            if (l, c) == (l_r, c_r):
                ligne.append("R")
            else:
                case_reelle = monde._grille[l][c]
                ligne.append(case_reelle)
        print(" ".join(ligne))
    print(f"Position robot : {robot.position} | Objet : {robot.objet_main}")
    if demandes_actions is None:
        return
    print()
    for d_index, demande_actions in enumerate(demandes_actions):
        print(f"[{"DONE" if d_index < len(demandes_actions) and not is_finished else "    "}] {demande_actions[0]}") # print de la demande
        for action in demande_actions[1]:
            print(f"       -> {action}") # print des actions effectuées par le robot        


def traiter_demande(monde: Monde, robot: Robot, trace: rio.Trace, demande: dict[str, Any], prev_demandes_actions: list[tuple[str, list[str]]]):
    num = demande["numero"]
    res_id = demande["resident"]
    message = demande["message"]
    pos_res = robot.position_residents[res_id]

    prev_demandes_actions.append((f"Demande {num} pour {res_id} : {message!r}", []))

    afficher_grille(monde, robot, prev_demandes_actions)
    


def main(argv):
    if len(argv) != 5:
        print("Usage : python main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>", file=sys.stderr)
        return 2

    chemin_carte, chemin_scenario, dossier_donnees, chemin_trace = Path(argv[1]), Path(argv[2]), Path(argv[3]), Path(argv[4])

    try:
        carte = rio.charger_carte(chemin_carte)
        scenario = rio.charger_scenario(chemin_scenario, carte=carte)
        dictionnaire = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
        armoire = rio.charger_armoire(dossier_donnees / f"{scenario["armoire"]}.json")
    except rio.ErreurFichier as err:
        print(f"Erreur de donnees : {err}", file=sys.stderr)
        return 1
    except Exception as err:  # noqa: BLE001
        print(f"Erreur inattendue : {err}", file=sys.stderr)
        return 1

    # cacher le curseur
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    print(f"carte        : {carte['nom']} {carte['dimensions']['hauteur']}x{carte['dimensions']['largeur']}, {len(carte['residents'])} residents")
    print(f"scenario     : {scenario['nom']}, {len(scenario['demandes'])} demandes")
    print(f"dictionnaire : {len(dictionnaire['entrees'])} entrees")
    print(f"armoire      : {armoire['nom']}, {len(armoire['casiers'])} casiers")
    print()
    print(f"depart robot   : {carte['depart_robot']}")
    print(f"armoire        : {carte['armoire']['position']}")
    print(f"dictionnaire   : {carte['dictionnaire']['position']}")
    print(f"casier depart  : {armoire['casier_depart']}")
    print()

    try:
        print("\033[s", end="") # sauvegarder pos curseur
        
        monde = Monde(carte, armoire)
        robot = Robot(carte, armoire)
        trace = rio.Trace(nom_carte=carte["nom"], nom_scenario=scenario["nom"], equipe=["FAIZE Adnan", "SELMI Eya"])
        prev_demandes_actions = [] # sert uniquement pour le visuel
                                   # au fur et a mesure que le robot complète des demandes, elles sont ajoutées là dedans

        afficher_grille(monde, robot)
    
        for demande in scenario["demandes"]:
            traiter_demande(monde, robot, trace, demande, prev_demandes_actions)

        afficher_grille(monde, robot, prev_demandes_actions, True)
    
        trace.ecrire(chemin_trace)
        print(f"trace ecrite : {chemin_trace}")
    except ActionIllegale as err:
        print(f"Erreur de simulation (action illegale) : {err}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        pass
    finally: 
        # montrer le curseur quand on quite le programme
        sys.stdout.write("\033[?25h") 
        sys.stdout.flush()
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
