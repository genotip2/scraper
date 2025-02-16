import os
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime

# 🔧 Konfigurasi URL situs yang dapat diubah
CONFIG = {
    "BASE_URL": "https://rebahinxxi.me/",  # Ganti jika URL berubah
    "M3U_FILE": "movies_playlist.m3u",
}

# 📆 Tentukan tahun yang diambil (tahun ini & tahun lalu)
CURRENT_YEAR = datetime.now().year
LAST_YEAR = CURRENT_YEAR - 1

# 🔄 Buat sesi dengan retry otomatis
session = requests.Session()
retries = Retry(total=5, backoff_factor=5, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))


def load_existing_movies():
    """Memuat daftar film yang sudah ada dalam file M3U."""
    existing_movies = set()
    if os.path.exists(CONFIG["M3U_FILE"]):
        with open(CONFIG["M3U_FILE"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#EXTINF"):
                    title = line.split(",")[-1].strip()
                    existing_movies.add(title)
    return existing_movies


def get_movie_list():
    """Scraping daftar film dari website."""
    url = CONFIG["BASE_URL"]
    print(f"📡 Mengambil daftar film dari {url}...")
    
    response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    movies = []
    
    # Sesuaikan dengan struktur HTML website
    for item in soup.select(".ml-item"):
        title = item.select_one(".mli-info h2").text.strip()
        
        # Ekstrak tahun dari judul, jika tidak ada anggap tahun terbaru
        try:
            year = int(title.split()[-1])
        except ValueError:
            year = CURRENT_YEAR

        link = item.select_one("a")["href"]
        category = item.select_one(".jt-info i").text.strip()  # Kategori film
        
        # ✅ Hanya ambil film dari tahun ini & tahun lalu
        if year in {CURRENT_YEAR, LAST_YEAR}:
            movies.append({"title": title, "link": link, "category": category})
    
    return movies


def save_to_m3u(movies, existing_movies):
    """Simpan daftar film ke dalam file M3U dengan kategori sebagai grup."""
    with open(CONFIG["M3U_FILE"], "a", encoding="utf-8") as f:
        for movie in movies:
            if movie["title"] not in existing_movies:
                f.write(f'#EXTINF:-1 tvg-group="{movie["category"]}",{movie["title"]}\n')
                f.write(f"{movie['link']}\n")
    print("✅ File M3U diperbarui!")


def main():
    existing_movies = load_existing_movies()
    movies = get_movie_list()
    save_to_m3u(movies, existing_movies)


if __name__ == "__main__":
    main()
