import re
import os

eleveur_path = 'database/models/eleveur.py'

with open(eleveur_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ajouter la relation manquante si elle n'existe pas
if 'traitements_individuels' not in content:
    content = content.replace(
        'class Eleveur(Base):',
        'class Eleveur(Base):\n    traitements_individuels = relationship("TraitementIndividuel", back_populates="eleveur")'
    )

# Ajouter l'import relationship si absent
if 'from sqlalchemy.orm import relationship' not in content:
    content = 'from sqlalchemy.orm import relationship\n' + content

with open(eleveur_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Relation 'traitements_individuels' ajoutée à Eleveur.")