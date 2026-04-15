"""
Gestionnaire de Liste de Courses
====================================
Selectionnez vos recettes de la semaine et obtenez une liste de courses
compilee, dedoublonnee et prete a exporter vers Samsung Notes.
"""

import json
import os
import subprocess
import sys

# Forcer l'encodage UTF-8 sur Windows pour supporter les emojis et caractères spéciaux
if sys.platform == "win32":
    os.system("")  # Active le support ANSI/VT100 sur Windows 10+
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
from collections import defaultdict
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))
FICHIER_RECETTES = os.path.join(DOSSIER_PROJET, "recettes.json")
FICHIER_EXPORT = os.path.join(DOSSIER_PROJET, "liste_courses.txt")
NOM_PROJET = "Liste_Course"
GITHUB_REMOTE = "https://github.com/ryzuud/Liste_Course.git"


# ─── Couleurs terminal ───────────────────────────────────────────────────────

class Couleurs:
    """Codes ANSI pour colorer le terminal (désactivé si non supporté)."""
    SUPPORT = sys.stdout.isatty()

    RESET = "\033[0m" if SUPPORT else ""
    GRAS = "\033[1m" if SUPPORT else ""
    DIM = "\033[2m" if SUPPORT else ""

    VERT = "\033[92m" if SUPPORT else ""
    BLEU = "\033[94m" if SUPPORT else ""
    JAUNE = "\033[93m" if SUPPORT else ""
    CYAN = "\033[96m" if SUPPORT else ""
    ROUGE = "\033[91m" if SUPPORT else ""
    MAGENTA = "\033[95m" if SUPPORT else ""


C = Couleurs


# ─── Fonctions utilitaires ────────────────────────────────────────────────────

