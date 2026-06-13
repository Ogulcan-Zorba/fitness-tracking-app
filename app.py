import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_gizli_anahtar_kelime" 

# --- KULLANICI GİRİŞ, KAYIT VE ÇIKIŞ MOTORU ---

@app.route("/register", methods=["POST"])
def register():
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    try:
        # DİKKAT: Artık 'uyeler' tablosuna 'eposta' kaydediyoruz
        cursor.execute("INSERT INTO uyeler (eposta, sifre) VALUES (?, ?)", (eposta, sifre))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
        
    conn.close()
    return redirect(url_for("ana_sayfa"))


@app.route("/login", methods=["POST"])
def login():
    eposta = request.form.get("eposta")
    sifre = request.form.get("sifre")
    
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM uyeler WHERE eposta = ? AND sifre = ?", (eposta, sifre))
    kullanici = cursor.fetchone()
    conn.close()
    
    if kullanici:
        # Kullanıcıyı içeri al
        session["kullanici_id"] = kullanici[0]
        
        # 👑 E-POSTA KONTROLÜ İLE KESİN ADMİNLİK
        # Aşağıdaki e-posta adresini, sitede üye olurken kullandığın e-posta ile değiştir!
        if eposta == "ogulcanzorba14@gmail.com":
            session["kullanici_rol"] = "admin"
        else:
            session["kullanici_rol"] = "kullanici"
            
    return redirect(url_for("ana_sayfa"))
