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

## 3. Kurasi Topik & Prioritas 10 Portal Berita Indonesia

Sistem diprioritaskan penuh pada **10 portal berita nasional terpercaya dari Indonesia** (tanpa media asing) dengan sistem failover antar-kategori:

| No | Portal Berita | Domain | Kategori Utama & Fokus |
|---|---|---|---|
| 1 | **Antara News** | `antaranews.com` | Tech & Inovasi, Keamanan Siber, Isu Lingkungan (Kantor Berita Nasional) |
| 2 | **CNN Indonesia** | `cnnindonesia.com` | Cyber Security & Teknologi |
| 3 | **CNBC Indonesia** | `cnbcindonesia.com` | AI, Komputasi Cloud, & Data Center |
| 4 | **Detikcom (DetikINET)**| `inet.detik.com` | Tren Gadget, Cyber Security, & AI |
| 5 | **Mongabay Indonesia** | `mongabay.co.id` | Renewable Energy, Krisis Air, & Lingkungan Hidup |
| 6 | **Sindonews** | `sindonews.com` | Sains, Hardware, & Perkembangan Teknologi |
| 7 | **Katadata** | `katadata.co.id` | Ekonomi Hijau, Startup, & AI Digital |
| 8 | **Republika (Inovasi)** | `republika.co.id` | Transformasi Digital & Inovasi Sistem |
| 9 | **Jagat Review** | `jagatreview.com` | Review Hardware, Komponen PC, & Gadget |
| 10 | **Gizmologi** | `gizmologi.id` | Tren Perangkat Konsumen & Gadget Mobile |

---

## 4. Gaya Bahasa & Formatting (Stop-Slop Ringkas & Tuntas)

Formatting output disusun mengikuti prinsip **anti-slop padat, humanis, dan tuntas**:
1. **Ringkas & Bebas Paragraf Berlebih:** Menghilangkan komentar boilerplate statis buatan bot yang dipaksakan di tiap topik. Setiap berita langsung menyajikan Judul Tebal, 1 paragraf ringkasan tuntas (1-2 kalimat), dan link sumber.
2. **Anti-Gantung (Penyelesaian Kalimat Terpotong):** Jika ringkasan bawaan RSS feed terpotong elipsis (`...`) di tengah jalan (seperti fenomena potongan kata "True Wireless Stereo ..."), sistem otomatis mengambil paragraf pertama dari halaman web asli agar kalimatnya selesai utuh hingga tanda titik (`.`).
3. **Pembersihan Prefix Pers:** Menghapus tag kota dan media di awal teks secara presisi (misalnya `Jakarta (ANTARA) -` atau `Jakarta, CNN Indonesia --`) tanpa merusak akronim penting seperti `(TWS)`.
4. **Pembatas Bersih:** Menggunakan garis pembatas tipis (`─────────────────────`) dan format link langsung.

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