def charger_recettes() -> list[dict]:
    """Charge les recettes depuis le fichier JSON."""
    try:
        with open(FICHIER_RECETTES, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("recettes", [])
    except FileNotFoundError:
        print(f"{C.ROUGE}❌ Fichier '{FICHIER_RECETTES}' introuvable.{C.RESET}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{C.ROUGE}❌ Erreur de lecture JSON : {e}{C.RESET}")
        sys.exit(1)


def afficher_banniere():
    """Affiche la bannière du programme."""
    print()
    print(f"{C.CYAN}{C.GRAS}╔══════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}{C.GRAS}║     🛒  GESTIONNAIRE DE LISTE DE COURSES  🛒    ║{C.RESET}")
    print(f"{C.CYAN}{C.GRAS}╚══════════════════════════════════════════════════╝{C.RESET}")
    print()


def afficher_menu_principal():
    """Affiche le menu principal."""
    print(f"{C.GRAS}{'─' * 50}{C.RESET}")
    print(f"{C.BLEU}{C.GRAS}  MENU PRINCIPAL{C.RESET}")
    print(f"{C.GRAS}{'─' * 50}{C.RESET}")
    print(f"  {C.JAUNE}1.{C.RESET} 📋  Voir toutes les recettes")
    print(f"  {C.JAUNE}2.{C.RESET} ✅  Sélectionner les recettes de la semaine")
    print(f"  {C.JAUNE}3.{C.RESET} 📝  Générer la liste de courses")
    print(f"  {C.JAUNE}4.{C.RESET} ➕  Ajouter une nouvelle recette")
    print(f"  {C.JAUNE}5.{C.RESET} 🗑️   Supprimer une recette")
    print(f"  {C.JAUNE}0.{C.RESET} 🚪  Quitter")
    print(f"{C.GRAS}{'─' * 50}{C.RESET}")


def afficher_recettes(recettes: list[dict]):
    """Affiche la liste de toutes les recettes disponibles."""
    print()
    print(f"{C.GRAS}{C.BLEU}  📖 RECETTES DISPONIBLES ({len(recettes)}){C.RESET}")
    print(f"  {'─' * 46}")
    for i, recette in enumerate(recettes, 1):
        nb_ing = len(recette["ingredients"])
        portions = recette.get("portions", "?")
        print(f"  {C.JAUNE}{i:>2}.{C.RESET} {C.GRAS}{recette['nom']}{C.RESET}")
        print(f"      {C.DIM}{nb_ing} ingrédients · {portions} portions{C.RESET}")
    print()


def afficher_detail_recette(recette: dict):
    """Affiche le détail d'une recette avec ses ingrédients."""
    print()
    print(f"  {C.GRAS}{C.MAGENTA}🍽️  {recette['nom']}{C.RESET}")
    print(f"  {C.DIM}Portions : {recette.get('portions', '?')}{C.RESET}")
    print(f"  {'─' * 40}")
    for ing in recette["ingredients"]:
        print(f"    • {ing['nom']}: {C.CYAN}{ing['quantite']} {ing['unite']}{C.RESET}")
    print()


def selectionner_recettes(recettes: list[dict]) -> list[dict]:
    """Permet à l'utilisateur de sélectionner les recettes de la semaine."""
    print()
    print(f"{C.GRAS}{C.VERT}  ✅ SÉLECTION DES RECETTES DE LA SEMAINE{C.RESET}")
    print(f"  {'─' * 46}")
    print()

    # Afficher les recettes numérotées
    for i, recette in enumerate(recettes, 1):
        print(f"  {C.JAUNE}{i:>2}.{C.RESET} {recette['nom']} {C.DIM}({recette.get('portions', '?')} portions){C.RESET}")
    print()

    print(f"  {C.DIM}Entrez les numéros des recettes séparés par des virgules.{C.RESET}")
    print(f"  {C.DIM}Exemple : 1, 3, 5{C.RESET}")
    print()

    while True:
        choix = input(f"  {C.CYAN}Votre sélection ▸ {C.RESET}").strip()
        if not choix:
            print(f"  {C.ROUGE}⚠ Veuillez entrer au moins un numéro.{C.RESET}")
            continue

        try:
            indices = [int(x.strip()) for x in choix.split(",")]
            selection = []
            invalides = []

            for idx in indices:
                if 1 <= idx <= len(recettes):
                    selection.append(recettes[idx - 1])
                else:
                    invalides.append(idx)

            if invalides:
                print(f"  {C.ROUGE}⚠ Numéros invalides ignorés : {invalides}{C.RESET}")

            if not selection:
                print(f"  {C.ROUGE}⚠ Aucune recette valide sélectionnée, réessayez.{C.RESET}")
                continue

            # Confirmation
            print()
            print(f"  {C.VERT}Recettes sélectionnées :{C.RESET}")
            for r in selection:
                print(f"    {C.VERT}✓{C.RESET} {r['nom']}")
            print()

            confirm = input(f"  {C.CYAN}Confirmer ? (O/n) ▸ {C.RESET}").strip().lower()
            if confirm in ("", "o", "oui", "y", "yes"):
                return selection
            else:
                print(f"  {C.JAUNE}↩ Reprenons la sélection...{C.RESET}")
                print()

        except ValueError:
            print(f"  {C.ROUGE}⚠ Format invalide. Utilisez des numéros séparés par des virgules.{C.RESET}")


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

        liste_finale.append({
            "nom": nom_affiche,
            "quantite": quantite,
            "unite": unite,
        })

    return liste_finale


def afficher_liste_courses(liste: list[dict], selection: list[dict]):
    """Affiche la liste de courses compilée dans le terminal."""
    print()
    print(f"{C.GRAS}{C.CYAN}╔══════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.GRAS}{C.CYAN}║          🛒  LISTE DE COURSES  🛒               ║{C.RESET}")
    print(f"{C.GRAS}{C.CYAN}╚══════════════════════════════════════════════════╝{C.RESET}")
    print()

    # Résumé des recettes
    print(f"  {C.GRAS}Recettes pour la semaine :{C.RESET}")
    for r in selection:
        print(f"    {C.VERT}•{C.RESET} {r['nom']}")
    print()
    print(f"  {C.GRAS}{'─' * 46}{C.RESET}")
    print(f"  {C.GRAS}{len(liste)} ingrédients au total{C.RESET}")
    print(f"  {C.GRAS}{'─' * 46}{C.RESET}")
    print()

    # Liste des ingrédients
    for ing in liste:
        print(f"    ☐ {ing['nom']:<30} {C.CYAN}{ing['quantite']} {ing['unite']}{C.RESET}")

    print()


def generer_texte_export(liste: list[dict], selection: list[dict]) -> str:
    """Génère le texte formaté pour l'export (Samsung Notes / fichier texte)."""
    date = datetime.now().strftime("%d/%m/%Y")
    lignes = []

    lignes.append("🛒 LISTE DE COURSES")
    lignes.append(f"📅 Semaine du {date}")
    lignes.append("")
    lignes.append("━" * 35)
    lignes.append("📖 Recettes prévues :")
    for r in selection:
        lignes.append(f"  • {r['nom']}")
    lignes.append("━" * 35)
    lignes.append("")
    lignes.append(f"📝 {len(liste)} articles à acheter :")
    lignes.append("")

    for ing in liste:
        lignes.append(f"☐ {ing['nom']} — {ing['quantite']} {ing['unite']}")

    lignes.append("")
    lignes.append("━" * 35)
    lignes.append("Bon shopping ! 🛍️")

    return "\n".join(lignes)


def copier_presse_papiers(texte: str) -> bool:
    """Copie le texte dans le presse-papiers (Windows)."""
    try:
        import subprocess
        process = subprocess.Popen(
            ["clip.exe"],
            stdin=subprocess.PIPE,
            encoding="utf-16-le",  # clip.exe attend de l'UTF-16 LE sur Windows
        )
        # clip.exe sur Windows attend du texte via stdin
        process.communicate(input=texte)
        return process.returncode == 0
    except Exception:
        return False


def exporter_fichier(texte: str) -> str:
    """Exporte la liste dans un fichier texte."""
    with open(FICHIER_EXPORT, "w", encoding="utf-8") as f:
        f.write(texte)
    return FICHIER_EXPORT


def menu_export(liste: list[dict], selection: list[dict]):
    """Menu d'export de la liste de courses."""
    texte = generer_texte_export(liste, selection)

    print(f"  {C.GRAS}{C.MAGENTA}📤 OPTIONS D'EXPORT{C.RESET}")
    print(f"  {'─' * 40}")
    print(f"  {C.JAUNE}1.{C.RESET} 📋  Copier dans le presse-papiers (pour Samsung Notes)")
    print(f"  {C.JAUNE}2.{C.RESET} 💾  Exporter en fichier texte (.txt)")
    print(f"  {C.JAUNE}3.{C.RESET} 📋 + 💾  Les deux !")
    print(f"  {C.JAUNE}0.{C.RESET} ↩   Retour")
    print()

    choix = input(f"  {C.CYAN}Votre choix ▸ {C.RESET}").strip()

    if choix in ("1", "3"):
        if copier_presse_papiers(texte):
            print(f"\n  {C.VERT}✅ Liste copiée dans le presse-papiers !{C.RESET}")
            print(f"  {C.DIM}→ Ouvrez Samsung Notes et collez (Ctrl+V){C.RESET}")
        else:
            print(f"\n  {C.ROUGE}❌ Impossible de copier dans le presse-papiers.{C.RESET}")
            print(f"  {C.DIM}→ Utilisez plutôt l'export fichier.{C.RESET}")

    if choix in ("2", "3"):
        chemin = exporter_fichier(texte)
        print(f"\n  {C.VERT}✅ Liste exportée vers :{C.RESET}")
        print(f"  {C.CYAN}{chemin}{C.RESET}")
        print(f"  {C.DIM}→ Ouvrez ce fichier avec Samsung Notes ou partagez-le.{C.RESET}")

    if choix == "0":
        return

    print()


def ajouter_recette(recettes: list[dict]) -> list[dict]:
    """Permet d'ajouter une nouvelle recette au fichier JSON."""
    print()
    print(f"  {C.GRAS}{C.VERT}➕ AJOUTER UNE NOUVELLE RECETTE{C.RESET}")
    print(f"  {'─' * 40}")
    print()

    nom = input(f"  {C.CYAN}Nom de la recette ▸ {C.RESET}").strip()
    if not nom:
        print(f"  {C.ROUGE}⚠ Nom invalide, abandon.{C.RESET}")
        return recettes

    while True:
        try:
            portions = int(input(f"  {C.CYAN}Nombre de portions ▸ {C.RESET}").strip())
            break
        except ValueError:
            print(f"  {C.ROUGE}⚠ Entrez un nombre entier.{C.RESET}")

    ingredients = []
    print()
    print(f"  {C.DIM}Ajoutez les ingrédients un par un. Tapez 'fin' pour terminer.{C.RESET}")
    print()

    while True:
        nom_ing = input(f"    {C.JAUNE}Ingrédient ▸ {C.RESET}").strip()
        if nom_ing.lower() in ("fin", "stop", ""):
            if not ingredients:
                print(f"  {C.ROUGE}⚠ Ajoutez au moins un ingrédient.{C.RESET}")
                continue
            break

        while True:
            try:
                quantite = float(input(f"    {C.JAUNE}Quantité ▸ {C.RESET}").strip())
                break
            except ValueError:
                print(f"    {C.ROUGE}⚠ Entrez un nombre.{C.RESET}")

        unite = input(f"    {C.JAUNE}Unité (g, ml, pièce(s), c. à soupe...) ▸ {C.RESET}").strip()
        if not unite:
            unite = "pièce(s)"

        ingredients.append({
            "nom": nom_ing,
            "quantite": quantite if quantite != int(quantite) else int(quantite),
            "unite": unite,
        })
        print(f"    {C.VERT}✓ {nom_ing} ajouté{C.RESET}")
        print()

    nouvelle_recette = {
        "nom": nom,
        "portions": portions,
        "ingredients": ingredients,
    }

    recettes.append(nouvelle_recette)
    sauvegarder_recettes(recettes)
    print(f"\n  {C.VERT}✅ Recette « {nom} » ajoutée avec succès !{C.RESET}")
    print()
    return recettes


def supprimer_recette(recettes: list[dict]) -> list[dict]:
    """Permet de supprimer une recette existante."""
    print()
    print(f"  {C.GRAS}{C.ROUGE}🗑️  SUPPRIMER UNE RECETTE{C.RESET}")
    print(f"  {'─' * 40}")
    print()

    for i, recette in enumerate(recettes, 1):
        print(f"  {C.JAUNE}{i:>2}.{C.RESET} {recette['nom']}")
    print()

    try:
        choix = int(input(f"  {C.CYAN}Numéro à supprimer (0 = annuler) ▸ {C.RESET}").strip())
        if choix == 0:
            return recettes
        if 1 <= choix <= len(recettes):
            nom = recettes[choix - 1]["nom"]
            confirm = input(f"  {C.ROUGE}Supprimer « {nom} » ? (o/N) ▸ {C.RESET}").strip().lower()
            if confirm in ("o", "oui", "y", "yes"):
                recettes.pop(choix - 1)
                sauvegarder_recettes(recettes)
                print(f"\n  {C.VERT}✅ Recette « {nom} » supprimée.{C.RESET}")
            else:
                print(f"  {C.JAUNE}↩ Annulé.{C.RESET}")
        else:
            print(f"  {C.ROUGE}⚠ Numéro invalide.{C.RESET}")
    except ValueError:
        print(f"  {C.ROUGE}⚠ Entrée invalide.{C.RESET}")

    print()
    return recettes


def sauvegarder_recettes(recettes: list[dict]):
    """Sauvegarde les recettes dans le fichier JSON."""
    data = {"recettes": recettes}
    with open(FICHIER_RECETTES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Automatisation Git ──────────────────────────────────────────────────────

def _run_git(*args: str) -> subprocess.CompletedProcess:
    """Exécute une commande git dans le dossier du projet."""
    return subprocess.run(
        ["git"] + list(args),
        cwd=DOSSIER_PROJET,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def git_auto_push():
    """
    Automatisation Git :
    1. Vérifie / initialise le dépôt Git
    2. Vérifie / configure le remote origin
    3. git add . → git commit → git push origin main
    """
    print()
    print(f"{C.GRAS}{'─' * 50}{C.RESET}")
    print(f"{C.BLEU}{C.GRAS}  🔄 AUTOMATISATION GIT{C.RESET}")
    print(f"{C.GRAS}{'─' * 50}{C.RESET}")
    print()

    # ── Étape 1 : Vérifier / initialiser le dépôt ─────────────────────────
    result = _run_git("rev-parse", "--is-inside-work-tree")
    if result.returncode != 0:
        print(f"  {C.JAUNE}📁 Aucun dépôt Git détecté. Initialisation...{C.RESET}")
        result = _run_git("init")
        if result.returncode != 0:
            print(f"  {C.ROUGE}❌ Échec de git init : {result.stderr.strip()}{C.RESET}")
            return
        # S'assurer qu'on est sur la branche main
        _run_git("branch", "-M", "main")
        print(f"  {C.VERT}✅ Dépôt Git initialisé sur la branche main.{C.RESET}")
    else:
        print(f"  {C.VERT}✅ Dépôt Git détecté.{C.RESET}")

    # ── Étape 2 : Vérifier / configurer le remote origin ──────────────────
    result = _run_git("remote", "get-url", "origin")
    if result.returncode != 0:
        # Pas de remote origin → l'ajouter
        print(f"  {C.JAUNE}🔗 Ajout du remote origin → {GITHUB_REMOTE}{C.RESET}")
        result = _run_git("remote", "add", "origin", GITHUB_REMOTE)
        if result.returncode != 0:
            print(f"  {C.ROUGE}❌ Échec de l'ajout du remote : {result.stderr.strip()}{C.RESET}")
            return
        print(f"  {C.VERT}✅ Remote origin ajouté.{C.RESET}")
    else:
        url_actuelle = result.stdout.strip()
        if url_actuelle != GITHUB_REMOTE:
            print(f"  {C.JAUNE}🔗 Mise à jour du remote origin :{C.RESET}")
            print(f"     {C.DIM}{url_actuelle} → {GITHUB_REMOTE}{C.RESET}")
            _run_git("remote", "set-url", "origin", GITHUB_REMOTE)
            print(f"  {C.VERT}✅ Remote origin mis à jour.{C.RESET}")
        else:
            print(f"  {C.VERT}✅ Remote origin correctement configuré.{C.RESET}")

    # ── Étape 3 : git add . ───────────────────────────────────────────────
    print(f"\n  {C.CYAN}📦 Ajout des fichiers modifiés...{C.RESET}")
    result = _run_git("add", ".")
    if result.returncode != 0:
        print(f"  {C.ROUGE}❌ Échec de git add : {result.stderr.strip()}{C.RESET}")
        return

    # Vérifier s'il y a quelque chose à commiter
    result = _run_git("diff", "--cached", "--quiet")
    if result.returncode == 0:
        print(f"  {C.JAUNE}ℹ️  Aucune modification à commiter.{C.RESET}")
        print(f"  {C.DIM}Le dépôt est déjà à jour.{C.RESET}")
        return

    # ── Étape 4 : git commit ──────────────────────────────────────────────
    message_commit = f"Mise à jour automatique - {NOM_PROJET}"
    print(f"  {C.CYAN}💬 Commit : \"{message_commit}\"...{C.RESET}")
    result = _run_git("commit", "-m", message_commit)
    if result.returncode != 0:
        print(f"  {C.ROUGE}❌ Échec de git commit : {result.stderr.strip()}{C.RESET}")
        return
    print(f"  {C.VERT}✅ Commit effectué.{C.RESET}")

    # ── Étape 5 : git push origin main ────────────────────────────────────
    print(f"  {C.CYAN}🚀 Push vers origin/main...{C.RESET}")
    result = _run_git("push", "-u", "origin", "main")
    if result.returncode != 0:
        stderr = result.stderr.strip()
        print(f"\n  {C.ROUGE}❌ Échec du push :{C.RESET}")
        print(f"  {C.ROUGE}{stderr}{C.RESET}")
        if "rejected" in stderr:
            print(f"\n  {C.JAUNE}💡 Astuce : essayez 'git pull --rebase origin main' puis relancez.{C.RESET}")
        elif "Could not resolve host" in stderr or "unable to access" in stderr:
            print(f"\n  {C.JAUNE}💡 Vérifiez votre connexion internet et l'URL du dépôt.{C.RESET}")
        elif "Authentication" in stderr or "403" in stderr:
            print(f"\n  {C.JAUNE}💡 Vérifiez votre authentification GitHub (token / SSH).{C.RESET}")
        return

    print(f"\n  {C.VERT}{C.GRAS}✅ Push réussi ! Dépôt GitHub mis à jour.{C.RESET}")
    print(f"  {C.DIM}→ https://github.com/ryzuud/Liste_Course{C.RESET}")
    print()


# ─── Boucle principale ───────────────────────────────────────────────────────

def main():
    """Point d'entrée du programme."""
    recettes = charger_recettes()
    selection_courante = []
    liste_courante = []

    afficher_banniere()

    while True:
        afficher_menu_principal()
        choix = input(f"\n  {C.CYAN}Votre choix ▸ {C.RESET}").strip()

        if choix == "1":
            afficher_recettes(recettes)
            # Proposer de voir le détail d'une recette
            detail = input(f"  {C.DIM}Voir le détail d'une recette ? (numéro ou Entrée) ▸ {C.RESET}").strip()
            if detail.isdigit() and 1 <= int(detail) <= len(recettes):
                afficher_detail_recette(recettes[int(detail) - 1])

        elif choix == "2":
            selection_courante = selectionner_recettes(recettes)
            # Compiler automatiquement
            liste_courante = compiler_ingredients(selection_courante)
            print(f"  {C.VERT}✅ {len(selection_courante)} recette(s) sélectionnée(s), "
                  f"{len(liste_courante)} ingrédients compilés.{C.RESET}")
            print()

        elif choix == "3":
            if not selection_courante:
                print(f"\n  {C.ROUGE}⚠ Sélectionnez d'abord des recettes (option 2).{C.RESET}\n")
                continue
            afficher_liste_courses(liste_courante, selection_courante)
            menu_export(liste_courante, selection_courante)

        elif choix == "4":
            recettes = ajouter_recette(recettes)

        elif choix == "5":
            recettes = supprimer_recette(recettes)

        elif choix == "0":
            print(f"\n  {C.VERT}👋 À bientôt et bon appétit !{C.RESET}\n")
            return True  # Exécution réussie

        else:
            print(f"\n  {C.ROUGE}⚠ Choix invalide, réessayez.{C.RESET}\n")

    return True  # Ne devrait pas arriver, mais considéré comme succès


if __name__ == "__main__":
    try:
        succes = main()
        if succes:
            git_auto_push()
    except KeyboardInterrupt:
        print(f"\n\n  {C.JAUNE}⚠ Interruption clavier. Au revoir !{C.RESET}\n")
    except Exception as e:
        print(f"\n  {C.ROUGE}❌ Erreur inattendue : {e}{C.RESET}")
        print(f"  {C.ROUGE}Le push Git n'a pas été effectué.{C.RESET}\n")
