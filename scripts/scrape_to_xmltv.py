import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# URL target
url = "https://epg.pw/areas/id/epg.html?lang=en&timezone=QXNpYS9KYWthcnRh"

# Mengambil data dari URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Asumsi tanggal awal adalah tanggal hari ini
current_date = datetime.now().date()

# Parsing data dari tabel
programs = []
channels = {}  # Menyimpan informasi channel
table = soup.find("table", class_="table is-bordered is-striped")

if table:
    last_time = None  # Waktu program sebelumnya
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) > 1:  # Setiap baris memiliki beberapa kolom
            channel_name = cells[0].text.strip()
            channel_id = channel_name.replace(" ", "")  # Channel id tanpa spasi
            
            for cell in cells[1:]:
                time_tag = cell.find("span", class_="tag is-primary")
                title = cell.get_text(strip=True).replace(time_tag.text.strip(), "") if time_tag else ""
                time = time_tag.text.strip() if time_tag else ""
                
                if time:
                    # Jika waktu sudah mencakup tanggal, gunakan format "%Y-%m-%d %H:%M"
                    try:
                        # Cek apakah waktu sudah mencakup tanggal
                        if len(time.split(" ")) > 1:  # Format sudah mencakup tanggal
                            program_time = datetime.strptime(time, "%Y-%m-%d %H:%M")
                        else:  # Format hanya waktu
                            program_time = datetime.strptime(time, "%H:%M").replace(year=current_date.year, month=current_date.month, day=current_date.day)
                        
                        # Gabungkan tanggal dan waktu
                        time = program_time.strftime("%Y-%m-%d %H:%M")

                        # Deteksi perubahan hari berdasarkan waktu
                        if last_time and program_time.time() < last_time.time():
                            current_date += timedelta(days=1)
                        
                        last_time = program_time  # Perbarui waktu terakhir
                    except ValueError as e:
                        print(f"Error parsing time: {time} - {e}")
                        continue
                else:
                    # Jika waktu tidak ditemukan, asumsikan program dimulai pada waktu default
                    time = datetime.combine(current_date, datetime.min.time()).strftime("%Y-%m-%d %H:%M")

                programs.append({
                    "channel": channel_name,
                    "channel_id": channel_id,
                    "time": time,
                    "title": title,
                })
                
                # Menyimpan informasi channel jika belum ada
                if channel_id not in channels:
                    channels[channel_id] = {
                        "display_name": channel_name,
                        "icon": ""  # Tambahkan URL ikon jika ada
                    }

# Membuat struktur XMLTV
tv = ET.Element("tv")

# Membuat elemen <channel> untuk setiap channel
for channel_id, channel_info in channels.items():
    channel = ET.SubElement(tv, "channel", id=channel_id)
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_info["display_name"]
    icon = ET.SubElement(channel, "icon", src=channel_info["icon"])
    
# Membuat elemen <programme> untuk setiap program
for i, program in enumerate(programs):
    # Menggunakan format waktu yang telah diperbarui (jika perlu)
    try:
        start_time = datetime.strptime(program["time"], "%Y-%m-%d %H:%M")
        start_str = start_time.strftime("%Y%m%d%H%M%S +0000")
    except ValueError:
        start_str = f"20250112{program['time'].replace(':', '')}00 +0000"

    # Menentukan waktu stop untuk program berikutnya
    if i < len(programs) - 1:
        next_program = programs[i + 1]
        try:
            next_start_time = datetime.strptime(next_program["time"], "%Y-%m-%d %H:%M")
            stop_str = next_start_time.strftime("%Y%m%d%H%M%S +0000")
        except ValueError:
            stop_str = f"20250112{next_program['time'].replace(':', '')}00 +0000"
    else:
        # Jika ini adalah program terakhir, set waktu stop ke waktu yang sama
        stop_str = start_str

    programme = ET.SubElement(tv, "programme", start=start_str, stop=stop_str, channel=program["channel_id"])
    title = ET.SubElement(programme, "title", lang="en")
    title.text = program["title"]

# Menyimpan ke file XML dengan header XML
with open("epg.xml", "w", encoding="utf-8") as f:
    # Menulis header XML
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<tv>\n')
    
    # Menulis elemen channel
    for programme in tv:
        if programme.tag == "channel":
            channel_id = programme.attrib["id"]
            display_name = programme.find("display-name").text
            icon_src = programme.find("icon").attrib.get("src", "")
            f.write(f'  <channel id="{channel_id}">\n')
            f.write(f'    <display-name>{display_name}</display-name>\n')
            f.write(f'    <icon src="{icon_src}"/>\n')
            f.write('  </channel>\n')
        elif programme.tag == "programme":
            # Menulis elemen programme
            start = programme.attrib["start"]
            stop = programme.attrib["stop"]
            channel = programme.attrib["channel"]
            title = programme.find("title").text
            f.write(f'  <programme start="{start}" stop="{stop}" channel="{channel}">\n')
            f.write(f'    <title lang="en">{title}</title>\n')
            f.write('  </programme>\n')

    # Menutup tag <tv>
    f.write('</tv>\n')

print("EPG berhasil disimpan ke epg.xml!")
