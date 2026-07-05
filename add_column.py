import sqlite3
conn = sqlite3.connect('data/zaer.db')
cur = conn.cursor()
cur.execute('ALTER TABLE aliments ADD COLUMN code_elevage TEXT DEFAULT "0000"')
conn.commit()
conn.close()
print("✅ Colonne ajoutée.")
