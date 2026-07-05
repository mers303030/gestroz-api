import os

files = [f for f in os.listdir('database/models') if f.endswith('.py') and f not in ['__init__.py','main_window.py']]
imports = []
for f in files:
    mod = f[:-3]
    # Transformer par exemple "traitement_curatif" -> "TraitementCuratif"
    cls = ''.join(part.capitalize() for part in mod.split('_'))
    imports.append(f"from .{mod} import {cls}")

with open('database/models/__init__.py', 'w') as out:
    out.write('\n'.join(imports))

print(f"Nouveau __init__.py généré avec {len(imports)} imports.")