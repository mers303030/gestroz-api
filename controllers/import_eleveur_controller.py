import openpyxl
from datetime import datetime
from database.db_session import SessionLocal
from database.models.eleveur import Eleveur

def importer_eleveurs_depuis_excel(file_path):
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    db = SessionLocal()
    lignes_importees = 0
    erreurs = []

    # On suppose que la ligne 1 contient les en-têtes (on la saute)
    # Les données commencent à la ligne 2
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not row or len(row) < 8:
            continue
        # Extraction par position (0-indexé)
        code = str(row[0]).strip() if row[0] else None
        if not code:
            erreurs.append(f"Ligne {row_idx}: code_elevage manquant")
            continue
        nom = str(row[1]).strip() if row[1] else ''
        prenom = str(row[2]).strip() if row[2] else ''
        niveau = str(row[4]).strip() if row[4] else ''
        cnie = str(row[5]).strip() if row[5] else ''
        tel_raw = str(row[6]).strip() if row[6] else ''
        commune_raw = str(row[7]).strip() if row[7] else ''

        # Nettoyage téléphone : convertir les chaînes vides en None
        tel = ''.join(filter(str.isdigit, tel_raw))
        if not tel:
            tel = None  # ← Correction : remplacer la chaîne vide par None
        elif len(tel) != 10:
            erreurs.append(f"Ligne {row_idx}: téléphone invalide ({tel_raw}) pour {code}")
            continue

        # Normalisation commune
        commune = "Boukchmir" if commune_raw == "Bouikchmir" else commune_raw

        # Conversion date (identique au code précédent)
        date_val = row[3]
        if not date_val:
            erreurs.append(f"Ligne {row_idx}: date de naissance manquante pour {code}")
            continue
        try:
            if isinstance(date_val, datetime):
                date_naissance = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val).strip()
                for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                    try:
                        date_naissance = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                        break
                    except:
                        continue
                else:
                    raise ValueError(f"Format non reconnu: {date_str}")
        except Exception as e:
            erreurs.append(f"Ligne {row_idx}: date invalide {date_val} pour {code} - {e}")
            continue

        # Vérifier unicité CNIE et téléphone
        if cnie and db.query(Eleveur).filter(Eleveur.cnie == cnie).first():
            erreurs.append(f"Ligne {row_idx}: CNIE {cnie} déjà existant pour {code}")
            continue
        if tel and db.query(Eleveur).filter(Eleveur.telephone == tel).first():
            erreurs.append(f"Ligne {row_idx}: Téléphone {tel} déjà existant pour {code}")
            continue

        # Création ou mise à jour
        eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == code).first()
        if eleveur:
            eleveur.nom = nom
            eleveur.prenom = prenom
            eleveur.date_naissance = date_naissance
            eleveur.niveau_scolaire = niveau
            eleveur.cnie = cnie
            eleveur.telephone = tel
            eleveur.commune = commune
        else:
            eleveur = Eleveur(
                code_elevage=code,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                niveau_scolaire=niveau,
                cnie=cnie,
                telephone=tel,
                commune=commune
            )
            db.add(eleveur)
        lignes_importees += 1

    db.commit()
    db.close()
    return lignes_importees, erreurs