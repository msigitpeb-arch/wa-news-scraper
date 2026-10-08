import os
import sys
import datetime
import requests
import feedparser
import re
from bs4 import BeautifulSoup

# Pastikan output konsol mendukung Unicode (Emoji) di Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# KONFIGURASI SUMBER BERITA KREDIBEL (10 PORTAL UTAMA INDONESIA)
# ==============================================================================
# Prioritas portal media Indonesia:
# 1. Antara News (antaranews.com - Kantor Berita Nasional)
# 2. CNN Indonesia (cnnindonesia.com/teknologi)
# 3. CNBC Indonesia (cnbcindonesia.com/tech)
# 4. Detikcom / DetikINET (inet.detik.com)
# 5. Mongabay Indonesia (mongabay.co.id)
# 6. Sindonews (tekno.sindonews.com)
# 7. Katadata (katadata.co.id/digital)
# 8. Republika (republika.co.id/rss/inovasi)
# 9. Jagat Review (jagatreview.com)
# 10. Gizmologi (gizmologi.id)
# ==============================================================================
FEEDS = {
    # 1. Renewable Energy & Lingkungan
    "Renewable Energy & Lingkungan": [
        {"name": "Mongabay Indonesia", "url": "https://www.mongabay.co.id/feed/"},
        {"name": "Katadata (Lingkungan & Energi)", "url": "https://katadata.co.id/rss/digital", "filter": ["energi", "iklim", "emisi", "hijau", "plts", "karbon", "listrik", "lingkungan", "air"]},
        {"name": "Antara News (Lingkungan)", "url": "https://www.antaranews.com/rss/terkini.xml", "filter": ["lingkungan", "iklim", "energi", "plts", "hijau", "ebt", "sampah", "hutan", "kebakaran", "kekeringan", "air"]},
    ],

    # 2. Cyber Security
    "Cyber Security": [
        {"name": "CNN Indonesia (Keamanan & Tekno)", "url": "https://www.cnnindonesia.com/teknologi/rss", "filter": ["bssn", "data", "kebocoran", "hacker", "siber", "keamanan", "serangan", "bobol", "malware", "ransomware", "security", "phishing"]},
        {"name": "Detikcom (Inet Security)", "url": "https://inet.detik.com/rss", "filter": ["hacker", "siber", "bobol", "malware", "ransomware", "kebocoran", "keamanan", "data", "phishing", "dark web"]},
        {"name": "Antara News (Siber)", "url": "https://www.antaranews.com/rss/tekno.xml", "filter": ["siber", "keamanan", "hacker", "malware", "data", "kebocoran", "bssn", "serangan"]},
        {"name": "Sindonews (Siber)", "url": "https://tekno.sindonews.com/rss", "filter": ["siber", "hacker", "malware", "data", "keamanan", "bobol"]},
    ],

    # 3. AI & Data Center
    "AI & Data Center": [
        {"name": "CNBC Indonesia (Tech & AI)", "url": "https://www.cnbcindonesia.com/tech/rss", "filter": ["ai", "data center", "server", "komputasi", "chip", "nvidia", "cloud", "intel", "teknologi", "openai"]},
        {"name": "Katadata (Digital & AI)", "url": "https://katadata.co.id/rss/digital", "filter": ["ai", "kecerdasan", "data center", "cloud", "startup", "komputasi", "chip"]},
        {"name": "Detikcom (Inet AI)", "url": "https://inet.detik.com/rss", "filter": ["ai", "data center", "openai", "chatgpt", "chip", "nvidia", "cloud", "server"]},
        {"name": "Republika (Inovasi & AI)", "url": "https://www.republika.co.id/rss/inovasi", "filter": ["ai", "teknologi", "komputasi", "data", "sistem", "digital"]},
    ],

    # 4. Tech & Inovasi Perkembangan Teknologi
    "Tech & Inovasi": [
        {"name": "Antara News (Tekno)", "url": "https://www.antaranews.com/rss/tekno.xml"},
        {"name": "Detikcom (Inet)", "url": "https://inet.detik.com/rss"},
        {"name": "Jagat Review", "url": "https://www.jagatreview.com/feed/"},
        {"name": "Gizmologi", "url": "https://gizmologi.id/feed/"},
        {"name": "Sindonews (Tekno)", "url": "https://tekno.sindonews.com/rss"},
    ]
}

