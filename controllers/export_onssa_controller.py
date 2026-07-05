# controllers/export_onssa_controller.py
import csv
from database.db_session import SessionLocal
from database.models import Naissance, Vente, Mortalite, Eleveur

class ExportONSSAController:
    @staticmethod
    def exporter_animaux(fichier_sortie, date_debut=None, date_fin=None):
        """Export au format attendu par l'ONSSA (Maroc)."""
        db = SessionLocal()
        try:
            query = db.query(Naissance)
            if date_debut:
                query = query.filter(Naissance.date_naissance >= date_debut)
            if date_fin:
                query = query.filter(Naissance.date_naissance <= date_fin)
            naissances = query.all()

            lignes = []
            # En-têtes à adapter selon les spécifications ONSSA
            en_tetes = [
                "CodeElevage", "NomElevage", "Commune",
                "NumeroBoucle", "Sexe", "DateNaissance", "Race",
                "PoidsNaissance", "MereBoucle", "PereBoucle",
                "DateVente", "PrixVente", "LieuVente",
                "DateDeces", "CauseDeces"
            ]
            lignes.append(en_tetes)

            for n in naissances:
                eleveur = db.query(Eleveur).filter(Eleveur.code_elevage == n.code_elevage).first()
                nom_elevage = f"{eleveur.nom} {eleveur.prenom}" if eleveur else ""

                vente = db.query(Vente).filter(
                    Vente.code_elevage == n.code_elevage,
                    Vente.numero_boucle == n.numero_boucle
                ).first()
                date_vente = vente.date_vente if vente else ""
                prix_vente = vente.prix_vente if vente else ""
                lieu_vente = vente.lieu_vente if vente else ""

                mortalite = db.query(Mortalite).filter(
                    Mortalite.code_elevage == n.code_elevage,
                    Mortalite.numero_boucle == n.numero_boucle
                ).first()
                date_deces = mortalite.date_deces if mortalite else ""
                cause_deces = mortalite.cause_deces if mortalite else ""

                ligne = [
                    n.code_elevage,
                    nom_elevage,
                    eleveur.commune if eleveur else "",
                    n.numero_boucle,
                    n.sexe,
                    n.date_naissance,
                    n.race,
                    n.poids_naissance if n.poids_naissance else "",
                    n.mere_boucle or "",
                    n.pere_boucle or "",
                    date_vente,
                    prix_vente,
                    lieu_vente,
                    date_deces,
                    cause_deces
                ]
                lignes.append(ligne)

            with open(fichier_sortie, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(lignes)

            return len(lignes)-1, None
        except Exception as e:
            return 0, str(e)
        finally:
            db.close()