def veritabani_kurulumu():
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eposta TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            rol TEXT DEFAULT 'uye'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hareketler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hareket_adi TEXT NOT NULL,
            bolge TEXT NOT NULL,
            video_link TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS antrenmanlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_id INTEGER,
            hareket_id INTEGER,
            set_sayisi INTEGER,
            tekrar_sayisi INTEGER,
            agirlik REAL,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(kullanici_id) REFERENCES kullanicilar(id),
            FOREIGN KEY(hareket_id) REFERENCES hareketler(id)
        )
    """)
    conn.commit()
    conn.close()

veritabani_kurulumu()

# ANA SAYFA: Giriş durumuna göre farklı ekran gösterecek
# ANA SAYFA: Giriş durumuna göre farklı ekran gösterecek
# --- AKILLI ANA SAYFA YÖNLENDİRİCİSİ ---
@app.route("/")
def ana_sayfa():
    # 1. DURUM: Kullanıcı zaten giriş yapmışsa (Session'da ID'si varsa)
    if "kullanici_id" in session:
        conn = sqlite3.connect("fitness_app.db")
        cursor = conn.cursor()
        
        # Panel sayfasında hareketlerin listelenebilmesi için veritabanından çekiyoruz
        cursor.execute("SELECT id, hareket_adi, bolge FROM hareketler")
        hareketler = cursor.fetchall()
        conn.close()
        
        # Sadece sağ üstte ÇIKIŞ butonunun olduğu "panel.html" sayfasını göster
        return render_template("panel.html", hareketler=hareketler)
    
    # 2. DURUM: Kullanıcı giriş yapmamışsa
    # Sadece GİRİŞ/ÜYE OL butonlarının olduğu o havalı "index.html" sayfasını göster
    return render_template("index.html")

# YENİ EKLENEN KISIM: Giriş Yapma Sayfası


# YENİ EKLENEN KISIM: Çıkış Yapma Fonksiyonu
@app.route("/cikis")
def cikis():
    session.clear() # Hafızadaki kullanıcı oturumunu temizler
    print("BİLGİ - Güvenli çıkış yapıldı.")
    return redirect(url_for("ana_sayfa"))

# YENİ EKLENEN KISIM: Gizli Admin Paneli
# YENİ EKLENEN KISIM: Gizli Admin Paneli
@app.route("/admin", methods=["GET", "POST"])
def admin_paneli():
    if session.get("kullanici_rol") != "admin":
        return "<h1>Erişim Reddedildi!</h1><p>Bu sayfayı görüntüleme yetkiniz yok.</p>"

    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()

    if request.method == "POST":
        hareket_adi = request.form.get("hareket_adi")
        bolge = request.form.get("bolge")
        video_link = request.form.get("video_link")

        cursor.execute("INSERT INTO hareketler (hareket_adi, bolge, video_link) VALUES (?, ?, ?)", 
                       (hareket_adi, bolge, video_link))
        conn.commit()
        print(f"BİLGİ - Yeni hareket başarıyla eklendi: {hareket_adi}")
        
        # HATAYI ÇÖZEN SATIR: Kayıt işleminden sonra sayfayı yenilenmiş gibi kendi üzerine yönlendiriyoruz
        return redirect(url_for("admin_paneli"))

    cursor.execute("SELECT * FROM hareketler")
    tum_hareketler = cursor.fetchall()
    conn.close()

    return render_template("admin.html", hareketler=tum_hareketler)

# YENİ EKLENEN KISIM: Kullanıcılar için Hareket Rehberi Sayfası
# HAREKET REHBERİ SAYFASI
@app.route("/rehber")
def hareket_rehberi():
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # DİKKAT: Sütun adı senin kodundaki gibi 'video_link' olarak düzeltildi!
    cursor.execute("SELECT id, hareket_adi, bolge, video_link FROM hareketler ORDER BY bolge, hareket_adi")
    hareketler = cursor.fetchall()
    conn.close()
    
    return render_template("rehber.html", hareketler=hareketler)
# YENİ EKLENEN KISIM: Hareket Silme Fonksiyonu
@app.route("/admin/sil/<int:id>")
def hareket_sil(id):
    # Sadece adminlerin silme yetkisi var
    if session.get("kullanici_rol") != "admin":
        return redirect(url_for("ana_sayfa"))
        
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # Gelen ID numarasına göre o hareketi veritabanından siliyoruz
    cursor.execute("DELETE FROM hareketler WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    print(f"BİLGİ - {id} numaralı hareket sistemden silindi.")
    # Sildikten sonra sayfayı yenileyip admin paneline geri dönüyoruz
    return redirect(url_for("admin_paneli"))

# ADMİN: HAREKET DÜZENLEME SAYFASI
@app.route("/admin/duzenle/<int:id>", methods=["GET", "POST"])
def hareket_duzenle(id):
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()

    # Eğer form doldurulup 'Kaydet'e basıldıysa (POST)
    if request.method == "POST":
        yeni_ad = request.form.get("hareket_adi")
        yeni_bolge = request.form.get("bolge")
        yeni_video = request.form.get("video_link")

        # Veritabanındaki eski veriyi yenisiyle ez (UPDATE)
        cursor.execute("""
            UPDATE hareketler 
            SET hareket_adi = ?, bolge = ?, video_link = ? 
            WHERE id = ?
        """, (yeni_ad, yeni_bolge, yeni_video, id))
        conn.commit()
        conn.close()
        return redirect("/admin")

    # Eğer butona yeni tıklandıysa (GET), eski verileri kutulara doldurmak için çek
    cursor.execute("SELECT * FROM hareketler WHERE id = ?", (id,))
    hareket = cursor.fetchone()
    conn.close()

    return render_template("admin_duzenle.html", hareket=hareket)

# ... (Üstteki diğer kodlar, rotalar vs.)

# ANTRENMAN KAYDETME VE TARİH İŞLEME ROTASI
# ANTRENMAN KAYDETME ROTASI (AJAN/DEBUG MODU)
# ANTRENMAN KAYDETME ROTASI (AJAN/DEBUG MODU)
@app.route("/antrenman_kaydet", methods=["POST"])
def antrenman_kaydet():
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    try:
        # 1. Aşama: Formdan gelenleri terminale bas
        print("\n--- YENİ ANTRENMAN KAYDI BAŞLADI ---")
        print("Gelen Ham Veriler:", request.form)
        
        kullanici_id = session["kullanici_id"]
        hareket_id = int(request.form.get("hareket_id"))
        toplam_set = int(request.form.get("toplam_set"))
        
        # 2. Aşama: Tarih boş geliyorsa bugünün tarihini otomatik at
        from datetime import datetime
        antrenman_tarihi = request.form.get("antrenman_tarihi") 
        if not antrenman_tarihi:
            antrenman_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect("fitness_app.db")
        cursor = conn.cursor()
        
        # 3. Aşama: Setleri döngüyle veri tabanına yaz
        for i in range(1, toplam_set + 1):
            tekrar = int(request.form.get(f"tekrar_{i}"))
            agirlik = float(request.form.get(f"agirlik_{i}"))
            
            print(f"Set İşleniyor -> Set: {i}, Tekrar: {tekrar}, Ağırlık: {agirlik}")
            
            cursor.execute("""
                INSERT INTO antrenmanlar (kullanici_id, hareket_id, set_sayisi, tekrar_sayisi, agirlik, tarih)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (kullanici_id, hareket_id, i, tekrar, agirlik, antrenman_tarihi))
        
        conn.commit()
        conn.close()
        print("BAŞARILI: Antrenman veri tabanına kusursuz yazıldı!")
        print("------------------------------------\n")
        
    except Exception as e:
        # EĞER ÇÖKERSE NEDEN ÇÖKTÜĞÜNÜ KIRMIZI ALARM OLARAK YAZ
        print(f"!!! SİSTEM HATASI: Kayıt sırasında bir sorun oluştu: {str(e)}")
        print("------------------------------------\n")
        
    return redirect(url_for("ana_sayfa"))

