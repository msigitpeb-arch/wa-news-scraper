import os
import sys
import datetime
import requests
import feedparser
from bs4 import BeautifulSoup

# Pastikan output konsol mendukung Unicode (Emoji) di Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# KONFIGURASI SUMBER BERITA KREDIBEL
# Terdiri dari 5 Media Kredibel Indonesia + Media Global Khusus
# ==============================================================================
FEEDS = {
    # 1. Renewable Energy & Green Environment (Prioritas Nasional & Global)
    "Renewable Energy & Lingkungan": [
        {"name": "Mongabay Indonesia", "url": "https://www.mongabay.co.id/feed/", "lang": "id"},
        {"name": "CleanTechnica", "url": "https://cleantechnica.com/feed/", "lang": "en"},
        {"name": "GreenBiz", "url": "https://www.greenbiz.com/rss.xml", "lang": "en"},
    ],

    # 2. Cyber Security (Keamanan Siber & Insiden Data)
    "Cyber Security": [
        {"name": "CNN Indonesia (Teknologi & Keamanan)", "url": "https://www.cnnindonesia.com/teknologi/rss", "lang": "id", "filter": ["hacker", "siber", "bobol", "keamanan", "data", "serangan", "malware", "phishing", "ransomware", "security"]},
        {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews", "lang": "en"},
        {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/", "lang": "en"},
    ],

    # 3. AI & Data Center (Infrastruktur Komputasi & Kecerdasan Buatan)
    "AI & Data Center": [
        {"name": "CNBC Indonesia (Tech & AI)", "url": "https://www.cnbcindonesia.com/tech/rss", "lang": "id", "filter": ["ai", "kecerdasan", "data center", "server", "komputasi", "chip", "nvidia", "cloud"]},
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "lang": "en"},
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/rss/", "lang": "en"},
    ],

    # 4. Tech & Inovasi Perkembangan Teknologi
    "Tech & Inovasi Teknologi": [
        {"name": "Antara News (Tekno & Riset)", "url": "https://www.antaranews.com/rss/tekno.xml", "lang": "id"},
        {"name": "Republika Inovasi", "url": "https://www.republika.co.id/rss/retizen", "lang": "id"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "lang": "en"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index", "lang": "en"},
    ]
}

def bersihkan_html(raw_html):
    """Membersihkan tag HTML dari ringkasan berita."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text[:260] + "..." if len(text) > 260 else text

def ambil_berita_terbaru():
    """
    Cara Kerja Pemilihan Berita (Sistem Prioritas & Failover):
    1. Memprioritaskan topik utama (Renewable energy, Cyber security, Tech, AI, dan inovasi).
    2. Mencari di media utama (Indonesia). Jika ada filter kata kunci, dicocokkan ke entri terbaru.
    3. Jika media pertama tidak memiliki berita relevan terbaru atau gagal diakses, 
       otomatis failover ke sumber rujukan cadangan berikutnya tanpa henti.
    """
    hasil_kategori = {}

    for kategori, daftar_sumber in FEEDS.items():
        hasil_kategori[kategori] = None
        for sumber in daftar_sumber:
            try:
                feed = feedparser.parse(sumber["url"])
                if not feed.entries:
                    continue

                filter_keywords = sumber.get("filter")
                artikel_terpilih = None

                if filter_keywords:
                    # Cari entri terbaru yang judul atau ringkasannya cocok dengan kata kunci topik
                    for entry in feed.entries[:15]:
                        teks_gabungan = (entry.title + " " + entry.get("summary", "")).lower()
                        if any(kw in teks_gabungan for kw in filter_keywords):
                            artikel_terpilih = entry
                            break
                else:
                    # Ambil entri paling atas (terbaru)
                    artikel_terpilih = feed.entries[0]

                if artikel_terpilih:
                    summary = bersihkan_html(artikel_terpilih.get("summary", artikel_terpilih.get("description", "")))
                    hasil_kategori[kategori] = {
                        "sumber": sumber["name"],
                        "judul": artikel_terpilih.title.strip(),
                        "link": artikel_terpilih.link,
                        "ringkasan": summary
                    }
                    break  # Berhasil menemukan berita valid untuk kategori ini, lanjut ke kategori berikutnya
            except Exception as e:
                print(f"[Failover] Gagal/timeout pada {sumber['name']}: {e}. Berpindah ke cadangan...")
                continue

    return hasil_kategori

def dapatkan_salam_wib():
    """
    Menghasilkan sapaan santai sesuai kebutuhan user:
    - Jadwal Jam 3 Sore (15:00 WIB): Ucapan 'Selamat Sore'
    - Jadwal Jam 9 Malam (21:00 WIB): Ucapan 'Selamat Pagi' (karena bahan kurasi disiapkan untuk di-forward esok paginya)
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_wib = now_utc + datetime.timedelta(hours=7)
    jam = now_wib.hour

    if 13 <= jam < 19:
        salam = "Sore team, jelang akhir jam kerja ada beberapa kabar penting dari industri tech & green energy nih✨"
    else:
        salam = "Pagi team, pagi ini ada update menarik seputar tech & sustainability nih☕"

    return salam

def parafrase_opini_santai(kategori, item):
    """
    Menulis ulang berita dengan gaya percakapan santai, reflektif,
    dan kontekstual seperti obrolan grup WA pada referensi user.
    """
    judul = item["judul"]
    sumber = item["sumber"]
    link = item["link"]

    if kategori == "Renewable Energy & Lingkungan":
        return (
            f"🌱 *Energi Terbarukan & Lingkungan:*\n"
            f"Isu transisi hijau lagi hangat nih, ada kabar *\"{judul}\"*. "
            f"Langkah-langkah adaptasi iklim dan dorongan energi terbarukan ini memang krusial banget ya buat "
            f"keberlanjutan industri kita ke depan.\n\n"
            f"Selengkapnya dapat dibaca di sini:\n{link}"
        )
    elif kategori == "Cyber Security":
        return (
            f"🔒 *Keamanan Siber (Cyber Security):*\n"
            f"Dari lini pertahanan data, lagi ramai kabar *\"{judul}\"*. "
            f"Ini jadi pengingat penting buat kita semua bahwa celah keamanan dan pola eksploitasi data makin canggih. "
            f"Penting banget tim operasional buat terus perkuat proteksi autentikasi.\n\n"
            f"Detail beritanya bisa dicek di sini:\n{link}"
        )
    elif kategori == "AI & Data Center":
        return (
            f"🤖 *AI & Infrastruktur Komputasi:*\n"
            f"Menyoroti perkembangan AI dan data center, ada update menarik soal *\"{judul}\"*. "
            f"Kebutuhan daya komputasi server sekarang makin intensif, makanya kesiapan infrastruktur data center "
            f"sama efisiensi energi jadi kunci penentu persaingan AI.\n\n"
            f"Baca selengkapnya di sini:\n{link}"
        )
    else:  # Tech & Inovasi Teknologi
        return (
            f"⚡ *Tech & Inovasi Terkini:*\n"
            f"Sementara dari inovasi teknologi industri, ada perkembangan seputar *\"{judul}\"*. "
            f"Akselerasi inovasi perangkat dan solusi digital terus bergerak cepat mengikuti kebutuhan pasar saat ini.\n\n"
            f"Selengkapnya bisa dilihat di sini:\n{link}"
        )

def susun_pesan(berita):
    """Menyusun format chat grup santai dengan urutan topik terkurasi."""
    salam = dapatkan_salam_wib()

    blok_cerita = []
    urutan_topik = [
        "Renewable Energy & Lingkungan",
        "Cyber Security",
        "AI & Data Center",
        "Tech & Inovasi Teknologi"
    ]

    for kat in urutan_topik:
        item = berita.get(kat)
        if item:
            teks = parafrase_opini_santai(kat, item)
            blok_cerita.append(teks)

    isi_utama = "\n\n━━━━━━━━━━━━━━━━━━━━━\n\n".join(blok_cerita)

    pesan_final = (
        f"{salam}\n\n"
        f"{isi_utama}\n\n"
        f"Semoga bermanfaat dan tetap semangat kegiatannya hari ini! 🙏🔥"
    )

    return pesan_final

def kirim_ke_whatsapp(pesan):
    """Mengirim pesan via Fonnte WhatsApp API dengan perlindungan Anti-Banned."""
    import time
    import random

    token = os.getenv("FONNTE_TOKEN")
    target = os.getenv("WA_TARGET_NUMBER")

    if not token or not target:
        print("[PERINGATAN] FONNTE_TOKEN atau WA_TARGET_NUMBER belum diset di Environment Variable.")
        print("Mencetak hasil pesan ke konsol:\n")
        print(pesan)
        return False

    url = "https://api.fonnte.com/send"
    headers = {"Authorization": token}

    # Anti-ban: jeda manusiawi acak
    jeda_acak = random.randint(3, 7)
    print(f"[Anti-Ban] Menunggu jeda natural {jeda_acak} detik...")
    time.sleep(jeda_acak)

    payload = {
        "target": target,
        "message": pesan,
        "countryCode": "62",
        "typing": "true",
        "delay": str(jeda_acak)
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        res_data = response.json()
        print(f"Status Kirim WA: {res_data}")
        return res_data.get("status") == True
    except Exception as e:
        print(f"Error saat mengirim ke WhatsApp: {e}")
        return False

if __name__ == "__main__":
    print("Memulai proses scraping berita kurasi...")
    berita_terkumpul = ambil_berita_terbaru()
    pesan_siap_kirim = susun_pesan(berita_terkumpul)
    kirim_ke_whatsapp(pesan_siap_kirim)
