"""
Shared utilities for the Grocery List Manager.
"""

import json
import os
import subprocess
from collections import defaultdict

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")


def charger_recettes() -> list[dict]:
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
    """Compile et dédoublonne les ingrédients des recettes sélectionnées."""
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    noms_originaux: dict[tuple[str, str], str] = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            cle = (ing["nom"].lower().strip(), ing["unite"].lower().strip())
            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = ing["nom"]

    liste_finale = []
    for cle, quantite in sorted(comptes.items(), key=lambda x: x[0][0]):
        if quantite == int(quantite):
            quantite = int(quantite)
        liste_finale.append(
            {
                "nom": noms_originaux[cle],
                "quantite": quantite,
                "unite": cle[1],
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
