from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import lxml
import datetime
import logging.config
from os import path


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logger_conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

app = Flask(__name__)


@app.route('/')
def index():

    start = datetime.datetime.now()
    source = requests.get("https://www.imdb.com/name/nm0005363/?ref_=fn_al_nm_1")
    app.logger.info(f'{datetime.datetime.now() - start} getting the main request')

    start = datetime.datetime.now()
    soup = BeautifulSoup(source.text, 'lxml')
    app.logger.info(f'{datetime.datetime.now() - start} getting the main page soup')

    base_url = 'https://www.imdb.com/'

    role = 'director'
    movies_soup = soup.select(f'div[id*="{role}"]')
    movie_list = []
    for movie in movies_soup:
        title = movie.a.text
        if title.lower() == role:
            pass
        else:
            movie_dict = dict()
            movie_dict['title'] = title
            movie_dict['link'] = movie.a.get('href')

            if movie_dict['link'] is not None:
                full_url = urljoin(base_url, movie_dict['link'])

                start = datetime.datetime.now()
                movie_source = requests.get(full_url)
                app.logger.info(f'{datetime.datetime.now() - start} getting the request')

                start = datetime.datetime.now()
                movie_soup = BeautifulSoup(movie_source.text, 'lxml')
                app.logger.info(f'{datetime.datetime.now() - start} getting the soup')

                try:
                    movie_dict['rating'] = movie_soup.select('div.ratingValue span')[0].text
                except IndexError:
                    pass
                try:
                    movie_dict['budget'] = movie_soup.select('#titleDetails > div:nth-child(12)')[0].text.split()[0].split(':')[1]
                except IndexError:
                    pass

            movie_list.append(movie_dict)

    return render_template("index.html", movie_list=movie_list)
