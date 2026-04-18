import timeit
from collections import defaultdict
import json
import os

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")

def load_data():
    with open(FICHIER_RECETTES, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("recettes", [])

def test_original(selection):
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    noms_originaux: dict[tuple[str, str], str] = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            cle = (ing["nom"].lower().strip(), ing["unite"].lower().strip())
            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = ing["nom"]

def test_optimized(selection):
    comptes: dict[tuple[str, str], float] = defaultdict(float)
    noms_originaux: dict[tuple[str, str], str] = {}

    cache_nom = {}
    cache_unite = {}

    for recette in selection:
        for ing in recette["ingredients"]:
            nom = ing["nom"]
            unite = ing["unite"]

            nom_norm = cache_nom.get(nom)
            if nom_norm is None:
                nom_norm = nom.lower().strip()
                cache_nom[nom] = nom_norm

            unite_norm = cache_unite.get(unite)
            if unite_norm is None:
                unite_norm = unite.lower().strip()
                cache_unite[unite] = unite_norm

            cle = (nom_norm, unite_norm)

            comptes[cle] += ing["quantite"]
            if cle not in noms_originaux:
                noms_originaux[cle] = nom

data = load_data()
large_data = data * 100

def bench_old():
    test_original(large_data)

def bench_new():
    test_optimized(large_data)

if __name__ == '__main__':
    t_old = timeit.timeit(bench_old, number=100)
    t_new = timeit.timeit(bench_new, number=100)
    print(f"Original: {t_old:.4f}s")
    print(f"Optimized: {t_new:.4f}s")
