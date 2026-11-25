#!/usr/bin/env python3
import os
import requests

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projects", "cash_and_crown", "day1_rockstar", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "CashCrownBot/1.0 (https://github.com/pavanabharath24/editor; korukondapavanbharath@gmail.com)"
}

FILES = [
    ("rockstar_logo.png", "File:Rockstar Games Logo.svg"),
    ("gta_logo.png", "File:Grand Theft Auto logo.svg"),
    ("take_two_logo.png", "File:Take-Two Interactive Logo.svg"),
    ("lemmings_art.jpg", "File:Lemmings-Cover.jpg"),
    ("gta3_cover.jpg", "File:GTA3boxart.jpg"),
    ("gta_vice_city_cover.jpg", "File:Vice-city-cover.jpg"),
    ("gta_san_andreas_cover.jpg", "File:GTASABOX.jpg"),
    ("gta4_cover.jpg", "File:Grand Theft Auto IV cover.jpg"),
    ("gta5_cover.jpg", "File:Grand Theft Auto V.png"),
    ("rdr2_cover.jpg", "File:Red Dead Redemption II.jpg"),
    ("bully_cover.jpg", "File:Bully Cover.jpg"),
    ("max_payne_3_cover.jpg", "File:Max Payne 3 Cover Art.jpg")
]

def get_wikimedia_url(file_title):
    api = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }
    r = requests.get(api, params=params, headers=HEADERS, timeout=10)
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for p in pages.values():
        info = p.get("imageinfo", [])
        if info:
            return info[0].get("url")
    return None

def main():
    print("[+] Querying Wikipedia API for direct asset URLs...")
    for filename, title in FILES:
        dest = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            print(f"    [✓] {filename} already exists")
            continue
        url = get_wikimedia_url(title)
        if not url:
            # try commons api
            api_c = "https://commons.wikimedia.org/w/api.php"
            params = {
                "action": "query",
                "titles": title,
                "prop": "imageinfo",
                "iiprop": "url",
                "format": "json"
            }
            rc = requests.get(api_c, params=params, headers=HEADERS, timeout=10)
            data_c = rc.json()
            for p in data_c.get("query", {}).get("pages", {}).values():
                info = p.get("imageinfo", [])
                if info:
                    url = info[0].get("url")
        if url:
            print(f"    -> Downloading {filename} from {url}...")
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(res.content)
                print(f"    [✓] Saved {filename} ({len(res.content)} bytes)")
            else:
                print(f"    [!] Failed to download: status {res.status_code}")
        else:
            print(f"    [!] No URL found for {title}")

if __name__ == "__main__":
    main()
