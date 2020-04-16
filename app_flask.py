from flask import Flask, render_template, redirect, request, session
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import lxml
import datetime
import logging.config
from os import path
from forms import AddressForm
from flask_bootstrap import Bootstrap


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logger_conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
bootstrap = Bootstrap(app)


@app.route('/', methods=('GET', 'POST'))
def index():
    form = AddressForm()
    if form.validate_on_submit():
        session['person_url'] = request.form['person_url']

        start = datetime.datetime.now()
        url = session['person_url']
        source = requests.get(url)
        app.logger.info(f'{datetime.datetime.now() - start} getting the main request')

        start = datetime.datetime.now()
        soup = BeautifulSoup(source.text, 'lxml')
        app.logger.info(f'{datetime.datetime.now() - start} getting the main page soup')

        session['roles'] = [i.get('data-category') for i in soup.find('div', {'id': 'jumpto'}).find_all('a')]

        return redirect('/role')

    return render_template('index.html', form=form)


@app.route('/role', methods=('GET', 'POST'))
def role():
    roles = session['roles']
    return render_template('roles.html', roles=roles)


@app.route('/data')
def get_data():

    # repeated in index()
    start = datetime.datetime.now()
    # url = "https://www.imdb.com/name/nm0005363/?ref_=fn_al_nm_1"
    url = session['person_url']
    source = requests.get(url)
    app.logger.info(f'{datetime.datetime.now() - start} getting the main request')
    start = datetime.datetime.now()
    soup = BeautifulSoup(source.text, 'lxml')
    app.logger.info(f'{datetime.datetime.now() - start} getting the main page soup')

    selected_role = request.args.get('roles', '')

    movies_soup = soup.select(f'div[id*="{selected_role}"]')
    movie_list = []
    for movie in movies_soup:
        if movie.a is not None:
            title = movie.a.text
            if title.lower() == selected_role:
                pass
            else:
                movie_dict = dict()
                movie_dict['title'] = title
                movie_dict['link'] = movie.a.get('href')
                movie_dict['year'] = movie.span.text.strip()
                try:
                    movie_dict['add_info'] = movie.text.split('\n')[5]
                except IndexError:
                    pass

                if movie_dict['link'] is not None:
                    base_url = 'https://www.imdb.com/'
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

                    def get_genres(genres_list_unfilt):
                        for idx, item in enumerate(genres_list_unfilt):
                            if item[:5] == 'See A':
                                genres_list = [genre.strip() for genre in genres_list_unfilt[idx + 1:]]
                                return genres_list

                    genres_list_unfilt = [a.text for a in movie_soup.select('div.see-more.inline.canwrap a')]
                    movie_dict['genres'] = get_genres(genres_list_unfilt)

                    try:
                        movie_dict['runtime'] = int(movie_soup.select(
                        '#titleDetails > div:nth-child(23) > time')[0].text.split(' ')[0])
                    except IndexError:
                        pass

                movie_list.append(movie_dict)
    print(movie_list)

    return render_template("data.html", movie_list=movie_list)
