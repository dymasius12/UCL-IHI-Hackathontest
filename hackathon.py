import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import altair as alt
import sys
st.set_option('deprecation.showPyplotGlobalUse', False)
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../plotly/plotly')
def add_US(df):
    USA = df.groupby('Year',as_index= False).mean()
    USA['State Name'] = 'All States'
    df = pd.concat([USA,df])
    df = df.set_index(['State Name','Year'])
    return df

df = pd.read_csv("combined.csv")
state_names = df['State Name'].unique()
df = add_US(df)

future_df = pd.read_csv("future.csv")
future_df = add_US(future_df)

coords = pd.read_csv('coords.csv')
diseases = ['Asbestosis', 'Asthma',
       'Chronic obstructive pulmonary disease', 'Chronic respiratory diseases',
       'Coal workers pneumoconiosis',
       'Interstitial lung disease and pulmonary sarcoidosis',
       'Other chronic respiratory diseases', 'Other pneumoconiosis',
       'Pneumoconiosis', 'Silicosis']

pollution =['Carbon monoxide',
       'Nitrogen dioxide (NO2)', 'Outdoor Temperature', 'Ozone',
       'PM10 Total 0-10um STP', 'Sulfur dioxide']


st.title("Respiratory illness and Air Quality in the US from 1980 to 2020")
st.write("Here is the entire data set that we're using :sunglasses: On the left, you can select a specific state.")



#### line graph plots #########

state_option = st.sidebar.selectbox("Which state do you want to look at?",
                            df.reset_index()["State Name"].unique())

resp_illness = st.selectbox("Which illness do you want to focus on?", diseases )

air_quality = st.selectbox("Which air quality metric do you want to compare against?", pollution)

st.write("COMPARISON")
corr_df = df.loc[state_option][[resp_illness, air_quality]]

corr_df  = corr_df.set_index(resp_illness)
st.line_chart(corr_df)

##########  bar chart for the disease in a given year
st.write("YEARLY")
min_year = df.reset_index().Year.min()
max_year = df.reset_index().Year.max()
year = st.slider('What year?', min_year , max_year)
# bar_df = pd.DataFrame(df.loc[state_option,year][diseases].values.reshape(1,-1), columns = diseases,index = ['Rate'])
# st.bar_chart(bar_df)

bar_df = pd.DataFrame()
bar_df['Rate'] = df.loc[state_option,year][diseases].values
bar_df['Respiratory Disease'] = diseases
bar_df = bar_df.set_index('Respiratory Disease')
st.bar_chart(bar_df)


#### future line graph plots #########
st.write("FORECASTING")
air_quality_option = st.multiselect("Which air quality metric do you want to compare against?", pollution + ['Chronic respiratory diseases'],default=['Chronic respiratory diseases'])

line_df = future_df.loc[state_option][air_quality_option ]
line_df.index = pd.to_datetime(line_df.index, format="%Y")
st.line_chart(line_df)



import geopandas as gpd
import geoplot
import pandas as pd


usa = gpd.read_file('states.shp')
usa =  usa.rename(columns = {'STATE_NAME':'State Name'})
usa = usa[['State Name','geometry']]
map_df = df.reset_index().set_index('Year').loc[year].set_index('State Name')
map_df = df.loc[state_names].merge(usa, on = 'State Name')
gdf = gpd.GeoDataFrame(map_df, geometry='geometry')
gdf.plot('Asthma')
st.pyplot()


# import altair as alt
# from vega_datasets import data
#
# import pandas as pd
# import altair as alt
# from vega_datasets import data
# states = alt.topo_feature(data.us_10m.url, feature='states')
# states
#
# #unemp_data = pd.read_csv('http://vega.github.io/vega-datasets/data/unemployment.tsv',sep='\t')
# #unemp_data = unemp_data.head(50)
# # df = df.reset_index()
# # unemp_data = df.loc[df['State Name'] == state_names]
# #unemp_data['rate'] = df['Ozone'].values
# # US states background
# coords = pd.read_csv('coords.csv')
# coords.to_json('coords.json')
# states = alt.topo_feature(data.us_10m.url, 'states')
# states
# capitals = data.us_state_capitals.url
# capitals
# # US states background
# background = alt.Chart(states).mark_geoshape(
#     fill='lightgray',
#     stroke='white'
# ).properties(
#     title='US State Capitols',
#     width=650,
#     height=400
# ).project('albersUsa')
#
# # Points and text
# hover = alt.selection(type='single', on='mouseover', nearest=True,
#                       fields=['lat', 'lon'])
#
# base = alt.Chart(coords).encode(
#     longitude='lon:Q',
#     latitude='lat:Q',
# )
#
# text = base.mark_text(dy=-5, align='right').encode(
#     alt.Text('city', type='nominal'),
#     opacity=alt.condition(~hover, alt.value(0), alt.value(1))
# )
#
# points = base.mark_point().encode(
#     color=alt.value('black'),
#     size=alt.condition(~hover, alt.value(30), alt.value(100))
# ).add_selection(hover)
#
# background + points + text
# # .transform_lookup(
# #     lookup='id',
# #     from_=alt.LookupData(unemp_data, 'State Name', ['Asthma'])
# # ).project(
# #     type='albersUsa'
# # ).properties(
# #     width=500,
# #     height=300,
# #     title='Unemployment by County')
# # chart


# from plotly.figure_factory._county_choropleth import create_choropleth
# import pandas as pd
#
# NE_states = ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']
# df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/minoritymajority.csv')
# df_sample_r = df_sample[df_sample['STNAME'].isin(NE_states)]
#
#
# values = df_sample_r['TOT_POP'].tolist()
# fips = df_sample_r['FIPS'].tolist()
#
# colorscale = [
#     'rgb(68.0, 1.0, 84.0)',
#     'rgb(66.0, 64.0, 134.0)',
#     'rgb(38.0, 130.0, 142.0)',
#     'rgb(63.0, 188.0, 115.0)',
#     'rgb(216.0, 226.0, 25.0)'
# ]
#
# fig = create_choropleth(
#     fips=fips, values=values,
#     scope=NE_states, county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
#     legend_title='Population per county'
#
# )
# fig.update_layout(
#     legend_x = 0,
#     annotations = {'x': -0.12, 'xanchor': 'left'}
# )
#
# fig.layout.template = None
# fig.show()
