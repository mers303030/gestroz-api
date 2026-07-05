import sqlite3
conn = sqlite3.connect('data/zaer.db')
cur = conn.cursor()

# Ajout des index pour accélérer les recherches
cur.execute('CREATE INDEX IF NOT EXISTS idx_eleveurs_cnie ON eleveurs (cnie)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_eleveurs_telephone ON eleveurs (telephone)')
cur.execute('CREATE INDEX IF NOT EXISTS idx_eleveurs_code_elevage ON eleveurs (code_elevage)')

conn.commit()
conn.close()
print("✅ Index ajoutés avec succès.")