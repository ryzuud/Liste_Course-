"""
Serveur web Flask pour le Gestionnaire de Liste de Courses.
Lance l'interface web sur http://localhost:5000
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from liste_courses import git_auto_push

# Forcer UTF-8 sur Windows
if sys.platform == "win32":
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

# ─── Configuration ────────────────────────────────────────────────────────────

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")
NOM_PROJET = "Liste_Course"
GITHUB_REMOTE = "https://github.com/ryzuud/Liste_Course-.git"

app = Flask(__name__, static_folder="static", template_folder="templates")


# ─── Helpers ──────────────────────────────────────────────────────────────────


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


# ─── Routes ───────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    """Page principale."""
    return render_template("index.html")


@app.route("/api/recettes", methods=["GET"])
def api_get_recettes():
    """Retourne toutes les recettes."""
    recettes = charger_recettes()
    return jsonify(recettes)


@app.route("/api/recettes", methods=["POST"])
def api_add_recette():
    """Ajoute une nouvelle recette."""
    nouvelle = request.json
    recettes = charger_recettes()
    recettes.append(nouvelle)
    sauvegarder_recettes(recettes)
    return jsonify({"success": True, "count": len(recettes)})


@app.route("/api/recettes/<int:idx>", methods=["DELETE"])
def api_delete_recette(idx):
    """Supprime une recette par index."""
    recettes = charger_recettes()
    if 0 <= idx < len(recettes):
        supprimee = recettes.pop(idx)
        sauvegarder_recettes(recettes)
        return jsonify({"success": True, "deleted": supprimee["nom"]})
    return jsonify({"success": False, "error": "Index invalide"}), 400


@app.route("/api/compiler", methods=["POST"])
def api_compiler():
    """Compile la liste de courses à partir des indices de recettes sélectionnées."""
    indices = request.json.get("indices", [])
    recettes = charger_recettes()
    selection = [recettes[i] for i in indices if 0 <= i < len(recettes)]

    if not selection:
        return jsonify({"success": False, "error": "Aucune recette sélectionnée"}), 400

    liste = compiler_ingredients(selection)
    noms_recettes = [r["nom"] for r in selection]

    # Générer le texte d'export
    date = datetime.now().strftime("%d/%m/%Y")
    lignes = [
        "🛒 LISTE DE COURSES",
        f"📅 Semaine du {date}",
        "",
        "━" * 35,
        "📖 Recettes prévues :",
    ]
    for nom in noms_recettes:
        lignes.append(f"  • {nom}")
    lignes.extend(
        [
            "━" * 35,
            "",
            f"📝 {len(liste)} articles à acheter :",
            "",
        ]
    )
    for ing in liste:
        lignes.append(f"☐ {ing['nom']} — {ing['quantite']} {ing['unite']}")
    lignes.extend(["", "━" * 35, "Bon shopping ! 🛍️"])

    return jsonify(
        {
            "success": True,
            "liste": liste,
            "recettes": noms_recettes,
            "texte_export": "\n".join(lignes),
        }
    )


@app.route("/api/git-push", methods=["POST"])
def api_git_push():
    """Lance l'automatisation Git."""
    result = git_auto_push()
    return jsonify(result)


# ─── Lancement ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  [*] Interface web disponible sur : http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
