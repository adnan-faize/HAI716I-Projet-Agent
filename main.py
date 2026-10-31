"""
Entrypoint du projet

python3 main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>
"""

import os
import sys
import time
from pathlib import Path

import reconfort_io as rio
from monde import ActionIllegale, Monde
from robot import Robot


def afficher_grille(monde: Monde, robot: Robot):
    print()
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


def actualiser_affichage(monde: Monde, robot: Robot, nouveaux_messages: list[str] | None = None, premiere_fois: bool = False):
    lignes_grille = robot.hauteur + 2

    if not premiere_fois:
        print(f"\033[{lignes_grille}F\033[J", end="")

    if nouveaux_messages:
        for msg in nouveaux_messages:
            print(msg)

    afficher_grille(monde, robot)
    time.sleep(0.5)


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

    # compatibilite windows pour codes ansi
    if os.name == 'nt':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # -11 correspond à STD_OUTPUT_HANDLE
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        # 0x0004 correspond à ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)

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
    print("-"*60)
    print()

    try:
        trace = rio.Trace(nom_carte=carte["nom"], nom_scenario=scenario["nom"], equipe=["FAIZE Adnan", "SELMI Eya"])
        monde = Monde(carte, armoire)
        robot = Robot(carte, armoire, dictionnaire, trace)

        actualiser_affichage(monde, robot, ["--- DEBUT DE LA SIMULATION ---"], True)

        def callback_affichage(messages_supplementaires: list[str] | None):
            actualiser_affichage(monde, robot, messages_supplementaires, premiere_fois=False)

        for demande in scenario["demandes"]:
            robot.traiter_demande(monde, demande, actualiser_affichage=callback_affichage)

        trace.ecrire(chemin_trace)
        print()
        print(f"[FIN] trace ecrite : {chemin_trace}")
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
