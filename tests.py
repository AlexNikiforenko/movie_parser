from numpy import save
import requests
from bs4 import BeautifulSoup
import csv
import time

# Kinopoisk
#URL = "https://www.kinopoisk.ru/name/37859/"
#HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36', 'accept': '*/*'}

# Kinorium
URL = 'https://ru.kinorium.com/name/138/' # DiCaprio
# URL = "https://en.kinorium.com/name/138/" # ENG DiCaprio
# URL = 'https://ru.kinorium.com/name/912449/' # Stone
HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36', 'accept': '*/*'}
HOST = 'https://ru.kinorium.com'
FILE = 'movies.csv'

def convert_numeral(number):
    symbols = ['', 'а', 'ов']
    number = number % 100
    if number>=11 and number<=19:
        s=symbols[2]
    else:
        i = number % 10
        if i == 1:
            s = symbols[0]
        elif i in [2,3,4]:
            s = symbols[1]
        else:
            s = symbols[2]
    return s

def convert_word_to_numeral(number):
    symbols = ['', 'о']
    number = number % 100
    if number>=11 and number<=19:
        s=symbols[1]
    else:
        i = number % 10
        if i == 1:
            s = symbols[0]
        else:
            s = symbols[1]
    return s

def format_grosses(grosses):
    pass

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
                'imdb_rating': item.find('li', class_='rating_imdb').find('span', class_='value').get_text(strip=True),
                'movie_link': HOST + item.find('a', class_='filmList__item-title-link').get('href')
            })

    return movies
    print(movies)
    print(len(movies))

def get_awards(html):
    soup = BeautifulSoup(html, 'html.parser')
    awards = soup.find_all('a', class_='movieAwards__item')

    for award in awards:
        award_name = award.select_one('a.movieAwards__item span.title').text
        # wins = award.select_one('span[data-award"]')
        print(award_name)
        # print(wins)
    print(len(awards))

def parse_movie_info(items):
    info = []
    count = 1
    for item in items:
        item_url = item['movie_link']
        html = get_html(item_url).text

        soup = BeautifulSoup(html, 'html.parser')

        movie_name = soup.find('h1', class_='film-page__title-text')
        type = soup.find('a', class_='tabs-subpage__item')
        year = soup.find('span', class_='data film-page__date')
        rating_kp = soup.select_one('a.ratingsBlockKP span.value')
        rating_kp_count = soup.select_one('a.ratingsBlockKP span.count')
        rating_imdb = soup.select_one('a.ratingsBlockIMDb span.value')
        grosses = soup.find('span', 'film-page__gross-switcher-control')

        if movie_name is None:
            movie_name_text = '-'
        else:
            movie_name_text = movie_name.get_text(strip=True).replace('\xa0', ' ')

        if type is None:
            type_text = '-'
        else:
            type_text = type.get_text(strip=True)

        if year is None:
            year_text = '-'
        else:
            year_text = year.get_text(strip=True).replace('(', '').replace(')', '')

        if rating_kp_count != None:
            rating_kp_count_text = rating_kp_count.text
        else:
            rating_kp_count_text = '-'

        if rating_kp_count_text == ' ' or rating_kp_count_text == '-':
            rating_kp_count_text = '-'
        else:
            rating_kp_count_text = rating_kp_count.text.replace('\xa0', ' ')
            if int(rating_kp_count_text.replace(' ', '')) < 100:
                continue

        if rating_kp is None:
            rating_kp_text = '-'
        else:
            rating_kp_text = rating_kp.get_text(strip=True)#.replace('.', '')

        if rating_imdb is None:
            rating_imdb_text = '-'
        else:
            rating_imdb_text = rating_imdb.get_text(strip=True)#.replace('.', '')

        if grosses is None:
            grosses_text = '-'
        else:
            grosses_text = grosses.get_text(strip=True).replace('\xa0', ' ')

        info.append({
            'movie_name': movie_name_text,
            'type': type_text,
            'year': year_text,
            'rating_kp': rating_kp_text,
            # 'rating_kp_count': rating_kp_count_text
            'rating_imdb': rating_imdb_text,
            'grosses': grosses_text
        })
        print(f'Обработан{convert_word_to_numeral(count)} {count} фильм{convert_numeral(count)} из {len(items)}.')
        count += 1

    info_rev = list(reversed(info))
    print(info_rev)
    print(len(info_rev))
    return info_rev

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Проект', 'Категория', 'Год', 'КП', 'IMDB', 'Средний балл КП', 'Средний балл IMDB', 'Сборы'])
        current_rating_kp = current_rating_imdb = rating_sum_kp = rating_sum_imdb = count_kp = count_imdb = 0

        total_grosses = 0
        for item in items:
            rating_kp = item['rating_kp']
            rating_imdb = item['rating_imdb']
            grosses = item['grosses']

            if rating_kp == '—' or rating_kp == '-':
                rating_kp = 0
            else:
                rating_kp = float(rating_kp)
                count_kp += 1
            if rating_imdb == '—' or rating_imdb == '-':
                rating_imdb = 0
            else:
                rating_imdb = float(rating_imdb)
                count_imdb += 1

            rating_sum_kp += rating_kp
            rating_sum_imdb += rating_imdb

            if count_kp != 0:
                current_rating_kp = round(rating_sum_kp / count_kp, 1)
            if count_imdb != 0:
                current_rating_imdb = round(rating_sum_imdb / count_imdb, 1)

            if grosses == '—' or grosses == '-':
                total_grosses += 0
            else:
                total_grosses += int(grosses.replace('$', '').replace(' ', ''))


            writer.writerow([item['movie_name'], item['type'], item['year'], item['rating_kp'], item['rating_imdb'], current_rating_kp, current_rating_imdb, item['grosses']])


        writer.writerow([''])
        writer.writerow([f'Средний балл КП: ', current_rating_kp])
        writer.writerow([f'Средний балл IMDB: ', current_rating_imdb])
        writer.writerow([f'Общие сборы за карьеру: ', total_grosses])


def parse():
    start_time = time.time()
    html = get_html(URL)
    if html.status_code == 200:
        movies = get_content(html.text)
        movies_info = parse_movie_info(movies)
        get_awards(html.text)
        save_file(movies_info, FILE)
    else:
        print("Error")

    print(f'{(time.time() - start_time)*1000} миллисекунд')


parse()
