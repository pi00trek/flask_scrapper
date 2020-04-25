from flask import render_template, redirect, request, session, Blueprint, current_app
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import lxml
import datetime
# import logging.config
from box_office_info_app.forms import AddressForm
from box_office_info_app.data import data_from_movie_page
from box_office_info_app.charts import data_prep_viz, make_first_chart,budget_ccy_info


bp = Blueprint('bp_app', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    form = AddressForm()
    session['navbar_role_selection'] = False

    if form.validate_on_submit():
        session['person_url'] = request.form['person_url']

        start = datetime.datetime.now()
        url = session['person_url']
        source = requests.get(url)
        current_app.logger.info(f'{datetime.datetime.now() - start} getting the main request')

        start = datetime.datetime.now()
        soup = BeautifulSoup(source.text, 'lxml')
        current_app.logger.info(f'{datetime.datetime.now() - start} getting the main page soup')

        session['roles'] = [i.get('data-category') for i in soup.find('div', {'id': 'jumpto'}).find_all('a')]
        session['person'] = soup.select('h1 span', class_='itemprop')[
            0].get_text()  # Todo: redo other data extraction with get_text()

        return redirect('/role')

    return render_template('index.html', form=form)


@bp.route('/role', methods=('GET', 'POST'))
def role():
    print(session.items())
    session['navbar_role_selection'] = False
    return render_template('roles.html', roles=session['roles'], person=session['person'])


@bp.route('/data')
def get_data():
    # repeated in index()
    start = datetime.datetime.now()
    # url = "https://www.imdb.com/name/nm0005363/?ref_=fn_al_nm_1"
    url = session['person_url']
    source = requests.get(url)
    current_app.logger.info(f'{datetime.datetime.now() - start} getting the main request')
    start = datetime.datetime.now()
    soup = BeautifulSoup(source.text, 'lxml')
    current_app.logger.info(f'{datetime.datetime.now() - start} getting the main page soup')

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
                    # app.logger.info(f'{datetime.datetime.now() - start} getting the request')

                    start = datetime.datetime.now()
                    movie_soup = BeautifulSoup(movie_source.text, 'lxml')
                    # app.logger.info(f'{datetime.datetime.now() - start} getting the soup')

                    movie_dict.update(data_from_movie_page(movie_soup))

                    movie_list.append(movie_dict)

    print(movie_list)

    clean_df = data_prep_viz(movie_list)
    make_first_chart(clean_df)

    ccy_info_dict = budget_ccy_info(clean_df)
    if ccy_info_dict:
        main_budget_ccy = ccy_info_dict.pop('main_budget_ccy')
    else:
        main_budget_ccy = None

    session['navbar_role_selection'] = True

    return render_template("data.html", movie_list=movie_list, person=session['person'],
                           main_budget_ccy=main_budget_ccy, ccy_info_dict=ccy_info_dict)


@bp.route('/chart')
def charting():
    return render_template("charts/chart1.html")