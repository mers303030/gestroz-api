import os, re

eleveur_path = 'database/models/eleveur.py'
with open(eleveur_path, 'r', encoding='utf-8') as f:
    content = f.read()

models_dir = 'database/models'
relations = set()
for file in os.listdir(models_dir):
    if file.endswith('.py') and file not in ['__init__.py','main_window.py','eleveur.py']:
        with open(os.path.join(models_dir, file), 'r', encoding='utf-8') as m:
            text = m.read()
            matches = re.findall(r'back_populates\s*=\s*["\']([^"\']+)["\']', text)
            relations.update(matches)

# Ajouter chaque relation manquante dans Eleveur
for rel in relations:
    if rel not in content:
        # Trouver la classe correspondante (on suppose qu'elle est dans un fichier avec le même nom)
        # Mais pour simplifier, on crée une propriété avec relationship vers une classe du même nom capitalisé
        content = content.replace(
            'class Eleveur(Base):',
            f'class Eleveur(Base):\n    {rel} = relationship("{rel.capitalize()}", back_populates="{rel}")'
        )

# Ajouter l'import relationship si absent
if 'from sqlalchemy.orm import relationship' not in content:
    content = 'from sqlalchemy.orm import relationship\n' + content

with open(eleveur_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Toutes les relations manquantes ont été ajoutées.")
print("Relations trouvées :", relations)