import altair as alt
import pandas as pd
from os import path


def data_prep_viz(movie_list):
    df = pd.DataFrame(movie_list)

    if df.year[df['year'].apply(len) > 4].any():
        df['year'] = df['year'].apply(lambda x: x[:4])  # TODO: do something better with date ranges, e.g. 2012-2014
    df['year'] = pd.to_numeric(df['year'])
    df['rating'] = pd.to_numeric(df['rating'])

    # capitalized columns for charting, non-capitalized for tooltip display (including ccy)
    for i in ['budget', 'opening_weekend_USA', 'gross_USA', 'cumulative_world_gross']:
        # df[i + '_ccy'] = df[i].str.extract(r'(^\D+)', expand=False)
        try:
            df[i[0].upper() + i[1:]] = pd.to_numeric(df[i].str.replace(r'\D+', ''))
        except KeyError:
            pass
    df.to_csv("data_after_prep.csv")
    return df


def budget_ccy_info(df_after_prep):
    """

    :param df_after_prep:
    :return: e.g. {'main_budget_ccy': '$', 'AUD': ['Gallipoli']}; None if no budget values/ccy
    """

    budget_ccy_serie = df_after_prep['budget'].str.extract(r'(^\D+)', expand=False).dropna()
    ccy_info_dict = dict()

    if len(budget_ccy_serie.unique()) == 0:
        ccy_info_dict = None

    elif len(budget_ccy_serie.unique()) == 1:
        ccy_info_dict['main_budget_ccy'] = budget_ccy_serie.unique()[0]

    else:
        all_ccy = budget_ccy_serie.value_counts()
        ccy_info_dict['main_budget_ccy'] = all_ccy.index[0]
        other_ccy_dict_tmp = dict()

        for i in all_ccy.index[1:]:
            other_ccy_dict_tmp[i] = ('; ').join(df_after_prep.title[budget_ccy_serie[budget_ccy_serie == i].index].values)

        ccy_info_dict.update(other_ccy_dict_tmp)

    return ccy_info_dict


def make_first_chart(df):
    columns = ['rating', 'Budget',
               'Opening_weekend_USA', 'Gross_USA', 'Cumulative_world_gross']
    # to get only available columns
    columns = list(set(columns) & set(df.columns))

    select_box = alt.binding_select(options=columns, name='column')
    sel = alt.selection_single(fields=['column'], bind=select_box)  # , init={'column': 'Budget'})

    chart = alt.Chart(df).transform_fold(
        columns,
        as_=['column', 'value']
    ).transform_filter(
        sel
    ).mark_bar().encode(
        alt.X(field='title', type='nominal', sort=alt.EncodingSortField(field='year')),
        alt.Y(field='value', type='quantitative'),
        tooltip=['year', 'genres', 'add_info'] + [i[0].lower() + i[1:] for i in columns],
    ).add_selection(
        sel
    )

    chart_location = path.join(path.dirname(path.abspath(__file__)), 'templates/charts/chart1.html')

    return chart.save(chart_location)
