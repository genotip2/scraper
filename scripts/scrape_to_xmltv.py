import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.dom import minidom

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

# Membuat struktur XMLTV
tv = ET.Element("tv")
for program in programs:
    channel = ET.SubElement(tv, "programme", start=program["time"], channel=program["channel"])
    title = ET.SubElement(channel, "title")
    title.text = program["title"]

# Memformat XML agar lebih rapi
def prettify_xml(element):
    rough_string = ET.tostring(element, encoding="utf-8", method="xml")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Menyimpan ke file XML
formatted_xml = prettify_xml(tv)
with open("epg.xml", "w", encoding="utf-8") as f:
    f.write(formatted_xml)

print("EPG berhasil disimpan ke epg.xml!")
