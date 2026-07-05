import sqlite3
conn = sqlite3.connect('data/zaer.db')
cur = conn.cursor()
cur.execute('UPDATE aliments SET code_elevage = "OLM001" WHERE code_elevage = "0000"')
conn.commit()
conn.close()
print("✅ Aliments associés à OLM001.")
