# Skill Hermes (virtual office)

Skill untuk Hermes Agent di VPS. Pasang atau update dengan:

```bash
cd ~/wa-news-scraper && git pull
bash hermes/install_skills.sh <THREAD_ID_TOPIK_CONTENT_PLANNING>
```

## content-planning
Content planner PeopleSync (tema: masalah SaaS dan keuntungan software sekali beli).
Alur: pembuat menyusun draft → pemeriksa (subagent terpisah) mengoreksi dan memberi skor/approval → baris yang lolos disimpan ke `~/hermes-data/content-plan/peoplesync_content_plan.csv` dengan status "Menunggu review SML" → file CSV dikirim ke topik Telegram → SML membalas `approve CP-xxx`, `revisi CP-xxx <catatan>`, atau `tolak CP-xxx <alasan>`.

Pakai di Telegram: `/content-planning buat content plan 2 minggu untuk PeopleSync`
