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
# ==============================================================================
FEEDS = {
    # 1. Renewable Energy & Lingkungan
    "Renewable Energy & Lingkungan": [
        {"name": "Mongabay Indonesia", "url": "https://www.mongabay.co.id/feed/"},
        {"name": "CleanTechnica", "url": "https://cleantechnica.com/feed/"},
    ],

    # 2. Cyber Security
    "Cyber Security": [
        {"name": "CNN Indonesia (Keamanan & Tekno)", "url": "https://www.cnnindonesia.com/teknologi/rss", "filter": ["bssn", "data", "kebocoran", "hacker", "siber", "keamanan", "serangan", "bobol", "malware", "ransomware", "security"]},
        {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
    ],

    # 3. AI & Data Center
    "AI & Data Center": [
        {"name": "CNBC Indonesia (Tech & AI)", "url": "https://www.cnbcindonesia.com/tech/rss", "filter": ["ai", "data center", "server", "komputasi", "chip", "nvidia", "cloud", "intel", "teknologi"]},
        {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/rss/"},
    ],

    # 4. Tech & Inovasi Perkembangan Teknologi
    "Tech & Inovasi": [
        {"name": "Antara News (Tekno)", "url": "https://www.antaranews.com/rss/tekno.xml"},
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    ]
}

def bersihkan_html(raw_html):
    """Membersihkan tag HTML dan karakter aneh dari deskripsi feed."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = text.replace("\ufffd", " ")
    return " ".join(text.split())

def ambil_berita_terbaru():
    """Mengambil berita terhangat per kategori dengan failover."""
    hasil_kategori = {}

    for kategori, daftar_sumber in FEEDS.items():
        hasil_kategori[kategori] = None
        for sumber in daftar_sumber:
            try:
                feed = feedparser.parse(sumber["url"])
                if not feed.entries:
                    continue

                filter_keywords = sumber.get("filter")
                artikel = None

                if filter_keywords:
                    for entry in feed.entries[:20]:
                        teks = (entry.title + " " + entry.get("summary", "")).lower()
                        if any(kw in teks for kw in filter_keywords):
                            artikel = entry
                            break

                if not artikel:
                    artikel = feed.entries[0]

                if artikel:
                    summary = bersihkan_html(artikel.get("summary", artikel.get("description", "")))
                    hasil_kategori[kategori] = {
                        "sumber": sumber["name"],
                        "judul": artikel.title.strip().replace("\ufffd", "").replace("", ""),
                        "link": artikel.link,
                        "ringkasan": summary
                    }
                    break
            except Exception as e:
                print(f"[Failover] Gagal pada {sumber['name']}: {e}")
                continue

    return hasil_kategori

def dapatkan_salam_wib():
    """Sapaan natural tanpa template robot."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_wib = now_utc + datetime.timedelta(hours=7)
    jam = now_wib.hour

    if 13 <= jam < 19:
        return "Sore rekan-rekan, ada beberapa info menarik seputar isu lingkungan dan industri tech hari ini:"
    else:
        return "Pagi team, semoga sehat selalu dan lancar aktivitasnya. Pagi ini ada update penting dari industri tech dan lingkungan:"

def potong_kalimat(teks, batas=180):
    """Memotong kalimat secara natural pada tanda titik terdekat."""
    if len(teks) <= batas:
        return teks
    potongan = teks[:batas]
    posisi_titik = potongan.rfind(".")
    if posisi_titik > 60:
        return potongan[:posisi_titik + 1]
    return potongan.rsplit(" ", 1)[0] + "..."

def buat_narasi_topik(kategori, item):
    """
    Format penulisan Stop-Slop:
    1. Tanpa klise AI ("Langkah adaptasi iklim ini sangat krusial", "menjadi pengingat penting").
    2. Langsung ke fakta dan konteks masalah nyata (seperti gaya tulisan di screenshot).
    3. Nada santai rekan kerja (mengalir wajar).
    4. Link disajikan langsung di bawahnya.
    """
    judul = item["judul"]
    summary = item["ringkasan"]
    link = item["link"]
    ringkas = potong_kalimat(summary) if summary else ""

    if kategori == "Renewable Energy & Lingkungan":
        return (
            f"Terkait dampak iklim dan lingkungan, ada catatan soal *{judul}*.\n\n"
            f"{ringkas}\n"
            f"Kondisi ini bikin tantangan ketahanan pangan dan adaptasi lingkungan makin nyata di lapangan, "
            f"terutama dampaknya ke ekosistem air dan pasokan lokal.\n\n"
            f"Selengkapnya dapat dibaca di sini:\n{link}"
        )

    elif kategori == "Cyber Security":
        return (
            f"Dari ranah keamanan siber, update terbaru: *{judul}*.\n\n"
            f"{ringkas}\n"
            f"Peredaran data di ruang publik ini menegaskan pentingnya audit berkala "
            f"dan verifikasi sistem autentikasi di tiap unit operasional.\n\n"
            f"Detail beritanya:\n{link}"
        )

    elif kategori == "AI & Data Center":
        return (
            f"Soal infrastruktur AI dan komputasi, perkembangan soal *{judul}*.\n\n"
            f"{ringkas}\n"
            f"Pertumbuhan model kecerdasan buatan saat ini terus menuntut kesiapan kapasitas data center "
            f"dan efisiensi daya listrik yang jauh lebih hemat.\n\n"
            f"Baca selengkapnya:\n{link}"
        )

    else:  # Tech & Inovasi
        return (
            f"Sementara dari inovasi perangkat teknologi: *{judul}*.\n\n"
            f"{ringkas}\n"
            f"Integrasi fitur baru di perangkat pintar makin fokus ke akurasi sensor dan efisiensi baterai.\n\n"
            f"Selengkapnya:\n{link}"
        )

def susun_pesan(berita):
    """
    Menyusun pesan bergaya human-to-human:
    - Tanpa emoji berderet-deret di setiap baris
    - Menggunakan pembatas garis bersih
    - Menghilangkan frasa template AI
    """
    salam = dapatkan_salam_wib()
    daftar_blok = []

    urutan = [
        "Renewable Energy & Lingkungan",
        "Cyber Security",
        "AI & Data Center",
        "Tech & Inovasi"
    ]

    for kat in urutan:
        item = berita.get(kat)
        if item:
            daftar_blok.append(buat_narasi_topik(kat, item))

    # Gabungkan dengan pembatas garis tunggal yang bersih
    isi_pesan = "\n\n─────────────────────\n\n".join(daftar_blok)

    pesan_final = f"{salam}\n\n{isi_pesan}"
    return pesan_final

def kirim_ke_whatsapp(pesan):
    """Mengirim pesan via Fonnte dengan proteksi anti-ban."""
    import time
    import random

    token = os.getenv("FONNTE_TOKEN")
    target = os.getenv("WA_TARGET_NUMBER")

    if not token or not target:
        print("[PERINGATAN] FONNTE_TOKEN atau WA_TARGET_NUMBER belum diset.")
        print("Mencetak hasil pesan ke konsol:\n")
        print(pesan)
        return False

    url = "https://api.fonnte.com/send"
    headers = {"Authorization": token}

    jeda_acak = random.randint(3, 7)
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
    berita_terkumpul = ambil_berita_terbaru()
    pesan_siap_kirim = susun_pesan(berita_terkumpul)
    kirim_ke_whatsapp(pesan_siap_kirim)