def parse_feed_dengan_headers(url):
    """Mengambil RSS Feed dengan browser headers agar tidak terblokir firewall media."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        return feedparser.parse(resp.content)
    except Exception:
        return feedparser.parse(url)

def is_english_text(text):
    """Mendeteksi apakah teks berbahasa Inggris."""
    if not text:
        return False
    common_en = {"the", "and", "for", "with", "from", "about", "this", "that", "are", "was", "were", "of", "in", "to", "on", "at", "by", "is"}
    words = set(text.lower().replace(":", " ").replace("-", " ").replace(".", " ").replace(",", " ").split())
    en_matches = len(words.intersection(common_en))
    id_matches = len(words.intersection({"yang", "di", "dan", "dari", "untuk", "ini", "itu", "pada", "oleh", "ke", "adalah"}))
    return en_matches >= 2 or (en_matches >= 1 and id_matches == 0)

def poles_bahasa_indonesia(teks):
    """Poles terjemahan agar mengalir alami (Stop-Slop) dan tidak kaku ala robot."""
    if not teks:
        return ""
    replacements = {
        "Pusat Data": "Data Center",
        "pusat data": "data center",
        "Kecerdasan Buatan": "AI",
        "kecerdasan buatan": "AI",
        "situs Edge": "fasilitas Edge Data Center",
        "Situs Edge": "Fasilitas Edge Data Center",
        "pra-konstruksi": "fase awal pra-konstruksi",
        "merupakan sebuah": "adalah",
        "secara signifikan": "nyata",
        "sangat penting": "krusial",
        "pada hari ini": "hari ini",
    }
    for lama, baru in replacements.items():
        teks = teks.replace(lama, baru)
    return teks.strip()

def terjemahkan_ke_indonesia(teks):
    """Menerjemahkan teks bahasa Inggris ke Bahasa Indonesia murni jika ada istilah asing."""
    if not teks or not teks.strip():
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "auto", "tl": "id", "dt": "t", "q": teks}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, params=params, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            hasil = "".join([s[0] for s in data[0] if s and s[0]])
            return poles_bahasa_indonesia(hasil)
    except Exception as e:
        print(f"[Translate Warn] Gagal menerjemahkan: {e}")
    return teks

def bersihkan_html(raw_html):
    """Membersihkan tag HTML dan karakter aneh dari deskripsi feed."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = text.replace("\ufffd", " ")
    return " ".join(text.split())

def bersihkan_teks_berita(teks):
    """Membersihkan tag jurnalisme kota/media dan merapikan spasi."""
    if not teks:
        return ""
    # Hilangkan prefix kota/media pers (cth: 'Jakarta (ANTARA) -', 'Jakarta, CNN Indonesia --')
    pattern = r'^(?:[A-Za-z\s]{2,20}\s*\([A-Za-z\s]{2,12}\)|[A-Za-z\s]{2,20},\s*[A-Za-z0-9\s]{2,20}\s*--|[A-Za-z\s]{2,20},\s*[A-Za-z0-9\s]{2,20}\s*-)\s*[-–—]?\s*'
    teks = re.sub(pattern, '', teks)
    teks = " ".join(teks.split())
    # Bersihkan sisa tanda baca di awal kalimat jika ada
    teks = teks.lstrip(". ,;:!-–—\t\n")
    return teks

def selesaikan_kalimat(teks, max_kalimat=2):
    """Memastikan teks berakhir pada tanda titik tanpa terpotong elipsis."""
    if not teks:
        return ""
    teks = re.sub(r'\s*\.{2,}\s*$', '', teks).strip()
    teks = bersihkan_teks_berita(teks)
    kalimat_list = re.split(r'(?<=[.!?])\s+', teks)
    hasil = []
    total_len = 0
    for k in kalimat_list:
        k = k.strip()
        if not k:
            continue
        hasil.append(k)
        total_len += len(k)
        if total_len >= 130 or len(hasil) >= max_kalimat:
            break
    res = ' '.join(hasil)
    if res and not res.endswith('.'):
        res += '.'
    return res

