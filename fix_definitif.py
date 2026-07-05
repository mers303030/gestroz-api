import os, re, shutil

models_dir = 'database/models'

# 1. Supprimer toutes les lignes contenant relationship/backref/back_populates
for file in os.listdir(models_dir):
    if file.endswith('.py') and file not in ['__init__.py', 'main_window.py', 'migration_famille_ressources.py']:
        path = os.path.join(models_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if 'relationship' in line or 'back_populates' in line or 'backref' in line:
                continue
            new_lines.append(line)
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

# 2. Réécrire Eleveur (propre, sans relations)
eleveur = """from sqlalchemy import Column, String
from database.db_session import Base

class Eleveur(Base):
    __tablename__ = 'eleveurs'
    code_elevage = Column(String, primary_key=True)
    nom = Column(String)
    prenom = Column(String)
    date_naissance = Column(String)
    niveau_scolaire = Column(String)
    cnie = Column(String, unique=True)
    telephone = Column(String, unique=True)
    commune = Column(String)
"""
with open(os.path.join(models_dir, 'eleveur.py'), 'w', encoding='utf-8') as f:
    f.write(eleveur)

# 3. Créer aliments_base.py (alias)
with open(os.path.join(models_dir, 'aliments_base.py'), 'w', encoding='utf-8') as f:
    f.write('from .aliment_base import AlimentBase as AlimentsBase\n')

# 4. Régénérer __init__.py
files = [f for f in os.listdir(models_dir) if f.endswith('.py') and f not in ['__init__.py', 'main_window.py', 'migration_famille_ressources.py']]
imports = []
for f in files:
    cls = ''.join(part.capitalize() for part in f[:-3].split('_'))
    # Correction pour les noms spéciaux si besoin
    if cls == 'Ficheculturale':
        cls = 'FicheCulturale'
    if cls == 'Alimentbase':
        cls = 'AlimentBase'
    imports.append(f'from .{f[:-3]} import {cls}')
with open(os.path.join(models_dir, '__init__.py'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(imports))

# 5. Nettoyer les caches
for root, dirs, files in os.walk('.'):
    for d in dirs:
        if d == '__pycache__':
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)

print("✅ TOUT EST CORRIGÉ.")
print("Lancez maintenant : python main.py")