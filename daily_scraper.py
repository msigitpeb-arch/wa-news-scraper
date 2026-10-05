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

# --- KONFIGURASI SUMBER BERITA KREDIBEL ---
FEEDS = {
    "Cyber Security": [
        {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
    ],
    "AI / Data Center": [
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/rss/"},
    ],
    "Green Environment": [
        {"name": "CleanTechnica", "url": "https://cleantechnica.com/feed/"},
        {"name": "GreenBiz", "url": "https://www.greenbiz.com/rss.xml"},
    ],
    "Tech Industries": [
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    ]
}

def bersihkan_html(raw_html):
    """Membersihkan tag HTML dari deskripsi feed."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def ambil_berita_terbaru():
    """Mengambil berita terhangat per kategori."""
    hasil_kategori = {}

    for kategori, daftar_sumber in FEEDS.items():
        hasil_kategori[kategori] = None
        for sumber in daftar_sumber:
            try:
                feed = feedparser.parse(sumber["url"])
                if feed.entries:
                    top = feed.entries[0]
                    summary = bersihkan_html(top.get("summary", top.get("description", "")))
                    hasil_kategori[kategori] = {
                        "sumber": sumber["name"],
                        "judul": top.title.strip(),
                        "link": top.link,
                        "ringkasan": summary
                    }
                    break
            except Exception as e:
                print(f"Gagal mengambil dari {sumber['name']}: {e}")
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

    # Jika berjalan sekitar jam 15:00 WIB (fase sore)
    if 13 <= jam < 19:
        salam = "Sore team, jelang akhir jam kerja ada beberapa kabar penting dari industri tech & green energy nih✨"
    else:
        # Jika jam 21:00 WIB atau jam lainnya (disiapkan khusus bertema Pagi hari)
        salam = "Pagi team, pagi ini ada update menarik seputar tech & sustainability nih☕"

    return salam

def parafrase_opini_santai(kategori, item):
    """
    Menulis ulang berita dengan gaya percakapan santai, reflektif,
    dan kontekstual seperti obrolan grup WA pada referensi user.
    """
    judul = item["judul"]
    summary = item["ringkasan"]

    if kategori == "Cyber Security":
        return (
            f"🔒 *Terkait Keamanan Siber:*\n"
            f"Lagi ramai kabar *\"{judul}\"*. Isu ini jadi pengingat buat kita semua bahwa celah keamanan "
            f"dan eksploitasi data makin canggih modusnya. Penting banget buat tim IT dan operasional untuk "
            f"selalu audit berkala dan jangan sampai lengah sama sistem autentikasi.\n\n"
            f"Selengkapnya bisa dicek di sini:\n{item['link']}"
        )
    elif kategori == "AI / Data Center":
        return (
            f"🤖 *Update AI & Komputasi:*\n"
            f"Dari ranah AI dan infrastruktur, ada sorotan menarik soal *\"{judul}\"*. "
            f"Kebutuhan daya komputasi data center sekarang bener-bener gila-gilaan naiknya, makanya persaingan "
            f"penyediaan kapasitas server sama efisiensi energi jadi kunci penentu buat perlombaan AI ke depan.\n\n"
            f"Detail beritanya ada di sini:\n{item['link']}"
        )
    elif kategori == "Green Environment":
        return (
            f"🌱 *Lingkungan & Isu Hijau:*\n"
            f"Masih seputar adaptasi iklim dan transisi hijau, ada kabar soal *\"{judul}\"*. "
            f"Langkah-langkah keberlanjutan dan pengelolaan sumber daya ramah lingkungan ini memang makin krusial ya, "
            f"apalagi dengan regulasi emisi dan tantangan cuaca ekstrem saat ini.\n\n"
            f"Baca selengkapnya di sini:\n{item['link']}"
        )
    else:  # Tech Industries
        return (
            f"⚡ *Kabar Industri Teknologi:*\n"
            f"Sementara dari pergerakan industri teknologi, ada perkembangan baru mengenai *\"{judul}\"*. "
            f"Inovasi perangkat dan ekosistem digital terus bergerak cepat menyesuaikan tren pasar konsumen terbaru.\n\n"
            f"Selengkapnya dapat dibaca di sini:\n{item['link']}"
        )

def susun_pesan(berita):
    """
    Menyusun pesan bergaya humanis/storytelling seperti contoh chat grup WhatsApp:
    - Salam hangat santai
    - Pembahasan reflektif per topik mengalir dengan emoji natural
    - Link bersih di akhir tiap topik
    """
    salam = dapatkan_salam_wib()

    blok_cerita = []
    for kategori in ["Cyber Security", "AI / Data Center", "Green Environment", "Tech Industries"]:
        item = berita.get(kategori)
        if item:
            teks_topik = parafrase_opini_santai(kategori, item)
            blok_cerita.append(teks_topik)

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

    # Anti-ban delay dinamis
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
    print("Memulai proses scraping dan penyusunan narasi humanis...")
    berita_terkumpul = ambil_berita_terbaru()
    pesan_siap_kirim = susun_pesan(berita_terkumpul)
    kirim_ke_whatsapp(pesan_siap_kirim)
