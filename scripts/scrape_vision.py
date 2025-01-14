import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import xml.etree.ElementTree as ET

BASE_URL = "https://www.mncvision.id/schedule/table"
TIMEZONE = "Asia/Jakarta"

def get_channels():
    url = "https://www.mncvision.id/schedule"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    channels = []
    options = soup.select('select[name="fchannel"] option')
    for option in options:
        site_id = option.get("value")
        name = option.text.split(" - ")[0].strip()
        if site_id:
            channels.append({"site_id": site_id, "name": name})
    return channels

def get_epg(channel_id, date):
    form_data = {
        "search_model": "channel",
        "af0rmelement": "aformelement",
        "fdate": date.strftime("%Y-%m-%d"),
        "fchannel": channel_id,
        "submit": "Search"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(BASE_URL, data=form_data, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select('tr[valign="top"]')
    
    programs = []
    for item in items:
        start = parse_start(item, date)
        duration = parse_duration(item)
        stop = start + timedelta(minutes=duration)
        programs.append({
            "title": parse_title(item),
            "description": parse_description(item),
            "start": start,
            "stop": stop
        })
    return programs

def parse_start(item, date):
    time_str = item.select_one('td:nth-child(1)').text.strip()
    datetime_str = f"{date.strftime('%d/%m/%Y')} {time_str}"
    local_tz = pytz.timezone(TIMEZONE)
    start_time = local_tz.localize(datetime.strptime(datetime_str, "%d/%m/%Y %H:%M"))
    return start_time

def parse_duration(item):
    duration_text = item.select_one('td:nth-child(3)').text.strip()
    hours, minutes = map(int, duration_text.split(":"))
    return hours * 60 + minutes

def parse_title(item):
    return item.select_one('td:nth-child(2) > a').text.strip()

def parse_description(item):
    link = item.select_one('td:nth-child(2) > a').get("href")
    if not link:
        return None
    response = requests.get(link)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    description = soup.select_one(".synopsis").text.strip()
    return description if description != "-" else None

def generate_xmltv(channels, epg_data, output_file="epg_vision.xml"):
    # Buat elemen root
    root = ET.Element("tv")
    root.set("generator-info-name", "EPG Scraper")
    root.set("generator-info-url", "https://www.mncvision.id")

    # Tambahkan saluran
    for channel in channels:
        channel_element = ET.SubElement(root, "channel", id=channel["site_id"])
        display_name = ET.SubElement(channel_element, "display-name")
        display_name.text = channel["name"]

    # Tambahkan program
    for channel_id, programs in epg_data.items():
        for program in programs:
            programme_element = ET.SubElement(
                root, "programme",
                start=program["start"].strftime("%Y%m%d%H%M%S %z"),
                stop=program["stop"].strftime("%Y%m%d%H%M%S %z"),
                channel=channel_id
            )
            title = ET.SubElement(programme_element, "title")
            title.text = program["title"]
            desc = ET.SubElement(programme_element, "desc")
            desc.text = program["description"] or "No description available"

    # Tulis file XML
    tree = ET.ElementTree(root)
    with open(output_file, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        tree.write(f, encoding="utf-8", xml_declaration=False)

if __name__ == "__main__":
    # Ambil saluran
    channels = get_channels()
    print("Fetching channels and EPG data...")
    
    # Ambil EPG untuk setiap saluran untuk hari ini
    today = datetime.now(pytz.timezone(TIMEZONE)).date()
    epg_data = {}
    for channel in channels[:5]:  # Ambil 5 saluran pertama (bisa diubah sesuai kebutuhan)
        epg_data[channel["site_id"]] = get_epg(channel["site_id"], today)
    
    # Hasilkan file XMLTV
    generate_xmltv(channels, epg_data, output_file="epg_vision.xml")
    print("EPG saved to epg_vision.xml")
