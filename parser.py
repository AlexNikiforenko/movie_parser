import requests
from bs4 import BeautifulSoup

# Kinopoisk
#URL = "https://www.kinopoisk.ru/name/37859/"
#HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36', 'accept': '*/*'}

# Kinorium
URL = 'https://ru.kinorium.com/name/138/' # DiCaprio
# URL = "https://en.kinorium.com/name/138/" # ENG DiCaprio
# URL = 'https://ru.kinorium.com/name/912449/' # Stone
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36', 'accept': '*/*'}

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    actor_name = soup.find('div', class_='person-page__title-elements-wrap').text.strip()
    actor_type = soup.select_one('span[itemprop*="jobTitle"]').text.strip()
    items = soup.select_one(f'div[data-title*="{actor_name}: {actor_type}"]').find_all('div', class_='filmList__item-content')

# СДЕЛАТЬ ГИБКИЕ УСЛОВИЯ
    movies = []
    for item in items:
        if item.find('span', class_='status-list__voice') or item.find('span', class_='status-list__short') or str(item.find('p', class_='filmList__extra-info')).find('мультфильм') != -1 or str(item.find('span', 'filmList__small-text')).find('в титрах не указана') != -1 or str(item.find('p', 'filmList__extra-info')).find('документальный') != -1:
            continue
        else:
            movies.append({
                'name': item.find('i', class_='movie-title__text').get_text(strip=True).replace('\xa0', ' '),
                'imdb_rating': item.find('li', class_='rating_imdb').find('span', class_='value').get_text(strip=True)
            })

    print(movies)
    print(len(movies))

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Error")


parse()