def ekstrak_dua_paragraf(link, fallback_summary):
    """
    Mengambil 2 paragraf compact dari artikel:
    Paragraf 1: Fakta inti berita (1-2 kalimat).
    Paragraf 2: Konteks lanjutan / dampak / latar belakang (1-2 kalimat).
    """
    p1 = ""
    p2 = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(link, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()
            selectors = [
                "div.detail-text", "div.post-content", "div.read__content",
                "div.detail__body-text", "article", "div.entry-content", "div.content"
            ]
            container = None
            for sel in selectors:
                c = soup.select_one(sel)
                if c:
                    container = c
                    break
            if container:
                paragraphs = container.find_all("p")
                ps = []
                for p_tag in paragraphs:
                    txt = bersihkan_teks_berita(p_tag.get_text(separator=" ", strip=True))
                    if len(txt) > 50 and not txt.lower().startswith(("baca juga", "simak", "foto:", "video:", "iklan")):
                        if not txt.endswith(":"):
                            clean_p = selesaikan_kalimat(txt, max_kalimat=2)
                            if clean_p and clean_p not in ps:
                                ps.append(clean_p)
                    if len(ps) >= 2:
                        break
                if len(ps) >= 2:
                    p1, p2 = ps[0], ps[1]
                elif len(ps) == 1:
                    p1 = ps[0]
    except Exception:
        pass

    # Fallback jika belum dapat 2 paragraf
    if not p1:
        clean_fb = bersihkan_teks_berita(fallback_summary)
        p1 = selesaikan_kalimat(clean_fb, max_kalimat=2)

    if not p2:
        clean_fb = bersihkan_teks_berita(fallback_summary)
        kalimat_fb = re.split(r'(?<=[.!?])\s+', clean_fb)
        if len(kalimat_fb) >= 3:
            p2 = selesaikan_kalimat(" ".join(kalimat_fb[1:3]), max_kalimat=2)
            if p2 == p1:
                p2 = ""

    return p1, p2

def ambil_berita_terbaru():
    """Mengambil berita terhangat per kategori dari 10 portal berita Indonesia."""
    hasil_kategori = {}

    for kategori, daftar_sumber in FEEDS.items():
        hasil_kategori[kategori] = None
        for sumber in daftar_sumber:
            try:
                feed = parse_feed_dengan_headers(sumber["url"])
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
                    judul = artikel.title.strip().replace("\ufffd", "").replace("", "")
                    link = artikel.link
                    p1, p2 = ekstrak_dua_paragraf(link, artikel.get("summary", artikel.get("description", "")))

                    # Terjemahkan jika ada judul/isi yang berbahasa Inggris (Stop-Slop Full Indonesia)
                    if is_english_text(judul):
                        judul = terjemahkan_ke_indonesia(judul)
                    if is_english_text(p1):
                        p1 = terjemahkan_ke_indonesia(p1)
                    if is_english_text(p2):
                        p2 = terjemahkan_ke_indonesia(p2)

                    hasil_kategori[kategori] = {
                        "sumber": sumber["name"],
                        "judul": judul,
                        "link": link,
                        "p1": p1,
                        "p2": p2
                    }
                    break
            except Exception as e:
                print(f"[Failover] Gagal pada {sumber['name']}: {e}")
                continue

    return hasil_kategori

def dapatkan_salam_wib():
    """Sapaan natural fleksibel sesuai jam eksekusi cron job."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_wib = now_utc + datetime.timedelta(hours=7)
    jam = now_wib.hour

    if 5 <= jam < 11:
        sapaan = "Pagi rekan-rekan"
    elif 11 <= jam < 15:
        sapaan = "Siang rekan-rekan"
    elif 15 <= jam < 19:
        sapaan = "Sore rekan-rekan"
    else:
        sapaan = "Malam rekan-rekan"

    return f"{sapaan}, ada beberapa update penting seputar industri tech dan lingkungan hari ini:"

def buat_narasi_topik(kategori, item):
    """
    Format penulisan Stop-Slop 2 Paragraf Compact:
    - Judul tebal
    - Paragraf 1: Fakta inti berita (1-2 kalimat utuh)
    - Paragraf 2: Konteks lanjutan / dampak (1-2 kalimat utuh)
    - Link sumber di baris penutup
    """
    judul = item["judul"]
    p1 = item["p1"]
    p2 = item.get("p2", "")
    link = item["link"]

    # Proteksi ganda jika masih ada sisa bahasa Inggris
    if is_english_text(judul):
        judul = terjemahkan_ke_indonesia(judul)
    if is_english_text(p1):
        p1 = terjemahkan_ke_indonesia(p1)
    if p2 and is_english_text(p2):
        p2 = terjemahkan_ke_indonesia(p2)

    if p2:
        return f"*{judul}*\n{p1}\n\n{p2}\n\nSelengkapnya:\n{link}"
    else:
        return f"*{judul}*\n{p1}\n\nSelengkapnya:\n{link}"

def susun_pesan(berita):
    """
    Menyusun pesan bergaya human-to-human:
    - Ringkas dan padat tanpa paragraf redundan
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
