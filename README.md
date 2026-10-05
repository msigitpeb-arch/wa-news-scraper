# 🚀 Panduan Setup Automasi Daily News ke WhatsApp (24/7 Tanpa Menyalakan Komputer)

Proyek ini telah dikonfigurasi untuk berjalan secara otomatis di cloud menggunakan **GitHub Actions** (100% Gratis & tanpa server pribadi).

---

## 📁 Struktur Berkas

```
wa-news-scraper/
├── daily_scraper.py                   # Script penarik berita, remake artikel, & pengirim WA
├── requirements.txt                   # Dependensi Python
├── .github/
│   └── workflows/
│       └── daily_briefing.yml         # Jadwal otomatis (Cron 15:00 WIB & 21:00 WIB)
└── README.md
```

---

## 🛠️ Langkah Menghubungkan ke WhatsApp & Menjalankannya

### 1. Dapatkan Token WhatsApp Gateway (Fonnte)
1. Buka [https://fonnte.com](https://fonnte.com) dan buat akun gratis.
2. Masuk ke menu **Device**, lalu scan QR code menggunakan WhatsApp Anda.
3. Masuk ke menu **API**, lalu salin **API Token** Anda.

---

### 2. Upload Kode ke GitHub Repository Pribadi
1. Buat repository baru di GitHub (disarankan diset ke **Private**).
2. Upload seluruh folder `wa-news-scraper` ke repository tersebut:
   ```bash
   git init
   git add .
   git commit -m "feat: daily news to wa scraper"
   git branch -M main
   git remote add origin <URL_REPO_GITHUB_ANDA>
   git push -u origin main
   ```

---

### 3. Simpan Secret Token di GitHub
Agar nomor WA dan Token Anda aman dan tidak terbaca publik:
1. Buka repo Anda di GitHub $\rightarrow$ klik tab **Settings**.
2. Di bilah samping kiri, pilih **Secrets and variables** $\rightarrow$ **Actions**.
3. Klik tombol **New repository secret**, lalu tambahkan 2 rahasia:
   * **Nama:** `FONNTE_TOKEN`  
     **Nilai:** *(Paste Token dari Fonnte Anda)*
   * **Nama:** `WA_TARGET_NUMBER`  
     **Nilai:** *(Nomor WA tujuan Anda, contoh: `081234567890`)*

---

### 4. Selesai! Automasi Berjalan 24/7
* **Jadwal Otomatis**:
  * Pukul **15:00 WIB (08:00 UTC)**: Mengirim salam sore dengan update berita sesi siang/sore.
  * Pukul **21:00 WIB (14:00 UTC)**: Mengirim salam malam dengan update berita penutup hari.
* **Test Manual Kapan Saja**:
  * Anda bisa langsung menguji tanpa menunggu jam di atas: Buka tab **Actions** di GitHub repo Anda $\rightarrow$ klik **Daily Tech News to WhatsApp** $\rightarrow$ klik tombol **Run workflow**. Pesan akan langsung masuk ke WhatsApp Anda dalam hitungan detik!
