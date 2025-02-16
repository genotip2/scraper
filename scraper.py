import requests
import json
import base64
import re
import os
import datetime
from bs4 import BeautifulSoup

# Base URL dari situs streaming (Ganti sesuai situs target)
BASE_URL = "http://198.54.124.245"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

# Tahun otomatis (tahun ini & tahun lalu)
current_year = datetime.datetime.now().year
last_year = current_year - 1
ALLOWED_YEARS = [str(current_year), str(last_year)]

# Kata kunci yang menandakan kualitas CAM (harus dihindari)
CAM_KEYWORDS = ["CAM", "HDCAM", "TS", "Telesync"]

# Path file M3U output
M3U_FILE = "output/movies.m3u"

# Fungsi untuk membaca daftar film yang sudah ada di M3U
def load_existing_movies():
    if not os.path.exists(M3U_FILE):
        return set()  # Jika file tidak ada, kembalikan set kosong

    existing_movies = set()
    with open(M3U_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#EXTINF"):
                title = line.split(",")[-1].strip()
                existing_movies.add(title)
    return existing_movies

# Fungsi untuk mendapatkan daftar kategori dari website
def get_categories():
    url = f"{BASE_URL}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print("Error: Tidak bisa mengakses halaman utama.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    categories = []

    # Mencari kategori film di menu atau sidebar
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.text.strip()
        if "/category/" in href:
            category_name = href.split("/category/")[-1].strip("/")
            categories.append((category_name, href))

    return categories

# Fungsi untuk mendapatkan daftar film dari kategori tertentu
def get_movies_from_category(category_url, category_name, existing_movies):
    response = requests.get(category_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error: Tidak bisa mengakses {category_url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    movies = []

    for post in soup.find_all("article"):
        title_tag = post.find("h2", class_="post-title")
        link_tag = title_tag.find("a") if title_tag else None
        title = link_tag.text.strip() if link_tag else "Tidak ada judul"
        movie_url = link_tag["href"] if link_tag else None

        # Ambil informasi tambahan
        details = post.find("div", class_="post-content")
        details_text = details.text.strip() if details else ""

        # Periksa apakah film termasuk dalam tahun yang diizinkan
        if any(year in title or year in details_text for year in ALLOWED_YEARS):
            # Pastikan bukan film kualitas CAM
            if not any(cam_word.lower() in title.lower() or cam_word.lower() in details_text.lower() for cam_word in CAM_KEYWORDS):
                # Hanya tambahkan jika belum ada dalam daftar
                if title not in existing_movies:
                    movie = {
                        "title": title,
                        "url": movie_url,
                        "category": category_name,
                        "details": details_text
                    }
                    movies.append(movie)

    return movies

# Fungsi untuk mendapatkan URL streaming dari halaman film
def get_stream_url(movie_url):
    response = requests.get(movie_url, headers=HEADERS)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    iframe = soup.find("iframe")

    if iframe:
        iframe_src = iframe["src"]
        if "base64" in iframe_src:
            try:
                decoded_url = base64.b64decode(iframe_src.split(",")[1]).decode("utf-8")
                return decoded_url
            except Exception:
                return None
        return iframe_src
    return None

# Fungsi untuk menyimpan data ke file M3U
def save_to_m3u(movies):
    os.makedirs("output", exist_ok=True)  # Buat folder output jika belum ada

    mode = "a" if os.path.exists(M3U_FILE) else "w"

    with open(M3U_FILE, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("#EXTM3U\n")  # Tambahkan header jika file baru

        for movie in movies:
            if movie["stream_url"]:
                f.write(f"#EXTINF:-1 tvg-group=\"{movie['category']}\",{movie['title']}\n{movie['stream_url']}\n")

    print(f"✅ Film baru ditambahkan ke file: {M3U_FILE}")

# Fungsi utama
def main():
    print("🔍 Memuat daftar film yang sudah ada...")
    existing_movies = load_existing_movies()
    print(f"📂 {len(existing_movies)} film sudah ada dalam daftar.")

    print("🔍 Mengambil daftar kategori dari website...")
    categories = get_categories()
    if not categories:
        print("❌ Tidak ada kategori yang ditemukan.")
        return

    all_movies = []

    for category_name, category_url in categories:
        print(f"📂 Mengambil film dari kategori: {category_name}")
        movies = get_movies_from_category(category_url, category_name, existing_movies)
        if movies:
            # Ambil URL streaming untuk setiap film
            for movie in movies:
                stream_url = get_stream_url(movie["url"]) if movie["url"] else None
                movie["stream_url"] = stream_url

            all_movies.extend(movies)

    if not all_movies:
        print("❌ Tidak ada film baru yang ditemukan.")
        return

    print("💾 Menyimpan film baru ke file M3U...")
    save_to_m3u(all_movies)
    print("🎉 Selesai!")

if __name__ == "__main__":
    main()
