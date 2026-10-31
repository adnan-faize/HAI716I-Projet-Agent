# HAI716I -- POA/SMA : Projet Robot Réconfort

###### Par FAIZE Adnan & SELMI Eya

https://github.com/adnan-faize/HAI716I-Projet-Agent

**Langage :** Python 3.9+

Un robot autonome à perception locale se déplace dans un appartement, consulte un dictionnaire pour déduire l'émotion et l'intensité d'un message, fouille une armoire selon la roue des émotions de Plutchik, et livre l'objet de réconfort approprié au résident concerné.

---

## Exécution

```bash
python main.py <chemin_carte> <chemin_scenario> <dossier_donnees> <chemin_trace>
```

### Exemple

```bash
python main.py cartes/appartement_01.json cartes/scenario_01.json donnees sorties/trace_01.json
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Il est également possible d'exécuter chaque suite de test indépendamment :

```bash
python -m unittest tests/test_planification.py -v
python -m unittest tests/test_monde.py -v
python -m unittest tests/test_armoire_roue.py -v
python -m unittest tests/test_reconfort_io.py -v
python -m unittest tests/test_robot.py -v
```

---

## Organisation du code

L'architecture du projet applique une séparation stricte entre **Perception**, **Mémoire**, **Décision** et **Action** :

| Fichier | Rôle architectural | Description |
|---|---|---|
| `main.py` | **Point d'entrée & Orchestration** | Lance le programme, charge les fichiers, anime la console et sauvegarde la trace finale. |
| `robot.py` | **Agent autonome** | Gère la mémoire, l'analyse des textes, le choix des actions et adapte son itinéraire en temps réel. |
| `planification.py` | **Recherche de chemin (BFS)** | Calcule le chemin le plus court (sans murs) grâce à un algorithme maison ultra-rapide. |
| `monde.py` | **Simulateur & Environnement physique** | Cache la vraie carte et les objets. Il donne au robot juste ce qu'il peut voir et punit la triche. |
| `roue.py` | **Roue de Plutchik & Logique de repli** | Gère les émotions (Plutchik) et calcule dans quel ordre de secours (repli) fouiller les casiers. |
| `reconfort_io.py` | **Entrées / Sorties & Validations** | Vérifie que les JSON (cartes, scénarios) n'ont pas d'erreurs, nettoie le texte et écrit la trace. |
| `rendu.json` | **Contrat de rendu** | Contient le nom de l'équipe et la commande pour lancer le projet. |
| `cartes/` | **Environnements de test** | Les différentes cartes des appartements (ex: appartement_01.json) et les scénarios associés. |
| `donnees/` | **Données statiques** | Le dictionnaire de vocabulaire (émotions) et l'armoire avec les objets. |
| `tests/` | **Tests automatisés** | Les tests pour vérifier que le code fonctionne. |

---

## État

### Ce qui marche

- Zéro triche : Le robot utilise uniquement ses capteurs et ne lit pas les données secrètes.
- Cycle complet : Le robot gère tout de A à Z (lecture, recherche, livraison).
- Navigation adaptative : Il crée sa carte mentale et esquive les murs en temps réel.
- Règle de repli : En cas de casier vide, il trouve la meilleure alternative selon les règles.
- Mouvements de l'armoire : Le sélecteur boucle parfaitement sur les bords Est/Ouest.
- Analyse des messages : Le nettoyage du texte et la détection d'émotion sont opérationnels.
- Contrôle des fichiers : Les mauvaises données (erreurs de carte/scénario) sont bloquées proprement.
- Fichier trace : Génération d'un trace.json parfait et conforme.
- Interface : L'affichage en console est fluide et animé en temps réel.

### Ce qui ne marche pas

- Recherche non optimisée : Le sélecteur d'armoire fait parfois des déplacements inutiles au lieu d'inspecter en chemin.

---

## Vidéo de démonstration

https://github.com/user-attachments/assets/25c1996e-5990-4315-8a5b-3701f1e20fc7
