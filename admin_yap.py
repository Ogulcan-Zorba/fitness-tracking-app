import sqlite3

# Veritabanına bağlanıyoruz
conn = sqlite3.connect("fitness_app.db")
cursor = conn.cursor()

# 1 numaralı kullanıcıyı (yani sisteme ilk kayıt olan seni) admin yapıyoruz
cursor.execute("UPDATE kullanicilar SET rol = 'admin' WHERE id = 1")

conn.commit()
conn.close()

print("BİLGİ - Tebrikler, artık sistemin tek yetkili Admin'isin!")