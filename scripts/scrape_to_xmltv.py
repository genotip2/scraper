import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# URL target
url = "https://epg.pw/areas/id/epg.html?lang=en"

# Mengambil data dari URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Parsing data dari tabel
programs = []
table = soup.find("table", class_="table is-bordered is-striped")
if table:
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) > 1:  # Setiap baris memiliki beberapa kolom
            channel_name = cells[0].text.strip()
            for cell in cells[1:]:
                time_tag = cell.find("span", class_="tag is-primary")
                title = cell.get_text(strip=True).replace(time_tag.text.strip(), "") if time_tag else ""
                time = time_tag.text.strip() if time_tag else ""
                programs.append({
                    "channel": channel_name,
                    "time": time,
                    "title": title,
                })

# Mengonversi waktu ke format lengkap dan mengelompokkan program berdasarkan channel
for program in programs:
    # Mengubah format waktu dari 'YYYY-MM-DD HH:MM' menjadi 'YYYYMMDDHHMMSS +0000'
    program["time"] = datetime.strptime(f"2025-01-12 {program['time']}", "%Y-%m-%d %H:%M").strftime("%Y%m%d%H%M%S +0000")

# Mengelompokkan program berdasarkan channel
channel_programs = {}
for program in programs:
    channel = program["channel"]
    if channel not in channel_programs:
        channel_programs[channel] = []
    channel_programs[channel].append(program)

# Membuat struktur XMLTV
tv = ET.Element("tv")

# Membuat elemen <channel>
channel_ids = {}
for channel_name, program_list in channel_programs.items():
    channel_id = channel_name.replace(" ", "").replace("&", "and")
    channel_ids[channel_name] = channel_id
    channel_elem = ET.SubElement(tv, "channel", id=channel_id)
    ET.SubElement(channel_elem, "display-name").text = channel_name
    ET.SubElement(channel_elem, "icon", src="https://i.imgur.com/NFFQNhq.png")
    ET.SubElement(channel_elem, "url").text = "https://firstmedia.com"

# Membuat elemen <programme>
for channel_name, program_list in channel_programs.items():
    for i, program in enumerate(program_list):
        start_time = program["time"]
        stop_time = program_list[i + 1]["time"] if i + 1 < len(program_list) else ""
        channel_id = channel_ids[channel_name]
        programme_elem = ET.SubElement(tv, "programme", start=start_time, stop=stop_time, channel=channel_id)
        title_elem = ET.SubElement(programme_elem, "title", lang="en")
        title_elem.text = program["title"]

# Menyimpan ke file XML
with open("epg.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    for element in tv:
        f.write(ET.tostring(element, encoding="unicode").strip() + "\n")

print("EPG berhasil disimpan ke epg.xml!")