# GEÇMİŞ ANTRENMANLAR SAYFASI (GÜNCELLENDİ)
# GEÇMİŞ ANTRENMANLAR SAYFASI
# KULLANICI PROFİLİ VE İSTATİSTİK SAYFASI
# KULLANICI PROFİLİ VE İSTATİSTİK SAYFASI (CİNSİYET EKLENDİ)
# KULLANICI PROFİLİ VE İSTATİSTİK SAYFASI (GRAFİK ALTYAPISI EKLENDİ)
# KULLANICI PROFİLİ VE İSTATİSTİK SAYFASI (CİNSİYET EKLENDİ)
from datetime import datetime
import json

# KULLANICI PROFİLİ - ARKA PLAN MOTORU (KESİN ÇÖZÜM)
from datetime import datetime
import json

# KULLANICI PROFİLİ - ARKA PLAN MOTORU (YAŞ SÜTUNU EKLENDİ)
@app.route("/profil", methods=["GET", "POST"])
def profil():
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    kullanici_id = session["kullanici_id"]
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # 1. Tabloların oluşturulması
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiller (
        kullanici_id INTEGER PRIMARY KEY,
        boy INTEGER,
        kilo REAL,
        cinsiyet TEXT,
        yas INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kilo_gecmisi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER,
        kilo REAL,
        tarih TEXT
    )
    """)
    
    # GÜVENLİK: Mevcut tabloya cinsiyet veya yas sütunları sonradan eklendiyse çökmeyi önle
    cursor.execute("PRAGMA table_info(profiller)")
    sutunlar = [kolon[1] for kolon in cursor.fetchall()]
    if "cinsiyet" not in sutunlar:
        cursor.execute("ALTER TABLE profiller ADD COLUMN cinsiyet TEXT")
    if "yas" not in sutunlar:
        cursor.execute("ALTER TABLE profiller ADD COLUMN yas INTEGER")
    conn.commit()
    
    # 2. Formdan veri geldiyse kaydet/güncelle
    if request.method == "POST":
        boy = request.form.get("boy")
        kilo = request.form.get("kilo")
        cinsiyet = request.form.get("cinsiyet")
        yas = request.form.get("yas") # Yeni eklenen Yaş verisini al
        bugun = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("SELECT * FROM profiller WHERE kullanici_id = ?", (kullanici_id,))
        mevcut_profil = cursor.fetchone()
        
        if mevcut_profil:
            cursor.execute("UPDATE profiller SET boy = ?, kilo = ?, cinsiyet = ?, yas = ? WHERE kullanici_id = ?", (boy, kilo, cinsiyet, yas, kullanici_id))
        else:
            cursor.execute("INSERT INTO profiller (kullanici_id, boy, kilo, cinsiyet, yas) VALUES (?, ?, ?, ?, ?)", (kullanici_id, boy, kilo, cinsiyet, yas))
            
        cursor.execute("DELETE FROM kilo_gecmisi WHERE kullanici_id = ? AND tarih = ?", (kullanici_id, bugun))
        cursor.execute("INSERT INTO kilo_gecmisi (kullanici_id, kilo, tarih) VALUES (?, ?, ?)", (kullanici_id, kilo, bugun))
        
        conn.commit()
        
    # 3. Güncel verileri çek ve ekrana bas (Eğer yas boşsa varsayılan 20 yap)
    cursor.execute("SELECT boy, kilo, cinsiyet, yas FROM profiller WHERE kullanici_id = ?", (kullanici_id,))
    profil_bilgisi = cursor.fetchone()
    
    boy = profil_bilgisi[0] if profil_bilgisi else 176
    kilo = profil_bilgisi[1] if profil_bilgisi else 77.0
    cinsiyet = profil_bilgisi[2] if profil_bilgisi and profil_bilgisi[2] else "Erkek"
    # Eğer veritabanında yas sütunu varsa ve doluysa onu al, yoksa 20 yap
    yas = profil_bilgisi[3] if profil_bilgisi and len(profil_bilgisi) > 3 and profil_bilgisi[3] else 20

    # 4. GRAFİK İÇİN GEÇMİŞ VERİLERİ HAZIRLA
    cursor.execute("SELECT tarih, kilo FROM kilo_gecmisi WHERE kullanici_id = ? ORDER BY tarih ASC", (kullanici_id,))
    gecmis = cursor.fetchall()
    conn.close()
    
    tarihler = json.dumps([veri[0] for veri in gecmis])
    kilolar = json.dumps([veri[1] for veri in gecmis])
    
    # 'yas' verisini HTML'e gönderiyoruz
    return render_template("profil.html", boy=boy, kilo=kilo, cinsiyet=cinsiyet, yas=yas, tarihler=tarihler, kilolar=kilolar)
        
    # 3. Güncel verileri ekrana basmak için çek
    cursor.execute("SELECT boy, kilo, cinsiyet FROM profiller WHERE kullanici_id = ?", (kullanici_id,))
    profil_bilgisi = cursor.fetchone()
    
    boy = profil_bilgisi[0] if profil_bilgisi else 176
    kilo = profil_bilgisi[1] if profil_bilgisi else 77.0
    cinsiyet = profil_bilgisi[2] if profil_bilgisi and profil_bilgisi[2] else "Erkek"

    # 4. GRAFİK İÇİN VERİLERİ ÇEK VE HAZIRLA
    cursor.execute("SELECT tarih, kilo FROM kilo_gecmisi WHERE kullanici_id = ? ORDER BY tarih ASC", (kullanici_id,))
    gecmis = cursor.fetchall()
    conn.close()
    
    # Listeleri JavaScript'in okuyabileceği JSON formatına çeviriyoruz
    tarihler = json.dumps([veri[0] for veri in gecmis])
    kilolar = json.dumps([veri[1] for veri in gecmis])
    
    return render_template("profil.html", boy=boy, kilo=kilo, cinsiyet=cinsiyet, tarihler=tarihler, kilolar=kilolar)
# YENİ EKLENEN: KULLANICI İÇİN SET SİLME
# YENİ EKLENEN: KULLANICI İÇİN SET DÜZENLEME MOTORU
    # Sayfa ilk defa açılıyorsa eski verileri çekip forma gönder
    cursor.execute("""
        SELECT a.id, a.tarih, h.hareket_adi, a.set_no, a.tekrar, a.agirlik 
        FROM antrenman_kayitlari a
        JOIN hareketler h ON a.hareket_id = h.id
        WHERE a.id = ? AND a.kullanici_id = ?
    """, (kayit_id, kullanici_id))
    
    kayit = cursor.fetchone()
    conn.close()
    
    # Eğer kayıt bulunamazsa veya başkasının kaydına girmeye çalışırsa geçmişe yolla
    if not kayit:
        return redirect(url_for("gecmis_antrenmanlar"))
        
    return render_template("gecmis_duzenle.html", kayit=kayit)
# --- KUSURSUZ VERİTABANI OLUŞTURMA VE GÜNCELLEME MOTORU ---
# --- KUSURSUZ VERİTABANI OLUŞTURMA VE GÜNCELLEME MOTORU (TAM KAPSAMLI) ---
# --- KUSURSUZ VERİTABANI OLUŞTURMA VE GÜNCELLEME MOTORU ---
def veritabani_kontrol():
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # 1. YEPYENİ ÜYELER TABLOSU (E-posta ile çalışacak sistem)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uyeler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eposta TEXT UNIQUE,
        sifre TEXT
    )
    """)

    # 2. HAREKETLER TABLOSU 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hareketler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hareket_adi TEXT,
        bolge TEXT
    )
    """)
    
    # 3. ANTRENMAN KAYITLARI TABLOSU (Geçmiş verilerin burada güvende)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS antrenman_kayitlari (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_id INTEGER,
        hareket_id INTEGER,
        set_no INTEGER,
        tekrar INTEGER,
        agirlik REAL,
        tarih DATE DEFAULT CURRENT_DATE
    )
    """)
    
    cursor.execute("PRAGMA table_info(antrenman_kayitlari)")
    sutunlar = [kolon[1] for kolon in cursor.fetchall()]
    if "tarih" not in sutunlar:
        cursor.execute("ALTER TABLE antrenman_kayitlari ADD COLUMN tarih DATE DEFAULT CURRENT_DATE")
            
    conn.commit()
    conn.close()

