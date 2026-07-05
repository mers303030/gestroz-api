with open('database/models/eleveur.py', 'r') as f:
    content = f.read()
# Remplacer l'appel incorrect
content = content.replace('Vaccinations_collectives', 'VaccinationCollective')
with open('database/models/eleveur.py', 'w') as f:
    f.write(content)
print("Corrigé.")