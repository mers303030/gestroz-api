import subprocess
import time
import sys
import os
import pygetwindow as gw

# CONFIGURATION À MODIFIER
REPERTOIRE = r"S:\Python-Project\Zaer"
FICHIER_BAT = "run.bat"
TITRE_FENETRE = "GESTROZ"   # ← remplacez par le mot clé du titre de la fenêtre de login

def afficher_barre_jusqua_fenetre(titre_contient):
    largeur = 50
    plein = "█"
    vide = "░"
    try:
        cols = os.get_terminal_size().columns
    except:
        cols = 80
    i = 0
    while True:
        fenetres = gw.getWindowsWithTitle(titre_contient)
        if fenetres:
            # Barre à 100% puis sortie
            barre = plein * largeur
            texte = f"[{barre}] 100%"
            marge = max(0, (cols - len(texte)) // 2)
            sys.stdout.write("\r" + " " * marge + texte)
            sys.stdout.flush()
            print()
            break
        rempli = int(largeur * (i % 100) / 100)
        barre = plein * rempli + vide * (largeur - rempli)
        texte = f"[{barre}] {i % 100:3d}%"
        marge = max(0, (cols - len(texte)) // 2)
        sys.stdout.write("\r" + " " * marge + texte)
        sys.stdout.flush()
        i = (i + 1) % 101
        time.sleep(0.05)

def lancer_gestroz():
    chemin_bat = os.path.join(REPERTOIRE, FICHIER_BAT)
    if not os.path.exists(chemin_bat):
        print(f"Erreur : {chemin_bat} introuvable")
        return False
    subprocess.Popen(["cmd", "/c", "start", FICHIER_BAT], cwd=REPERTOIRE, shell=False)
    return True

if __name__ == "__main__":
    print("Lancement de GESTROZ - Zaer\n")
    if lancer_gestroz():
        print("Démarrage de l'application... (barre jusqu'à l'ouverture du menu)")
        afficher_barre_jusqua_fenetre(TITRE_FENETRE)
        print("Menu login détecté.")
    else:
        print("Échec du lancement.")