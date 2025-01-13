import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# URL target
url = "https://epg.pw/areas/id/epg.html?lang=en"

# Mengambil data dari URL
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Parsing data (disesuaikan dengan struktur HTML di halaman target)
programs = []
for item in soup.find_all("div", class_="program-item"):  # Ganti dengan elemen HTML yang sesuai
    time = item.find("div", class_="time").text.strip()
    title = item.find("div", class_="title").text.strip()
    description = item.find("div", class_="description").text.strip()
    programs.append({"time": time, "title": title, "description": description})

# Membuat struktur XMLTV
tv = ET.Element("tv")
for program in programs:
    channel = ET.SubElement(tv, "programme", start=program["time"])
    title = ET.SubElement(channel, "title")
    title.text = program["title"]
    desc = ET.SubElement(channel, "desc")
    desc.text = program["description"]

# Menyimpan ke file XML
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print("EPG berhasil disimpan ke epg.xml!")
