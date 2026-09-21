import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, timezone
import requests

# Mappatura completa basata sugli screenshot forniti
CHANNELS = [
    # --- PRIMAFILA PREMIERE ---
    {"id": "primafila.vetrina", "name": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "sky_id": "3501"},
    {"id": "primafila1.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 1 4K", "sky_id": "3501"},
    {"id": "primafila2.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 2 4K", "sky_id": "3502"},
    {"id": "primafila3.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 3 4K", "sky_id": "3503"},
    {"id": "primafila4.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 4 4K", "sky_id": "3504"},
    {"id": "primafila5.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 5 4K", "sky_id": "3505"},
    {"id": "primafila6.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 6 4K", "sky_id": "3506"},
    {"id": "primafila7.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 7 4K", "sky_id": "3507"},
    {"id": "primafila8.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 8 4K", "sky_id": "3508"},
    {"id": "primafila9.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 9 4K+", "sky_id": "3509"},
    {"id": "primafila10.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 10 4K", "sky_id": "3510"},
    {"id": "primafila11.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 11 4K", "sky_id": "3511"},
    {"id": "primafila15.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 15 4K", "sky_id": "3515"},
    {"id": "primafila16.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 16 4K", "sky_id": "3516"},
    {"id": "primafila17.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 17 4K", "sky_id": "3517"},
    {"id": "primafila18.premiere", "name": "IT| SKY PRIMAFILA PREMIERE 18 4K", "sky_id": "3518"},

    # --- PRIMAFILA UHD ---
    {"id": "primafila.vetrinauhd", "name": "IT| VETRINA SKY PRIMAFILA UHD", "sky_id": "3501"},
    {"id": "primafila1.uhd", "name": "IT| SKY PRIMAFILA 1 UHD", "sky_id": "3501"},
    {"id": "primafila2.uhd", "name": "IT| SKY PRIMAFILA 2 UHD", "sky_id": "3502"},
    {"id": "primafila3.uhd", "name": "IT| SKY PRIMAFILA 3 UHD", "sky_id": "3503"},
    {"id": "primafila4.uhd", "name": "IT| SKY PRIMAFILA 4 UHD", "sky_id": "3504"},
    {"id": "primafila5.uhd", "name": "IT| SKY PRIMAFILA 5 UHD", "sky_id": "3505"},
    {"id": "primafila6.uhd", "name": "IT| SKY PRIMAFILA 6 UHD", "sky_id": "3506"},
    {"id": "primafila7.uhd", "name": "IT| SKY PRIMAFILA 7 UHD", "sky_id": "3507"},
    {"id": "primafila8.uhd", "name": "IT| SKY PRIMAFILA 8 UHD", "sky_id": "3508"},

    # --- DAZN ---
    {"id": "dazn.vetrina", "name": "IT| VETRINA DAZN", "sky_id": "214"},
    {"id": "dazn.redbull", "name": "IT| DAZN REDBULL FHD", "sky_id": "214"},
    {"id": "dazn.ch1", "name": "IT| DAZN CHANNEL FHD", "sky_id": "214"},
    {"id": "dazn.ch2", "name": "IT| DAZN CHANNEL HD", "sky_id": "214"},
    {"id": "dazn.ch3", "name": "IT| DAZN CHANNEL HEVC", "sky_id": "214"},
    {"id": "dazn.ch4", "name": "IT| DAZN CHANNEL", "sky_id": "214"},
    {"id": "dazn.z1", "name": "Zona DAZN", "sky_id": "214"},
    {"id": "dazn.z2", "name": "Zona DAZN 2", "sky_id": "215"}
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
