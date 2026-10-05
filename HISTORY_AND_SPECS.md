# Daily Tech News to WhatsApp Scraper — Documentation & History

> Dokumentasi arsitektur, histori konfigurasi, topik kurasi, dan alur pengiriman WhatsApp otomatis via GitHub Actions & Fonnte.

- **Repository GitHub:** [https://github.com/msigitpeb-arch/wa-news-scraper](https://github.com/msigitpeb-arch/wa-news-scraper)
- **Author:** msigitpeb-arch
- **Status:** Aktif (24/7 Serverless via GitHub Actions)
- **Terakhir Diperbarui:** 05 Oktober 2026

---

## 1. Arsitektur & Cara Kerja Sistem

```
┌────────────────────────────────┐
│   GitHub Actions (Cloud Cron)  │
│   • 08:00 UTC = 15:00 WIB      │
│   • 14:00 UTC = 21:00 WIB      │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│   daily_scraper.py             │
│   • Scraping RSS Feed Kredibel │
│   • Pemilihan Berita & Failover│
│   • Remake Gaya Chat Santai    │
│   • Proteksi Anti-Banned       │
└───────────────┬────────────────┘
                │
                ▼ (HTTP POST)
┌────────────────────────────────┐
│   Fonnte WhatsApp API Gateway  │
│   • Device: Terhubung via QR   │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│   Penerima WhatsApp            │
│   (Nomor Pribadi / Multi-Target│
└────────────────────────────────┘
```

---

## 2. Jadwal & Konfigurasi Salam (WIB / GMT+7)

| Jadwal Eksekusi | Jam UTC (Cron) | Sapaan Otomatis | Tujuan / Fungsi |
|---|---|---|---|
| **15:00 WIB (3 Sore)** | `0 8 * * *` | *"Sore team, jelang akhir jam kerja ada beberapa kabar penting dari industri tech & green energy nih✨"* | Update sore santai untuk konsumsi harian. |
| **21:00 WIB (9 Malam)** | `0 14 * * *` | *"Pagi team, pagi ini ada update menarik seputar tech & sustainability nih☕"* | Draf kurasi malam yang siap di-forward ke grup/rekan di pagi hari tanpa perlu edit salam lagi. |

---

## 3. Topik & Sumber Berita Kredibel

Script menggunakan filter kata kunci dan **mekanisme failover** (jika media Indonesia belum ada artikel baru, otomatis beralih ke media global terpercaya):

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

## 4. Proteksi Anti-Banned Fonnte & WhatsApp
Untuk mencegah nomor terblokir saat pengiriman otomatis:
1. **Typing Simulation (`typing: true`):** Fonnte memicu status *"Sedang mengetik..."* di WhatsApp selama beberapa detik sebelum pesan terkirim.
2. **Jeda Manusiawi Acak (Random Sleep):** Jeda waktu antara 3 hingga 7 detik sebelum mengeksekusi request HTTP ke gateway.
3. **Frekuensi Rendah & Aman:** Hanya mengirim 2 kali per hari ke nomor sendiri.
4. **Konten Dinamis:** Pesan selalu unik mengikuti pembaruan berita harian terbaru.

---

## 5. Fitur Multi-Target & Forward Pesan

Fonnte mendukung pengiriman ke banyak nomor sekaligus (multi-target) menggunakan pemisah koma:
* Parameter `target` dapat diisi: `081511385636,081234567890,089876543210`
* Format group ID: `120363024888888888@g.us`
* Hal ini meniadakan perlunya forward manual atau webhook forwarder terpisah.
