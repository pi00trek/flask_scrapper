import altair as alt
import pandas as pd
from os import path


def data_prep_viz(movie_list):
    df = pd.DataFrame(movie_list)

    if df.year[df['year'].apply(len) > 4].any():
        # TODO: do something with date ranges, e.g. 2012-2014
        pass
    df['year'] = pd.to_numeric(df['year'])
    df['rating'] = pd.to_numeric(df['rating'])

    return df


def make_first_chart(df):

    chart = alt.Chart(df).mark_bar(size=30).encode(
        alt.X(field='title', type='nominal', sort=alt.EncodingSortField(field='year')),
        y='rating',
        tooltip=['year', 'genres'],
    ).properties(
        width=600,
        height=400
    ).interactive()

    chart_location = path.join(path.dirname(path.abspath(__file__)), 'templates/charts/chart1.html')
    print(chart_location)

    return chart.save(chart_location)
