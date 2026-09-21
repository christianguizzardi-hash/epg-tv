import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, timezone
import requests

# Mappatura con NOMI ESATTI identici alla tua lista M3U
CHANNELS = [
    # --- PRIMAFILA PREMIERE ---
    {"id": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "name": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "sky_id": "3501"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 1 4K", "name": "IT| SKY PRIMAFILA PREMIERE 1 4K", "sky_id": "3501"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 2 4K", "name": "IT| SKY PRIMAFILA PREMIERE 2 4K", "sky_id": "3502"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 3 4K", "name": "IT| SKY PRIMAFILA PREMIERE 3 4K", "sky_id": "3503"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 4 4K", "name": "IT| SKY PRIMAFILA PREMIERE 4 4K", "sky_id": "3504"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 5 4K", "name": "IT| SKY PRIMAFILA PREMIERE 5 4K", "sky_id": "3505"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 6 4K", "name": "IT| SKY PRIMAFILA PREMIERE 6 4K", "sky_id": "3506"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 7 4K", "name": "IT| SKY PRIMAFILA PREMIERE 7 4K", "sky_id": "3507"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 8 4K", "name": "IT| SKY PRIMAFILA PREMIERE 8 4K", "sky_id": "3508"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 9 4K+", "name": "IT| SKY PRIMAFILA PREMIERE 9 4K+", "sky_id": "3509"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 10 4K", "name": "IT| SKY PRIMAFILA PREMIERE 10 4K", "sky_id": "3510"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 11 4K", "name": "IT| SKY PRIMAFILA PREMIERE 11 4K", "sky_id": "3511"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 15 4K", "name": "IT| SKY PRIMAFILA PREMIERE 15 4K", "sky_id": "3515"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 16 4K", "name": "IT| SKY PRIMAFILA PREMIERE 16 4K", "sky_id": "3516"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 17 4K", "name": "IT| SKY PRIMAFILA PREMIERE 17 4K", "sky_id": "3517"},
    {"id": "IT| SKY PRIMAFILA PREMIERE 18 4K", "name": "IT| SKY PRIMAFILA PREMIERE 18 4K", "sky_id": "3518"},

    # --- PRIMAFILA UHD ---
    {"id": "IT| VETRINA SKY PRIMAFILA UHD", "name": "IT| VETRINA SKY PRIMAFILA UHD", "sky_id": "3501"},
    {"id": "IT| SKY PRIMAFILA 1 UHD", "name": "IT| SKY PRIMAFILA 1 UHD", "sky_id": "3501"},
    {"id": "IT| SKY PRIMAFILA 2 UHD", "name": "IT| SKY PRIMAFILA 2 UHD", "sky_id": "3502"},
    {"id": "IT| SKY PRIMAFILA 3 UHD", "name": "IT| SKY PRIMAFILA 3 UHD", "sky_id": "3503"},
    {"id": "IT| SKY PRIMAFILA 4 UHD", "name": "IT| SKY PRIMAFILA 4 UHD", "sky_id": "3504"},
    {"id": "IT| SKY PRIMAFILA 5 UHD", "name": "IT| SKY PRIMAFILA 5 UHD", "sky_id": "3505"},
    {"id": "IT| SKY PRIMAFILA 6 UHD", "name": "IT| SKY PRIMAFILA 6 UHD", "sky_id": "3506"},
    {"id": "IT| SKY PRIMAFILA 7 UHD", "name": "IT| SKY PRIMAFILA 7 UHD", "sky_id": "3507"},
    {"id": "IT| SKY PRIMAFILA 8 UHD", "name": "IT| SKY PRIMAFILA 8 UHD", "sky_id": "3508"},

    # --- DAZN ---
    {"id": "IT| VETRINA DAZN", "name": "IT| VETRINA DAZN", "sky_id": "214"},
    {"id": "IT| DAZN REDBULL FHD", "name": "IT| DAZN REDBULL FHD", "sky_id": "214"},
    {"id": "IT| DAZN CHANNEL FHD", "name": "IT| DAZN CHANNEL FHD", "sky_id": "214"},
    {"id": "IT| DAZN CHANNEL HD", "name": "IT| DAZN CHANNEL HD", "sky_id": "214"},
    {"id": "IT| DAZN CHANNEL HEVC", "name": "IT| DAZN CHANNEL HEVC", "sky_id": "214"},
    {"id": "IT| DAZN CHANNEL", "name": "IT| DAZN CHANNEL", "sky_id": "214"},
    {"id": "IT| DAZN DIRETTA GOL SERIE A FHD", "name": "IT| DAZN DIRETTA GOL SERIE A FHD", "sky_id": "214"},
    {"id": "IT| DAZN DIRETTA GOL SERIE A HD", "name": "IT| DAZN DIRETTA GOL SERIE A HD", "sky_id": "214"},
    {"id": "IT| DAZN DIRETTA GOL SERIE A", "name": "IT| DAZN DIRETTA GOL SERIE A", "sky_id": "214"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def format_xmltv_date(dt):
    return dt.strftime("%Y%m%d%H%M%S +0200")

def fetch_sky_epg(channel_id_sky, date_str):
    url = f"https://apicall.sky.it/v1/epg/grid/{date_str}/channel/{channel_id_sky}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json().get("events", [])
    except Exception as e:
        print(f"Errore download: {e}")
    return []

def build_xmltv():
    tv = ET.Element("tv", {"generator-info-name": "GitHub Actions EPG Generator"})

    for ch in CHANNELS:
        channel_elem = ET.SubElement(tv, "channel", {"id": ch["id"]})
        name_elem = ET.SubElement(channel_elem, "display-name")
        name_elem.text = ch["name"]

    today = datetime.now(timezone.utc)
    dates_to_fetch = [
        today.strftime("%Y-%m-%d"),
        (today + timedelta(days=1)).strftime("%Y-%m-%d")
    ]

    for ch in CHANNELS:
        for date_str in dates_to_fetch:
            events = fetch_sky_epg(ch["sky_id"], date_str)
            for ev in events:
                try:
                    start_dt = datetime.fromisoformat(ev["starttime"].replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(ev["endtime"].replace("Z", "+00:00"))

                    prog = ET.SubElement(tv, "programme", {
                        "start": format_xmltv_date(start_dt),
                        "stop": format_xmltv_date(end_dt),
                        "channel": ch["id"]
                    })

                    title = ET.SubElement(prog, "title", {"lang": "it"})
                    title.text = ev.get("title", "Programma Sconosciuto")

                    if "description" in ev and ev["description"]:
                        desc = ET.SubElement(prog, "desc", {"lang": "it"})
                        desc.text = ev["description"]

                    if "genre" in ev and ev["genre"]:
                        cat = ET.SubElement(prog, "category", {"lang": "it"})
                        cat.text = ev["genre"]

                except KeyError:
                    continue

    raw_xml = ET.tostring(tv, encoding="utf-8")
    reparsed = minidom.parseString(raw_xml)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    build_xmltv()
