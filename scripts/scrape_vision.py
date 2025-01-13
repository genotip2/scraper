import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# URL target
url = "https://www.mncvision.id/schedule/formSearch"

# Tanggal hari ini
today_date = datetime.now().strftime('%Y-%m-%d')

# Header untuk menghindari blokir
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Data POST
data = {
    "fdate": today_date,
    "submit": "Submit"
}

# Kirim permintaan POST
response = requests.post(url, headers=headers, data=data)
soup = BeautifulSoup(response.text, 'html.parser')

# Parsing data jadwal
programs = []
channels = {}
schedule_items = soup.find_all("div", class_="schedule-item")  # Sesuaikan selector ini dengan struktur halaman

if schedule_items:
    for item in schedule_items:
        # Ambil informasi channel, waktu, judul, dan sinopsis
        channel_name = "MNC Vision"  # Sesuaikan jika channel ada di halaman
        channel_id = channel_name.replace(" ", "")
        time = item.find("span", class_="time").text.strip() if item.find("span", class_="time") else None
        title = item.find("h3").text.strip() if item.find("h3") else "No Title"
        synopsis = item.find("p", class_="synopsis").text.strip() if item.find("p", class_="synopsis") else "No Synopsis"

        if time:
            # Ubah waktu ke format lengkap
            start_time = datetime.strptime(f"{today_date} {time}", "%Y-%m-%d %H:%M")
            start_time_str = start_time.strftime("%Y%m%d%H%M%S +0000")
        else:
            continue

        programs.append({
            "channel": channel_name,
            "channel_id": channel_id,
            "start": start_time_str,
            "title": title,
            "synopsis": synopsis
        })

        # Tambahkan channel jika belum ada
        if channel_id not in channels:
            channels[channel_id] = {"display_name": channel_name, "icon": ""}

# Membuat struktur XMLTV
tv = ET.Element("tv")

# Tambahkan elemen <channel>
for channel_id, channel_info in channels.items():
    channel = ET.SubElement(tv, "channel", id=channel_id)
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_info["display_name"]
    icon = ET.SubElement(channel, "icon", src=channel_info["icon"])

# Tambahkan elemen <programme>
for program in programs:
    programme = ET.SubElement(
        tv,
        "programme",
        start=program["start"],
        stop="",
        channel=program["channel_id"],
    )
    title = ET.SubElement(programme, "title", lang="en")
    title.text = program["title"]
    desc = ET.SubElement(programme, "desc", lang="en")
    desc.text = program["synopsis"]

# Simpan ke file XML
tree = ET.ElementTree(tv)
with open("epg.xml", "wb") as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    tree.write(f, encoding="utf-8", xml_declaration=False)

print("EPG berhasil disimpan ke epg.xml!")