veritabani_kontrol()

# ... Yukarıdaki diğer kodların ...

# GEÇMİŞ ANTRENMANLAR ROTASI (Yeniden eklendi)
# GEÇMİŞ ANTRENMANLAR ROTASI (SÜTUN İSİMLERİ DÜZELTİLDİ)
# GEÇMİŞ ANTRENMANLAR ROTASI (INNER JOIN İLE KESİN ÇÖZÜM)
# GEÇMİŞ ANTRENMANLAR ROTASI (ZIRHLI LEFT JOIN VE DEBUG MODU)
@app.route("/gecmis")
def gecmis_antrenmanlar():
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    kullanici_id = session["kullanici_id"]
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # 1. INNER JOIN yerine LEFT JOIN kullanıyoruz. 
    # Böylece hareket ismi bulunamasa bile antrenman kaydı ekrandan GİZLENMEZ.
    # 2. IFNULL kullanarak eğer isim boşsa ekrana "Hareket ID: 3" gibi geçici bir bilgi basıyoruz.
    cursor.execute("""
        SELECT 
            a.id, 
            IFNULL(h.hareket_adi, 'Sistem Hareketi (ID: ' || a.hareket_id || ')') AS hareket_ismi, 
            a.set_sayisi, 
            a.tekrar_sayisi, 
            a.agirlik, 
            a.tarih 
        FROM antrenmanlar a
        LEFT JOIN hareketler h ON a.hareket_id = h.id
        WHERE a.kullanici_id = ? 
        ORDER BY a.tarih DESC
    """, (kullanici_id,))
    
    gecmis = cursor.fetchall()
    conn.close()
    
    # TERMINALDE ANALİZ: Kod çalışınca siyah ekrana bakacağız
    print("\n--- VERİTABANI DETAYLI ANALİZ RAPORU ---")
    print(f"Aktif Kullanıcı ID: {kullanici_id}")
    print(f"Veritabanından Çekilen Toplam Kayıt Sayısı: {len(gecmis)}")
    print(f"Gelen Ham Veri Paketleri: {gecmis}")
    print("---------------------------------------\n")
    
    return render_template("gecmis.html", antrenmanlar=gecmis)

