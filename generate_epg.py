import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, timezone
import requests

# Canali con EPG Reale da API Sky
SKY_REAL_CHANNELS = [
    {"xml_id": "SkyCinemaUno.it", "display": "IT| SKY CINEMA UNO UHD", "sky_id": "3001"},
    {"xml_id": "SkyCinemaPlus24.it", "display": "IT| SKY CINEMA UNO24 UHD", "sky_id": "3002"},
    {"xml_id": "SkyCinemaDue.it", "display": "IT| SKY CINEMA DUE UHD", "sky_id": "3003"},
    {"xml_id": "SkyCinemaDuePlus24.it", "display": "IT| SKY CINEMA DUE24 UHD", "sky_id": "3004"},
    {"xml_id": "SkyCinemaCollection.it", "display": "IT| SKY CINEMA COLLECTION UHD", "sky_id": "3005"},
    {"xml_id": "SkyCinemaFamily.it", "display": "IT| SKY CINEMA FAMILY UHD", "sky_id": "3006"},
    {"xml_id": "SkyCinemaAction.it", "display": "IT| SKY CINEMA ACTION UHD", "sky_id": "3009"},
    {"xml_id": "SkyCinemaSuspense.it", "display": "IT| SKY CINEMA SUSPENSE UHD", "sky_id": "3011"},
    {"xml_id": "SkyCinemaRomance.it", "display": "IT| SKY CINEMA ROMANCE UHD", "sky_id": "3007"},
    {"xml_id": "SkyCinemaDrama.it", "display": "IT| SKY CINEMA DRAMA UHD", "sky_id": "3008"},
    {"xml_id": "SkyCinemaComedy.it", "display": "IT| SKY CINEMA COMEDY UHD", "sky_id": "3010"},
    {"xml_id": "SkyUno.it", "display": "IT| SKY UNO UHD", "sky_id": "1001"},
    {"xml_id": "SkyAtlantic.it", "display": "IT| SKY ATLANTIC UHD", "sky_id": "1103"},
]

# Lista canali Primafila e Premiere (mappati sui vari tvg-id possibili)
PRIMAFILA_CHANNELS = []

for i in range(1, 19):
    PRIMAFILA_CHANNELS.extend([
        {"xml_id": f"Primafila{i}.it", "display": f"IT| SKY PRIMAFILA PREMIERE {i}"},
        {"xml_id": f"IT| SKY PRIMAFILA PREMIERE {i} HD", "display": f"IT| SKY PRIMAFILA PREMIERE {i} HD"},
        {"xml_id": f"IT| SKY PRIMAFILA PREMIERE {i} UHD", "display": f"IT| SKY PRIMAFILA PREMIERE {i} UHD"},
        {"xml_id": f"IT| SKY PRIMAFILA {i} HD", "display": f"IT| SKY PRIMAFILA {i} HD"},
        {"xml_id": f"IT| SKY PRIMAFILA {i} UHD", "display": f"IT| SKY PRIMAFILA {i} UHD"}
    ])

# Vetrine
PRIMAFILA_CHANNELS.extend([
    {"xml_id": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "display": "IT| SKY PRIMAFILA PREMIERE VETRINA HD"},
    {"xml_id": "IT| VETRINA SKY PRIMAFILA UHD", "display": "IT| VETRINA SKY PRIMAFILA UHD"}
])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def format_xmltv_date(dt):
    return dt.strftime("%Y%m%d%H%M%S +0200")

def fetch_sky_epg(channel_id_sky, date_str):
    url = f"https://apicall.sky.it/v1/epg/grid/{date_str}/channel/{channel_id_sky}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            return res.json().get("events", [])
    except Exception:
        pass
    return []

def generate_primafila_slots(tv, channel_id, channel_display):
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start_time = now - timedelta(hours=6)
    end_time = now + timedelta(days=2)

    slot_duration = timedelta(hours=2)
    current_time = start_time

    while current_time < end_time:
        next_time = current_time + slot_duration
        
        prog = ET.SubElement(tv, "programme", {
            "start": format_xmltv_date(current_time),
            "stop": format_xmltv_date(next_time),
            "channel": channel_id
        })

        title = ET.SubElement(prog, "title", {"lang": "it"})
        title.text = "Sky Primafila Premiere - Programmazione Film"

        desc = ET.SubElement(prog, "desc", {"lang": "it"})
        desc.text = f"Programmazione su {channel_display}. I film Premiere ruotano a cicli continui ogni 2 ore."

        cat = ET.SubElement(prog, "category", {"lang": "it"})
        cat.text = "Cinema"

        current_time = next_time

def build_xmltv():
    tv = ET.Element("tv", {"generator-info-name": "Sky & Primafila EPG Generator"})

    all_channels = SKY_REAL_CHANNELS + PRIMAFILA_CHANNELS

    for ch in all_channels:
        channel_elem = ET.SubElement(tv, "channel", {"id": ch["xml_id"]})
        name_elem = ET.SubElement(channel_elem, "display-name")
        name_elem.text = ch["display"]

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # EPG Reale per Sky Cinema
    for ch in SKY_REAL_CHANNELS:
        events = fetch_sky_epg(ch["sky_id"], today_str)
        for ev in events:
            try:
                start_dt = datetime.fromisoformat(ev["starttime"].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(ev["endtime"].replace("Z", "+00:00"))

                prog = ET.SubElement(tv, "programme", {
                    "start": format_xmltv_date(start_dt),
                    "stop": format_xmltv_date(end_dt),
                    "channel": ch["xml_id"]
                })

                title = ET.SubElement(prog, "title", {"lang": "it"})
                title.text = ev.get("title", "Programma Sconosciuto")

                if ev.get("description"):
                    desc = ET.SubElement(prog, "desc", {"lang": "it"})
                    desc.text = ev["description"]

            except (KeyError, ValueError):
                continue

    # Slot automatici per Primafila / Premiere
    for ch in PRIMAFILA_CHANNELS:
        generate_primafila_slots(tv, ch["xml_id"], ch["display"])

    raw_xml = ET.tostring(tv, encoding="utf-8")
    reparsed = minidom.parseString(raw_xml)
    
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(reparsed.toprettyxml(indent="  "))

if __name__ == "__main__":
    build_xmltv()
