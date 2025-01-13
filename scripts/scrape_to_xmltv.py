import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# URL target
url = "https://epg.pw/areas/id/epg.html?lang=en&timezone=QXNpYS9KYWthcnRh"

# Mengambil data dari URL
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 1. Cari tanggal di elemen HTML
date_element = soup.find("div", class_="date-class")  # Sesuaikan class sesuai HTML
if date_element:
    date_str = date_element.text.strip()
    try:
        base_date = datetime.strptime(date_str, "%d %B %Y")
    except ValueError:
        print("Format tanggal tidak sesuai. Menggunakan tanggal hari ini.")
        base_date = datetime.now()
else:
    # 2. Jika tanggal tidak ada, cari di URL
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if date_match:
        year, month, day = map(int, date_match.groups())
        base_date = datetime(year, month, day)
    else:
        # 3. Jika semua gagal, gunakan tanggal hari ini
        base_date = datetime.now()

print(f"Tanggal dasar yang digunakan: {base_date.strftime('%Y-%m-%d')}")

# Parsing data program (contoh waktu program dalam tabel)
programs = []
table = soup.find("table", class_="table is-bordered is-striped")
if table:
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) > 1:
            channel_name = cells[0].text.strip()
            for cell in cells[1:]:
                time_tag = cell.find("span", class_="tag is-primary")
                title = cell.get_text(strip=True).replace(time_tag.text.strip(), "") if time_tag else ""
                time = time_tag.text.strip() if time_tag else ""

                if time and len(time) == 5:  # Format waktu HH:MM
                    time = f"{base_date.strftime('%Y-%m-%d')} {time}"

                programs.append({
                    "channel": channel_name,
                    "time": time,
                    "title": title,
                })

# Cetak hasil
for program in programs:
    print(f"Channel: {program['channel']}, Time: {program['time']}, Title: {program['title']}")