# ANTRENMAN SİLME MOTORU
@app.route("/antrenman_sil/<int:id>", methods=["POST"])
def antrenman_sil(id):
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    kullanici_id = session["kullanici_id"]
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # Güvenlik için sadece aktif kullanıcının kendi antrenmanını silmesini sağlıyoruz
    cursor.execute("DELETE FROM antrenmanlar WHERE id = ? AND kullanici_id = ?", (id, kullanici_id))
    conn.commit()
    conn.close()
    
    print(f"BİLGİ - {id} ID'li antrenman başarıyla silindi.")
    return redirect(url_for("gecmis_antrenmanlar"))

# ANTRENMAN DÜZENLEME/GÜNCELLEME MOTORU
@app.route("/antrenman_duzenle", methods=["POST"])
def antrenman_duzenle():
    if "kullanici_id" not in session:
        return redirect(url_for("ana_sayfa"))
        
    kullanici_id = session["kullanici_id"]
    antrenman_id = request.form.get("id")
    set_sayisi = int(request.form.get("set_sayisi"))
    tekrar_sayisi = int(request.form.get("tekrar_sayisi"))
    agirlik = float(request.form.get("agirlik"))
    tarih = request.form.get("tarih")
    
    conn = sqlite3.connect("fitness_app.db")
    cursor = conn.cursor()
    
    # Veritabanında güncelleme sorgusu
    cursor.execute("""
        UPDATE antrenmanlar 
        SET set_sayisi = ?, tekrar_sayisi = ?, agirlik = ?, tarih = ?
        WHERE id = ? AND kullanici_id = ?
    """, (set_sayisi, tekrar_sayisi, agirlik, tarih, antrenman_id, kullanici_id))
    
    conn.commit()
    conn.close()
    
    print(f"BİLGİ - {antrenman_id} ID'li antrenman başarıyla güncellendi.")
    return redirect(url_for("gecmis_antrenmanlar"))

