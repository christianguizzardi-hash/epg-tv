import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, timezone
import requests

# Lista canali mappata esattamente sui nomi del tuo provider
CHANNELS = [
    # Primafila con i nomi esatti visibili in app
    {"id": "primafila1.it", "name": "IT| SKY PRIMAFILA PREMIERE 1 4K", "sky_id": "3501"},
    {"id": "primafila2.it", "name": "IT| SKY PRIMAFILA PREMIERE 2 4K", "sky_id": "3502"},
    {"id": "primafila3.it", "name": "IT| SKY PRIMAFILA PREMIERE 3 4K", "sky_id": "3503"},
    {"id": "primafila4.it", "name": "IT| SKY PRIMAFILA PREMIERE 4 4K", "sky_id": "3504"},
    {"id": "primafila5.it", "name": "IT| SKY PRIMAFILA PREMIERE 5 4K", "sky_id": "3505"},
    {"id": "primafila6.it", "name": "IT| SKY PRIMAFILA PREMIERE 6 4K", "sky_id": "3506"},
    {"id": "primafila7.it", "name": "IT| SKY PRIMAFILA PREMIERE 7 4K", "sky_id": "3507"},
    {"id": "primafila8.it", "name": "IT| SKY PRIMAFILA PREMIERE 8 4K", "sky_id": "3508"},
    {"id": "primafila9.it", "name": "IT| SKY PRIMAFILA PREMIERE 9 4K+", "sky_id": "3509"},
    {"id": "primafila10.it", "name": "IT| SKY PRIMAFILA PREMIERE 10 4K", "sky_id": "3510"},
    {"id": "primafila11.it", "name": "IT| SKY PRIMAFILA PREMIERE 11 4K", "sky_id": "3511"},
    
    # Variante senza "PREMIERE" o "4K" per massima compatibilità
    {"id": "primafila1_alt.it", "name": "Sky Primafila 1", "sky_id": "3501"},
    {"id": "primafila2_alt.it", "name": "Sky Primafila 2", "sky_id": "3502"},
    {"id": "primafila3_alt.it", "name": "Sky Primafila 3", "sky_id": "3503"},

    # DAZN
    {"id": "dazn1.it", "name": "Zona DAZN", "sky_id": "214"},
    {"id": "dazn2.it", "name": "Zona DAZN 2", "sky_id": "215"},
    {"id": "dazn1_alt.it", "name": "IT| ZONA DAZN", "sky_id": "214"},
    {"id": "dazn2_alt.it", "name": "IT| ZONA DAZN 2", "sky_id": "215"},
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
