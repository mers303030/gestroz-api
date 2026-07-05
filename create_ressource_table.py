# create_ressource_table.py
from database.db_session import engine
from database.models import Ressource

try:
    Ressource.__table__.create(engine, checkfirst=True)
    print("✅ Table 'ressources' créée avec succès.")
except Exception as e:
    print(f"❌ Erreur : {e}")