# ==========================================
# ŞİFRE SIFIRLAMA MOTORU (E-POSTA İLE)
# ==========================================

@app.route("/sifremi_unuttum", methods=["GET", "POST"])
def sifremi_unuttum():
    if request.method == "POST":
        eposta = request.form.get("eposta")
        yeni_sifre = request.form.get("yeni_sifre")
        
        conn = sqlite3.connect("fitness_app.db")
        cursor = conn.cursor()
        
        # 1. Aşama: Bu e-posta veritabanında var mı?
        cursor.execute("SELECT id FROM kullanicilar WHERE eposta = ?", (eposta,))
        kullanici = cursor.fetchone()
        
        if kullanici:
            # 2. Aşama: Varsa şifreyi güncelle
            cursor.execute("UPDATE kullanicilar SET sifre = ? WHERE eposta = ?", (yeni_sifre, eposta))
            conn.commit()
            conn.close()
            
            print(f"BİLGİ - '{eposta}' adresinin şifresi başarıyla yenilendi.")
            
            # Şifre yenilendikten sonra giriş sayfasına atıyoruz
            return redirect(url_for("ana_sayfa"))
        else:
            conn.close()
            print(f"UYARI - '{eposta}' adında bir hesap bulunamadı.")
            return render_template("sifremi_unuttum.html", hata="Bu e-posta adresiyle eşleşen bir hesap bulunamadı.")
            
    return render_template("sifremi_unuttum.html")

# SİTEYİ ÇALIŞTIRAN ANA BLOK
if __name__ == "__main__":
    app.run(debug=True)
