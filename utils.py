"""
Fonctions utilitaires partagées pour le Gestionnaire de Liste de Courses.
"""

import json
import os
import subprocess
from collections import defaultdict

# ─── Configuration ────────────────────────────────────────────────────────────

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")
NOM_PROJET = "Liste_Course"
GITHUB_REMOTE = "https://github.com/ryzuud/Liste_Course-.git"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def charger_recettes_base() -> list[dict]:
    """Charge les recettes depuis le fichier JSON."""
    with open(FICHIER_RECETTES, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("recettes", [])


def sauvegarder_recettes(recettes: list[dict]):
    """Sauvegarde les recettes dans le fichier JSON."""
    data = {"recettes": recettes}
    with open(FICHIER_RECETTES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compiler_ingredients(selection: list[dict]) -> list[dict]:
    """
    Compile tous les ingrédients des recettes sélectionnées.
    Additionne les quantités des ingrédients communs (même nom + même unité).
    Retourne une liste triée par catégorie implicite (ordre alphabétique).
    """
    # Clé = (nom_normalisé, unité) → quantité cumulée
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    # Garder le nom original (première occurrence) pour l'affichage
    noms_originaux: dict[tuple[str, str], str] = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            cle = (ing["nom"].lower().strip(), ing["unite"].lower().strip())
            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = ing["nom"]

    # Construire la liste finale triée alphabétiquement
    liste_finale = []
    for cle, quantite in sorted(comptes.items(), key=lambda x: x[0][0]):
        nom_affiche = noms_originaux[cle]
        unite = cle[1]

        # Formater la quantité (entier si pas de décimales)
        if quantite == int(quantite):
            quantite = int(quantite)

        liste_finale.append(
            {
                "nom": nom_affiche,
                "quantite": quantite,
                "unite": unite,
            }
        )

    return liste_finale


def _run_git(*args: str) -> subprocess.CompletedProcess:
    """Exécute une commande git dans le dossier du projet."""
    return subprocess.run(
        ["git"] + list(args),
        cwd=DOSSIER_PROJET,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
