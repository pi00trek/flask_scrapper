from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import lxml
import datetime

app = Flask(__name__)


@app.route('/')
def index():

    source = requests.get("https://www.imdb.com/name/nm0005363/?ref_=fn_al_nm_1")
    soup = BeautifulSoup(source.text, 'lxml')
    print(f'{datetime.datetime.now()} - after the main soup')

    base_url = 'https://www.imdb.com/'

    role = 'actor'
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
                app.logger.info('%s movie ', movie)
                print(f'{datetime.datetime.now()} - before the next request and movie soup')
                movie_source = requests.get(full_url)
                movie_soup = BeautifulSoup(movie_source.text, 'lxml')
                print(f'{datetime.datetime.now()} - after the next request and movie soup')
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

