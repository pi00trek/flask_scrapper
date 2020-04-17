
def data_from_movie_page(movie_dict, movie_soup):

    try:
        movie_dict['rating'] = movie_soup.select('div.ratingValue span')[0].text
    except IndexError:
        pass
    try:
        movie_dict['budget'] = movie_soup.select(
            '#titleDetails > div:nth-child(12)'
        )[0].text.split()[0].split(':')[1]
    except IndexError:
        pass
    try:
        movie_dict['opening_weekend_USA'] = movie_soup.select(
            '#titleDetails > div:nth-child(13)'
        )[0].text.split("\n")[1].split(' ')[-1]
    except IndexError:
        pass
    try:
        movie_dict['gross_USA'] = movie_soup.select(
            '#titleDetails > div:nth-child(14)'
        )[0].text.strip().split(" ")[-1]
    except IndexError:
        pass
    try:
        movie_dict['cumulative_world_gross'] = movie_soup.select(
            '#titleDetails > div:nth-child(15)'
        )[0].text.strip().split(" ")[-1]
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

    return movie_dict
