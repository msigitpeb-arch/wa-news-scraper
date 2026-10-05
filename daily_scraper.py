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

# --- KONFIGURASI SUMBER BERITA KREDIBEL (RSS FEED & PORTAL) ---
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
    """Membersihkan tag HTML dari ringkasan berita."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text[:280] + "..." if len(text) > 280 else text

def ambil_berita_terbaru():
    """Mengambil 1-2 berita terbaru dari masing-masing kategori."""
    hasil_kategori = {}

    for kategori, daftar_sumber in FEEDS.items():
        hasil_kategori[kategori] = []
        for sumber in daftar_sumber:
            try:
                feed = feedparser.parse(sumber["url"])
                if feed.entries:
                    top = feed.entries[0]
                    summary = bersihkan_html(top.get("summary", top.get("description", "")))
                    hasil_kategori[kategori].append({
                        "sumber": sumber["name"],
                        "judul": top.title.strip(),
                        "link": top.link,
                        "ringkasan": summary
                    })
                    break  # Ambil berita terbaik pertama yang berhasil
            except Exception as e:
                print(f"Gagal mengambil dari {sumber['name']}: {e}")
                continue

    return hasil_kategori

def dapatkan_salam_wib():
    """Menghitung waktu WIB (GMT+7) dan mengembalikan salam yang sesuai."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_wib = now_utc + datetime.timedelta(hours=7)
    jam = now_wib.hour

    if 4 <= jam < 11:
        salam = "Selamat Pagi"
    elif 11 <= jam < 15:
        salam = "Selamat Siang"
    elif 15 <= jam < 18:
        salam = "Selamat Sore"
    else:
        salam = "Selamat Malam"

    tanggal_str = now_wib.strftime("%d %B %Y, %H:%M WIB")
    return salam, tanggal_str

def susun_pesan(berita):
    """Menyusun pesan ringkasan (Opsi 1) dengan sumber berupa link aktual."""
    salam, waktu = dapatkan_salam_wib()

    icon_map = {
        "Cyber Security": "🔒",
        "AI / Data Center": "🤖",
        "Green Environment": "🌱",
        "Tech Industries": "⚡"
    }

    isi_kategori = []

    for kat, items in berita.items():
        icon = icon_map.get(kat, "📰")
        blok = f"{icon} *[{kat.upper()}]*\n"
        if items:
            for item in items:
                blok += (
                    f"• *{item['judul']}*\n"
                    f"  {item['ringkasan']}\n"
                    f"  🔗 *Sumber:* {item['link']}\n"
                )
        else:
            blok += "• Belum ada pembaruan signifikan saat ini.\n"
        isi_kategori.append(blok)

    konten = "\n".join(isi_kategori)

    pesan_final = (
        f"{salam}, Rekan! 🌐\n"
        f"Berikut *Daily Tech Intelligence Briefing* — {waktu}.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{konten}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 _Pembaruan otomatis berikutnya akan dikirimkan sesuai jadwal._"
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

    # Anti-ban layer 1: Random typing delay (jeda manusiawi antara 3 - 7 detik)
    jeda_acak = random.randint(3, 7)
    print(f"[Anti-Ban] Menunggu jeda natural {jeda_acak} detik sebelum pengiriman...")
    time.sleep(jeda_acak)

    # Anti-ban layer 2: Parameter proteksi Fonnte
    payload = {
        "target": target,
        "message": pesan,
        "countryCode": "62",
        "typing": "true",          # Menampilkan status 'Sedang mengetik...' di WA
        "delay": str(jeda_acak)     # Delay internal di gateway
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
    print("Memulai proses scraping berita...")
    berita_terkumpul = ambil_berita_terbaru()
    pesan_siap_kirim = susun_pesan(berita_terkumpul)
    kirim_ke_whatsapp(pesan_siap_kirim)
