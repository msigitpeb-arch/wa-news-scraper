# Daily Tech News to WhatsApp Scraper — Documentation & History

> Dokumentasi arsitektur, histori konfigurasi, topik kurasi, alur pengiriman WhatsApp otomatis (Personal & Group) via GitHub Actions & Fonnte.

- **Repository GitHub:** [https://github.com/msigitpeb-arch/wa-news-scraper](https://github.com/msigitpeb-arch/wa-news-scraper)
- **Author:** msigitpeb-arch
- **Status:** Aktif (24/7 Serverless via GitHub Actions & cron-job.org)
- **Terakhir Diperbarui:** 06 Oktober 2026

---

## 1. Arsitektur & Cara Kerja Sistem

```
┌──────────────────────────────────────────────┐
│  Eksternal Cron Trigger (cron-job.org)       │
│  • 15:00 WIB (08:00 UTC)                     │
│  • 21:00 WIB (14:00 UTC)                     │
└──────────────────────┬───────────────────────┘
                       │ (Trigger workflow_dispatch)
                       ▼
┌──────────────────────────────────────────────┐
│  GitHub Actions (Serverless Runner)          │
│  • Checkout repo & setup Python              │
│  • Eksekusi daily_scraper.py                 │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  daily_scraper.py                            │
│  • Scraping RSS Feed (Mongabay, CNN, CNBC,..)│
│  • Filter kata kunci & Fallback Global       │
│  • Formatting Stop-Slop (Natural & Bersih)   │
│  • Proteksi Anti-Ban (Typing + Random Sleep) │
└──────────────────────┬───────────────────────┘
                       │
                       ▼ (HTTP POST /send)
┌──────────────────────────────────────────────┐
│  Fonnte WhatsApp API Gateway                 │
│  • Device WhatsApp Terhubung                 │
└──────────────────────┬───────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐
│ Nomor Personal WA   │     │ WhatsApp Group      │
│ (081511385636)      │     │ (NEWS / ...@g.us)   │
└─────────────────────┘     └─────────────────────┘
```

---

## 2. Jadwal & Konfigurasi Salam (WIB / GMT+7)

| Jadwal Eksekusi | Jam UTC | Sapaan Otomatis | Target & Fungsi |
|---|---|---|---|
| **15:00 WIB (3 Sore)** | `08:00 UTC` | *"Sore team, jelang akhir jam kerja ada beberapa kabar penting dari industri tech & green energy nih✨"* | Update sore hari santai. |
| **21:00 WIB (9 Malam)** | `14:00 UTC` | *"Pagi team, semoga sehat selalu dan lancar aktivitasnya. Pagi ini ada update penting dari industri tech dan lingkungan:"* | Kurasi malam yang otomatis memakai salam pagi hari agar siap dibaca anggota tim di grup pagi-pagi. |

> **Catatan Trigger Jadwal:** Mengingat scheduler `cron` native GitHub Actions sering mengalami antrean/delay hingga puluhan menit, penjadwalan presisi di-trigger menggunakan **cron-job.org** yang menembak API GitHub `workflow_dispatch`.

---

## 3. Kurasi Topik & Sumber Berita Kredibel

Script menggunakan filter kata kunci dan **mekanisme failover** (jika media Indonesia belum memiliki artikel terbaru, otomatis beralih ke sumber global terpercaya):

### Topik 1 (Prioritas): Renewable Energy & Lingkungan
* **Sumber Utama:** Mongabay Indonesia (`mongabay.co.id`)
* **Cadangan:** CleanTechnica, GreenBiz

### Topik 2: Cyber Security (Keamanan Siber)
* **Sumber Utama:** CNN Indonesia Kanal Teknologi (`cnnindonesia.com/teknologi`)
* **Cadangan:** The Hacker News (`thehackernews.com`), BleepingComputer (`bleepingcomputer.com`)

### Topik 3: AI & Data Center
* **Sumber Utama:** CNBC Indonesia Kanal Tech (`cnbcindonesia.com/tech`)
* **Cadangan:** VentureBeat AI, Data Center Dynamics (DCD)

### Topik 4: Tech & Inovasi Perkembangan Teknologi
* **Sumber Utama:** Antara News Kanal Tekno (`antaranews.com/tekno`), Republika Inovasi
* **Cadangan:** The Verge, Ars Technica

---

## 4. Gaya Bahasa & Formatting (Stop-Slop Standard — 100% Full Indonesia)

Formatting output disusun mengikuti prinsip **anti-slop** dan **konsistensi satu bahasa penuh**:
1. **100% Full Bahasa Indonesia (Anti Gado-Gado):** Jika berita diambil dari sumber global berbahasa Inggris (CleanTechnica, The Hacker News, VentureBeat, DCD, The Verge), judul dan ringkasan otomatis diterjemahkan ke Bahasa Indonesia sebelum disatukan ke narasi briefing. Tidak ada lagi kalimat bahasa Inggris yang tercampur di tengah paragraf Indonesia.
2. **Polishing Istilah Tech Alami:** Mesin terjemahan dipoles agar tidak kaku ("Pusat Data" → "Data Center", "Kecerdasan Buatan" → "AI", "situs Edge" → "fasilitas Edge Data Center").
3. **Bebas Klise AI:** Tidak menggunakan frasa generik seperti *"Langkah ini sangat krusial...", "Menjadi pengingat penting...", "Menandai babak baru..."*.
4. **Konteks Nyata:** Penjelasan langsung mengarah ke inti permasalahan (dampak riil, operasional, ketahanan pangan, keamanan data, efisiensi komputasi).
5. **Pembatas & Link Bersih:** Menggunakan garis pembatas tipis (`─────────────────────`) dan format link seragam (`Selengkapnya dapat dibaca di sini:`).

---

## 5. Pengiriman Target: Nomor Pribadi & WhatsApp Group

### A. Pengiriman ke WhatsApp Group (JID `@g.us`)
Fonnte mendukung pengiriman langsung ke grup WhatsApp dengan format ID: `<group_id>@g.us`.

* **Syarat:** Nomor WhatsApp yang terhubung di Fonnte (`081511385636`) harus **sudah menjadi anggota (member)** di grup WhatsApp target.
* **Helper Script (`ambil_id_grup.py`):**
  Untuk mengambil Group ID dari WhatsApp, jalankan:
  ```powershell
  python ambil_id_grup.py
  ```
  Script akan memanggil endpoint Fonnte:
  1. `POST https://api.fonnte.com/fetch-group` (sinkronisasi data grup dari device)
  2. `POST https://api.fonnte.com/get-whatsapp-group` (mengambil daftar nama dan ID grup)
* **Hasil Uji:** Berhasil terkirim langsung ke grup **NEWS** (`120363xxxxxx@g.us`).

### B. Konfigurasi `WA_TARGET_NUMBER` di GitHub Secrets
Buka menu repository: `Settings` → `Secrets and variables` → `Actions` → `WA_TARGET_NUMBER`:
* **Hanya ke WhatsApp Group:**
  ```text
  120363xxxxxxxxx@g.us
  ```
* **Multi-Target (Personal + WhatsApp Group):**
  Pisahkan dengan koma tanpa spasi:
  ```text
  081511385636,120363xxxxxxxxx@g.us
  ```

---

## 6. Proteksi Anti-Banned Fonnte & WhatsApp
1. **Typing Simulation (`typing: true`):** Fonnte memicu status *"Sedang mengetik..."* di WhatsApp sebelum pesan terkirim.
2. **Jeda Manusiawi Acak (Random Sleep):** Jeda waktu antara 3 hingga 7 detik sebelum mengeksekusi request HTTP ke gateway.
3. **Frekuensi Aman:** Hanya mengirim 2 kali per hari pada jam-jam wajar.
4. **Konten Dinamis:** Selalu memuat berita baru yang berbeda setiap eksekusi.
