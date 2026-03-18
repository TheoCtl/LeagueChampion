"""
Download sprites for all Pokemon already in POKEMON_DB.
Run once to populate the sprites/ folder for existing Pokemon.
"""
import os
import re
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

SPRITES_DIR = "sprites"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
DATA_FILE = "data.py"


def get_all_pokemon():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"POKEMON_DB\s*=\s*\{", content)
    if not m:
        return []
    names = re.findall(r'^\s{4}"([A-Z][a-z\-\'. ]+)":\s*\{', content[m.start():], re.MULTILINE)
    return names


def download_sprite(name, session):
    dest = os.path.join(SPRITES_DIR, f"{name}.png")
    if os.path.exists(dest):
        print(f"  {name}: already exists, skipping")
        return True
    url_name = urllib.parse.quote(f"{name} (Pokémon)")
    url = f"https://bulbapedia.bulbagarden.net/wiki/{url_name}"
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", class_="roundy")
        if not table:
            print(f"  {name}: no infobox found")
            return False
        img = table.find("img")
        if not img or not img.get("src"):
            print(f"  {name}: no image found")
            return False
        img_url = img["src"]
        img_resp = session.get(img_url, timeout=30)
        img_resp.raise_for_status()
        with open(dest, "wb") as f:
            f.write(img_resp.content)
        print(f"  {name}: downloaded")
        return True
    except Exception as e:
        print(f"  {name}: error - {e}")
        return False


def main():
    os.makedirs(SPRITES_DIR, exist_ok=True)
    names = get_all_pokemon()
    print(f"Found {len(names)} Pokemon in {DATA_FILE}")
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    ok = 0
    for i, name in enumerate(names):
        if download_sprite(name, session):
            ok += 1
        time.sleep(0.5)  # Rate-limit between each download
    print(f"\nDone: {ok}/{len(names)} sprites downloaded to {SPRITES_DIR}/")


if __name__ == "__main__":
    main()
