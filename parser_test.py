from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import csv
import requests

URL = 'https://www.kinopoisk.ru/name/37859/'
FILE = 'movies.csv'

def get_html(url):
    s = Service('/Users/alexandernikiforenko/Developer/Python/Movie_parser/chromedriver/chromedriver')
    browser = webdriver.Chrome(service=s)
    SCROLL_PAUSE_TIME = 1.5
    # browser.maximize_window()
    try:
        browser.get(url=url)
        sleep(15)

        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")

        soup = BeautifulSoup(browser.page_source, 'lxml')
        while True:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                soup = BeautifulSoup(browser.page_source, 'lxml')
                break
            last_height = new_height

        return soup

    except Exception as _ex:
        print(_ex)
    finally:
        browser.close()
        browser.quit()

def get_movies(soup):
    cards = soup.select_one('div[class=infinite-scroll-component ]')
    # print(cards)

    movies = []
    for movie in cards:
        if movie.find('span', 'icons_inlineIcon__c9P3O') or str(movie.find('span', 'desktop-person-main-info_secondaryText__XD213')).lower().find('видео') != -1:
            continue
        else:
            ru_title = movie.find('span', class_='styles_mainTitle__IFQyZ')
            eng_title = movie.find('span', class_='desktop-person-main-info_secondaryText__XD213')
            rating = movie.find('span', class_='styles_kinopoiskValue__9qXjg')
            rating_count = movie.find('span', class_='styles_kinopoiskCount__2_VPQ')

            if ru_title is None:
                ru_title_text = 'Нет даннных'
            else:
                ru_title_text = ru_title.text

            if eng_title is None:
                eng_title_text = 'Нет даннных'
            else:
                eng_title_text = eng_title.text

            if rating is None:
                rating_text = 'Нет даннных'
            else:
                rating_text = rating.text

            if rating_count is None:
                continue
                rating_count_text = 'Нет даннных'
            else:
                rating_count_text = rating_count.text
                if int(rating_count_text.replace(' ', '')) < 100:
                    continue

            movies.append({
                'ru_title': ru_title_text,
                'eng_title': eng_title_text,
                'rating': rating_text,
                'rating_count': rating_count_text
            })
    return movies
    # print(movies)
    # print(len(movies))

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Название ENG', 'Оценка', 'Кол-во оценок'])
        rating_average = count = rating_sum = 0
        for item in items:
            writer.writerow([item['ru_title'], item['eng_title'], item['rating'], item['rating_count']])
            rating_sum += float(item['rating'])
            count += 1

        rating_average = rating_sum / count
        writer.writerow([f'Средний балл', rating_average])

def main():
    URL = input('Введите URL страницы Кинопоиска актера: ')
    URL = URL.strip()
    html = get_html(URL)
    movies = get_movies(html)
    save_file(movies, FILE)
    print(f'Получено {len(movies)} фильмов актера.')
    # print(movies)
    # print(len(movies))

if __name__ == "__main__":
    main()

