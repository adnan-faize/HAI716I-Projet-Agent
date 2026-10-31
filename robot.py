""" 
Ce que le robot sait et comment il décide où aller.
Regroupe la mémoire, la perception, la planification et la prise de décision.
"""

from typing import Any, Callable

from monde import Monde
from planification import DIRECTIONS, direction_entre, plus_court_chemin
from reconfort_io import Trace, normaliser
from roue import INTENSITES, RouePlutchik


class Robot:
    def __init__(self, carte, armoire, dictionnaire, trace):
        self.hauteur = carte["dimensions"]["hauteur"]
        self.largeur = carte["dimensions"]["largeur"]
        self.position = tuple(carte["depart_robot"])

        self.position_armoire = tuple(carte["armoire"]["position"])
        self.position_dictionnaire = tuple(carte["dictionnaire"]["position"])
        self.position_residents = { r["id"]: tuple(r["position"]) for r in carte["residents"] }

        self.dictionnaire = dictionnaire
        self.trace = trace
        self.roue = RouePlutchik()

        # La carte mentale 
        self.carte_mentale = {}
        self.carte_mentale[self.position] = "libre"      # il est dessus
        self.carte_mentale[self.position_armoire] = "armoire"
        self.carte_mentale[self.position_dictionnaire] = "dictionnaire"
        for case in self.position_residents.values():
            self.carte_mentale[case] = "resident"

        if armoire is not None:
            self.position_selecteur = list(armoire.get("casier_depart", [1, 0]))
        else:
            self.position_selecteur = [1, 0]
            
        self.memoire_armoire = {}
        self.objet_main = None

    # ---------- Décision et Analyse

    def analyser_message(self, message: str) -> tuple[str, str] | None:
        """
            Lit émotion et intensite dans le dic selon la sec 6.1
            1. normalise le message
            2. parcourt les mots de gauche à droite
            3. premier mot donne la réponse ; si aucun mot -> emotion indeterminee (None)
        """
        formes_connues: dict[str, tuple[str, str]] = {}
        for entree in self.dictionnaire.get("entrees", []):
            emotion = entree["emotion"]
            intensite = entree["intensite"]
            for forme in entree.get("formes", []):
                formes_connues[forme] = (emotion, intensite)

        mots = normaliser(message)
        for mot in mots:
            if mot in formes_connues:
                return formes_connues[mot]
        return None

    def preparer_candidats_armoire(self, emotion: str, intensite: str) -> list[dict[str, Any]]:
        return self.roue.candidats_repli(emotion, intensite)

    def chemin_selecteur(self, act_pos, target_pos) -> list[str]:
        return self.roue.deplacement_selecteur(act_pos, target_pos)

    # ---------- Memoire

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

    # ---------- La boucle : percevoir -> memoriser -> decider -> agir

    def aller_vers(self, monde, cible, demande_num, actualiser_affichage=None):
        """Déplace le robot jusqu'à côté de `cible`, un pas à la fois."""
        limite = 4 * self.hauteur * self.largeur * self.hauteur * self.largeur

        for _ in range(limite):
            perception = monde.percevoir()               # 1. percevoir
            self.memoriser(perception)                   # 2. memoriser

            if self.position in self.cases_autour(cible):
                return True
            
            direction = self.prochaine_direction(cible)  # 3. decider (BFS)

            if direction == "ARRIVE":
                return True
            if direction is None:
                return False

            # 4. agir
            casier_vue = getattr(monde, "percevoir_casier", lambda: None)()
            self.trace.ajouter_pas(demande=demande_num, position=self.position, casier=list(self.position_selecteur), action="AVANCER", argument=direction, perception=perception, contenu_casier=casier_vue)
            monde.avancer(direction)                     # 4. agir
            dl, dc = DIRECTIONS[direction]               #    et mettre a jour
            self.position = (self.position[0] + dl,      #    sa propre position
                             self.position[1] + dc)

            if actualiser_affichage:
                actualiser_affichage(None)

        raise RuntimeError(f"aller_vers {cible} : le robot tourne en rond")

    # ---------- Traiter demande

    def traiter_demande(self, monde: Monde, demande: dict[str, Any], actualiser_affichage: Callable | None = None):
        num = demande["numero"]
        res_id = demande["resident"]
        message = demande["message"]
        pos_resident = self.position_residents[res_id]

        if actualiser_affichage:
            actualiser_affichage(["", f"Demande {num} pour {res_id} : {message!r}"])

        # ----- Phase 1 : Aller au dictionnaire
        attent_dico = self.aller_vers(monde, self.position_dictionnaire, num, actualiser_affichage)
        if not attent_dico:
            self.trace.ajouter_livraison(demande=num, resident=res_id, emotion=None, INTENSITES=None, casier_choisi=None, repli="aucun", objet=None, success=False, motif_echec="dictionnaire inaccessible")
            return

        # ----- Phase 2 : Consulter le dictionnaire
        perception = monde.percevoir()
        self.memoriser(perception)
        casier_vue = getattr(monde, "percevoir_casier", lambda: None)()
        self.trace.ajouter_pas(demande=num, position=self.position, casier=list(self.position_selecteur), action="CONSULTER", argument=None, perception=perception, contenu_casier=casier_vue, commentaire="Consultation du dictionnaire")
        monde.consulter()
        
        analyse = self.analyser_message(message)
        if analyse is None:
            self.trace.ajouter_livraison(demande=num, resident=res_id, emotion=None, intensite=None, casier_choisi=None, repli="aucun", objet=None, succes=False, motif_echec="emotion indeterminee")
            if actualiser_affichage:
                actualiser_affichage(["\t-> Échec : Émotion indéterminée"])
            return

        emotion, intensite = analyse
        if actualiser_affichage:
            actualiser_affichage([f"\t-> Message compris : émotion={emotion}, intensité={intensite}"])

        # ----- Phase 3 : Rejoindre l'armoire

        # ----- Phase 4 : Fouiller l'armoire (chercher et prendre)
        
        # ----- Phase 5 : Rejoindre le résident
        
        # ----- Phase 6 : Donner l'objet au résident
        
        