import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, timezone
import requests

CHANNELS = [
    # --- SKY CINEMA & INTRATTENIMENTO ---
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
    {"xml_id": "CrimeInvestigation.it", "display": "IT| SKY CRIME INVEST UHD", "sky_id": "1105"},
    {"xml_id": "ComedyCentral.it", "display": "IT| SKY COMEDY CENTRAL UHD", "sky_id": "1106"},

    # --- SKY PRIMAFILA (tvg-id ufficiali della tua M3U) ---
    {"xml_id": "Primafila1.it", "display": "IT| SKY PRIMAFILA 1", "sky_id": "3501"},
    {"xml_id": "Primafila2.it", "display": "IT| SKY PRIMAFILA 2", "sky_id": "3502"},
    {"xml_id": "Primafila3.it", "display": "IT| SKY PRIMAFILA 3", "sky_id": "3503"},
    {"xml_id": "Primafila4.it", "display": "IT| SKY PRIMAFILA 4", "sky_id": "3504"},
    {"xml_id": "Primafila5.it", "display": "IT| SKY PRIMAFILA 5", "sky_id": "3505"},
    {"xml_id": "Primafila6.it", "display": "IT| SKY PRIMAFILA 6", "sky_id": "3506"},
    {"xml_id": "Primafila7.it", "display": "IT| SKY PRIMAFILA 7", "sky_id": "3507"},
    {"xml_id": "Primafila8.it", "display": "IT| SKY PRIMAFILA 8", "sky_id": "3508"},
    {"xml_id": "Primafila9.it", "display": "IT| SKY PRIMAFILA 9", "sky_id": "3509"},
    {"xml_id": "Primafila10.it", "display": "IT| SKY PRIMAFILA 10", "sky_id": "3510"},
    {"xml_id": "Primafila11.it", "display": "IT| SKY PRIMAFILA 11", "sky_id": "3511"},
    {"xml_id": "Primafila12.it", "display": "IT| SKY PRIMAFILA 12", "sky_id": "3512"},
    {"xml_id": "Primafila13.it", "display": "IT| SKY PRIMAFILA 13", "sky_id": "3513"},
    {"xml_id": "Primafila14.it", "display": "IT| SKY PRIMAFILA 14", "sky_id": "3514"},
    {"xml_id": "Primafila15.it", "display": "IT| SKY PRIMAFILA 15", "sky_id": "3515"},
    {"xml_id": "Primafila16.it", "display": "IT| SKY PRIMAFILA 16", "sky_id": "3516"},
    {"xml_id": "Primafila17.it", "display": "IT| SKY PRIMAFILA 17", "sky_id": "3517"},
    {"xml_id": "Primafila18.it", "display": "IT| SKY PRIMAFILA 18", "sky_id": "3518"},

    # --- VETRINE (tvg-id vuoto, abbinati per nome) ---
    {"xml_id": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "display": "IT| SKY PRIMAFILA PREMIERE VETRINA HD", "sky_id": "3501"},
    {"xml_id": "IT| VETRINA SKY PRIMAFILA UHD", "display": "IT| VETRINA SKY PRIMAFILA UHD", "sky_id": "3501"}
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
        print(f"Errore caricamento ID {channel_id_sky}: {e}")
    return []

def build_xmltv():
    tv = ET.Element("tv", {"generator-info-name": "GitHub Actions Sky EPG Generator"})

    for ch in CHANNELS:
        channel_elem = ET.SubElement(tv, "channel", {"id": ch["xml_id"]})
        name_elem = ET.SubElement(channel_elem, "display-name")
        name_elem.text = ch["display"]

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
                        "channel": ch["xml_id"]
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
