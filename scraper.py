from turtle import title
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import base64
import re

base_url = "http://179.43.163.54/movies/"
referer_header = "http://179.43.163.54/"

def save_to_playlist(title, quality, img_src, file_link):
    with open("output_playlist.txt", "a", encoding="utf-8") as f:
        f.write(f"#KODIPROP:inputstream.adaptive.stream_headers=Referer=http://172.96.161.72/\n")
        f.write(f"#EXTINF:-1 type=\"movie\" group-title=\"Rebahin\" tvg-logo=\"{img_src}\",{title} {quality}\n{file_link}\n\n")

def get_movies_data(page_num):
    try:
        url = urljoin(base_url, f"page/{page_num}")
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all movie items
            movie_items = soup.find_all('div', class_='ml-item')

            for movie_item in movie_items:
                title = movie_item.find('h2').text.strip()
                quality = movie_item.find('span', class_='mli-quality').text.strip()
                href = movie_item.find('a')['href'].strip()
                img_src = movie_item.find('img')['src'].strip()

                # Construct the "play" path based on the href
                play_path = urljoin(base_url, href) + "play/"

                # Make a second request for the "play" path
                play_response = requests.get(play_path)
                if play_response.status_code == 200:
                    # Extract the value of "data-iframe" from the first server
                    soup_play = BeautifulSoup(play_response.text, 'html.parser')
                    first_server = soup_play.find('div', class_='server server-active')
                    data_iframe_value = first_server.get('data-iframe', '')

                    # Decode base64
                    decoded_url = base64.b64decode(data_iframe_value).decode('utf-8')

                    # Make a third request using the decoded URL and Referer header
                    headers = {'Referer': referer_header}
                    third_response = requests.get(decoded_url, headers=headers)
                    if third_response.status_code == 200:
                        # Parse the content of the third response to extract the "file" link
                        match = re.search(r'"file":\s*"(.*?)"', third_response.text)
                        if match:
                            file_link = match.group(1)
                            save_to_playlist(title, quality, img_src, file_link)
                            print(f"Added: {title}")
                        else:
                            print("File link not found in the response.")

                else:
                    print(f"Error making second request: {play_response.status_code} - {play_response.text}")

        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    for page_num in range(1, 591):
        print(f"Scraping page {page_num}")
        get_movies_data(page_num)
