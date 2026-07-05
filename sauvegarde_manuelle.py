import shutil
import os
from datetime import datetime

src = 'S:/Python-Project/Zaer'
dest = f'S:/Python-Project/Zaer_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

print(f"Sauvegarde de {src} vers {dest}...")
shutil.copytree(src, dest, ignore_dangling_symlinks=True)
print("✅ Sauvegarde terminée.")