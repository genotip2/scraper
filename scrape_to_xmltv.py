import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import os

# URL target untuk scraping
URL = "https://epg.pw/areas/id/epg.html?lang=en"

# Fungsi untuk mengambil data EPG
def fetch_epg():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    programs = []

    # Sesuaikan parsing sesuai struktur HTML
    for item in soup.find_all("div", class_="program-item"):  # Ganti elemen HTML sesuai dengan halaman target
        time = item.find("div", class_="time").text.strip()
        title = item.find("div", class_="title").text.strip()
        description = item.find("div", class_="description").text.strip()
        programs.append({
            "time": time,
            "title": title,
            "description": description
        })
    
    return programs

# Fungsi untuk mengonversi ke format XMLTV
def convert_to_xmltv(programs, output_file="epg.xml"):
    tv = ET.Element("tv")
    for program in programs:
        channel = ET.SubElement(tv, "programme", start=program["time"])
        title = ET.SubElement(channel, "title")
        title.text = program["title"]
        desc = ET.SubElement(channel, "desc")
        desc.text = program["description"]
    
    tree = ET.ElementTree(tv)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"EPG berhasil disimpan ke {output_file}")

# Main program
if __name__ == "__main__":
    print("Mengambil data EPG...")
    epg_data = fetch_epg()
    if epg_data:
        print(f"{len(epg_data)} program ditemukan.")
        convert_to_xmltv(epg_data)
    else:
        print("Tidak ada data yang ditemukan.")
