import requests
import time
import urllib.parse

# === KENDİ BİLGİLERİNİ GİR ===
BEARER_TOKEN ="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E" # Buraya geçerli token'ı koy
OUTPUT_M3U = "vodden_proxy.m3u"
VOD_ID_FILE = "vod_ids.txt"
WORKER_URL_BASE = "https://umittvkablovod.umitm0d.workers.dev/?film="

HEADERS = {
    "Authorization": BEARER_TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://tvheryerde.com",
    "Origin": "https://tvheryerde.com"
}

def load_vod_ids(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] {filename} bulunamadı. Lütfen dosyayı oluşturun.")
        return []

def get_film_detail(vod_id):
    url = "https://core-api.kablowebtv.com/api/vod/detail"
    try:
        res = requests.get(url, headers=HEADERS, params={"VodUId": vod_id}, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("IsSucceeded") and data.get("Data"):
            return data["Data"][0]
    except Exception as e:
        print(f"[!] Hata: {vod_id} → {e}")
    return None

def write_m3u_proxy(films):
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for film in films:
            title = film.get("Title", "Bilinmeyen")
            uid = film.get("UId")
            logo = ""
            for poster in film.get("Posters", []):
                if poster.get("Type", "").lower() == "listing":
                    logo = poster.get("ImageUrl", "")
                    break
            encoded_title = urllib.parse.quote(title)
            proxy_url = f"{WORKER_URL_BASE}{encoded_title}"
            f.write(f'#EXTINF:-1 tvg-id="{uid}" tvg-logo="{logo}" group-title="VOD", {title}\n{proxy_url}\n')
    print(f"[✓] {len(films)} film yazıldı → {OUTPUT_M3U}")

def main():
    vod_ids = load_vod_ids(VOD_ID_FILE)
    if not vod_ids:
        return

    collected = []
    print(f"[▶] {len(vod_ids)} adet film işleniyor...")

    for i, vid in enumerate(vod_ids):
        print(f"[{i+1}/{len(vod_ids)}] Alınıyor: {vid}")
        detail = get_film_detail(vid)
        if detail and detail.get("StreamData", {}).get("DashStreamUrl"):
            collected.append(detail)
        time.sleep(0.5)  # Ban yememek için bekleme

    write_m3u_proxy(collected)

if __name__ == "__main__":
    main()
