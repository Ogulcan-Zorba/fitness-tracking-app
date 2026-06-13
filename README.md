# fitness-tracking-app
Python ve Flask tabanlı, SQLite entegreli akıllı fitness takip sistemi.
readme_content = """# 🏋️‍♂️ Gücünü Yaz - Akıllı Fitness ve Antrenman Takip Sistemi

**Gücünü Yaz**, bireysel sporcuların antrenman programlarını planlamaları, günlük set/tekrar/ağırlık verilerini kayıt altına almaları, gelişim süreçlerini analitik grafiklerle takip etmeleri ve hareketlerin doğru tekniklerini yerel video rehberiyle öğrenmeleri için geliştirilmiş **Full-Stack (Dinamik) bir Web Uygulamasıdır**.

Bu proje, bir **Yönetim Bilişim Sistemleri (YBS)** perspektifiyle ele alınmış; ilişkisel veritabanı mimarisi (RDBMS), arka plan iş motoru (Python/Flask), dinamik kullanıcı arayüzü kontrolü (JavaScript) ve canlı sunucu dağıtımı (Deployment) süreçlerinin tam entegrasyonunu sergileyen profesyonel bir portfolyo çalışmasıdır.

🌐 **Canlı Demo Adresi:** [gucunuyaz.pythonanywhere.com](https://gucunuyaz.pythonanywhere.com)

---

## 🚀 Öne Çıkan Özellikler

### 1. Akıllı Antrenman Kayıt Motoru (Dinamik Veri Girişi)
* Kullanıcıların seçtikleri hareketler için dinamik olarak set sayısı, tekrar sayısı ve ağırlık (kg) bazında kayıt girmesini sağlar.
* Her set verisi, ilişkisel veritabanında tarih ve zaman damgasıyla (Timestamp) atomik olarak saklanır.
* Gelişmiş `LEFT JOIN` sorgu mimarisi sayesinde, geçmiş antrenmanlar listelenirken sistem silinen veya değiştirilen hareket verilerinde dahi çökme yaşamadan zırhlı hata koruması sunar.

### 2. Rol Tabanlı Erişim Kontrolü (RBAC) & Güvenlik
* **Session (Oturum) Yönetimi:** Kullanıcı verileri ve oturum durumları Flask Session mekanizmasıyla güvenli bir şekilde sunucu tarafında doğrulanır.
* **Gizli Yönetici (Admin) Paneli:** Sadece belirli yetkiye (e-posta bazlı kimlik doğrulamasına) sahip olan "Admin" kullanıcının erişebildiği, sisteme yeni hareket ekleme, mevcut hareketleri düzenleme veya silme (CRUD) işlemlerini yürüten izole bir panel.
* **Güvenli Şifre Sıfırlama:** E-posta eşleşmesiyle çalışan, kullanıcıların şifrelerini unuttuklarında güvenle yenileyebilecekleri arka plan kontrol mekanizması.

### 3. JavaScript Destekli Akıllı Hareket Rehberi
* Sporcuların antrenman formunu bozmadan egzersiz yapabilmeleri için geliştirilmiş pop-up (Modal) tabanlı video oynatıcı.
* **Optimize Veri Akışı:** Veritabanında sadece dosya adı (örneğin: `deadlift`) saklanır. Sayfanın en altındaki asenkron JavaScript motoru, butona tıklandığı an dosya adını yakalar, otomatik olarak `/static/videos/` yolu ve `.mp4` uzantısıyla birleştirerek istemci tarafında (Client-side) dinamik olarak yükler (`.load()`). Bu sayede veritabanı şişmesi ve ağ trafiği yükü minimize edilir.

### 4. Analitik Profil ve Gelişim Takip Grafiği
* Kullanıcıların boy, kilo, yaş ve cinsiyet verilerini saklayan dinamik profil yönetim altyapısı.
* **Veri Serileştirme (JSON):** SQLite veritabanındaki tarihsel kilo geçmişi verileri, Python tarafında işlenerek `json.dumps()` ile JavaScript'in doğrudan okuyabileceği bir matrise dönüştürülür. Ön yüzde bu veriler analitik çizgi grafiklerine aktarılarak kullanıcının kilo değişim trendi görselleştirilir.

---

## 🛠️ Kullanılan Teknolojiler

* **Back-End (Arka Plan):** Python 3.8, Flask Framework
* **Veritabanı (RDBMS):** SQLite3 (İlişkisel Veritabanı Modeli)
* **Front-End (Ön Yüz):** HTML5, CSS3 (Karanlık/Siyah-Kırmızı Premium Spor Teması), JavaScript (ES6+)
* **Dağıtım / Sunucu (Deployment):** Linux / PythonAnywhere Web Server, WSGI Gateway
* **Sürüm Kontrolü:** Git / GitHub

---

## 📊 Veritabanı Mimarisi (Entity-Relationship)

Sistem mimarisinde veri bütünlüğünü (Data Integrity) sağlamak ve `Many-to-Many` (Çoka Çok) ilişkileri yönetmek adına optimize edilmiş 5 adet tablo bulunmaktadır:

1. **`uyeler`:** Kullanıcıların kimlik doğrulama verilerini saklar (`id`, `eposta`, `sifre`).
2. **`profiller`:** Sporcuların fiziksel metriklerini barındırır (`kullanici_id`, `boy`, `kilo`, `cinsiyet`, `yas`). `kullanici_id` alanı primary key olup `uyeler(id)` alanına bağlıdır.
3. **`hareketler`:** Admin tarafından yönetilen egzersiz kütüphanesidir (`id`, `hareket_adi`, `bolge`, `video_link`).
4. **`antrenmanlar` / `antrenman_kayitlari`:** Kullanıcıların yaptıkları setleri tutar (`id`, `kullanici_id`, `hareket_id`, `set_sayisi`, `tekrar_sayisi`, `agirlik`, `tarih`). `FOREIGN KEY` bağlantılarıyla üyeler ve hareketler tablolarına sıkı sıkıya bağlıdır.
5. **`kilo_gecmisi`:** Grafik çizimi için tarihsel gelişim verilerini loglar (`id`, `kullanici_id`, `kilo`, `tarih`).

---

## 💻 Yerel Kurulum Klavuzu (Local Setup)

Projeyi kendi bilgisayarınızda çalıştırmak isterseniz aşağıdaki adımları izleyebilirsiniz:

1. Bu depoyu bilgisayarınıza klonlayın veya ZIP olarak indirin:
   Kod çıkışı
README.md successfully created!

```bash
   git clone [https://github.com/KULLANICI_ADIN/kardiyo-projesi.git](https://github.com/KULLANICI_ADIN/kardiyo-projesi.git)
   cd kardiyo-projesi
2. Gerekli kütüphaneleri yükleyin:

Bash
pip install flask

3.Uygulamayı başlatın:

Bash
python app.py

4.Tarayıcınızdan şu adrese gidin:

Plaintext
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

