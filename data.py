import re


def data_from_movie_page(movie_soup):

    movie_dict = {}

    # get box office info:
    # keys: key names for movie_dict
    # values: text to be searched for to scrap box office info
    box_office_to_scrap = {'budget': 'Budget:',
                           'opening_weekend_USA': 'Opening Weekend USA:',
                           'gross_USA': 'Gross USA:',
                           'cumulative_world_gross': 'Cumulative Worldwide Gross'}

    for key, value in box_office_to_scrap.items():
        try:
            movie_dict[key] = movie_soup.find('h4', string=value).next_sibling.strip()
        except AttributeError:
            pass

    # remaining items:
    try:
        movie_dict['rating'] = movie_soup.select('div.ratingValue span')[0].text
    except IndexError:
        pass

    try:
        movie_dict['runtime'] = movie_soup.find('h4', string='Runtime:').find_next_sibling.text
    except AttributeError:
        pass

    try:
        movie_dict['genres'] = [
            i.text.strip() for i in movie_soup.find('h4', string="Genres:").find_next_siblings() if i.text.strip() != '|'
        ]
    except AttributeError:
        pass

    return movie_dict
