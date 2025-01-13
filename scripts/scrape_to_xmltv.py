from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

# Konfigurasi Selenium
service = Service("path/to/chromedriver")  # Ganti dengan path ke chromedriver Anda
driver = webdriver.Chrome(service=service)

# Buka URL target
url = "https://epg.pw/areas/id/epg.html?lang=en"
driver.get(url)

# Tunggu halaman selesai dimuat (opsional, jika ada waktu tunggu khusus)
driver.implicitly_wait(10)

# Ambil HTML setelah JavaScript selesai
html = driver.page_source
driver.quit()

# Parsing HTML dengan BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Lanjutkan parsing seperti sebelumnya
programs = []
for item in soup.find_all("div", class_="program-item"):  # Sesuaikan elemen HTML
    time = item.find("div", class_="time").text.strip()
    title = item.find("div", class_="title").text.strip()
    description = item.find("div", class_="description").text.strip()
    programs.append({"time": time, "title": title, "description": description})
