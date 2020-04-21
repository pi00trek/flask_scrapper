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

    # capitalized columns for charting, non-capitalized for tooltip display (including ccy)
    for i in ['budget', 'opening_weekend_USA', 'gross_USA', 'cumulative_world_gross']:
        # df[i + '_ccy'] = df[i].str.extract(r'(^\D+)', expand=False)
        df[i[0].upper() + i[1:]] = pd.to_numeric(df[i].str.replace(r'\D+', ''))
    df.to_csv("data_after_prep.csv")
    return df


def make_first_chart(df):

    # chart = alt.Chart(df).mark_bar(size=30).encode(
    #     alt.X(field='title', type='nominal', sort=alt.EncodingSortField(field='year')),
    #     y='rating',
    #     tooltip=['year', 'genres'],
    # ).properties(
    #     width=600,
    #     height=400
    # ).interactive()

    columns = ['rating', 'Budget',
               'Opening_weekend_USA', 'Gross_USA', 'Cumulative_world_gross']

    select_box = alt.binding_select(options=columns, name='column')
    sel = alt.selection_single(fields=['column'], bind=select_box, init={'column': 'Budget'})

    chart = alt.Chart(df).transform_fold(
        columns,
        as_=['column', 'value']
    ).transform_filter(
        sel
    ).mark_bar().encode(
        alt.X(field='title', type='nominal', sort=alt.EncodingSortField(field='year')),
        alt.Y(field='value', type='quantitative'),
        tooltip=['rating', 'year', 'genres', 'runtime', 'budget',
                 'opening_weekend_USA', 'gross_USA', 'cumulative_world_gross', 'add_info'],
    ).add_selection(
        sel
    )

    chart_location = path.join(path.dirname(path.abspath(__file__)), 'templates/charts/chart1.html')

    return chart.save(chart_location)
