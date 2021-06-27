import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns
import plotly.express as px
import json

from urllib.request import urlopen
import json
sns.set_style("whitegrid")
sns.set_palette("husl")
st.set_option('deprecation.showPyplotGlobalUse', False)
# insert at 1, 0 is the script path (or '' in REPL)
def add_US(df):
    USA = df.groupby('Year',as_index= False).mean()
    USA['State Name'] = 'All States'
    df = pd.concat([USA,df])
    df = df.set_index(['State Name','Year'])
    return df

def space():
    st.write("")
    st.write("")
    st.write("")
    st.write("")


df = pd.read_csv("combined.csv")
state_names = df['State Name'].unique()
df = add_US(df)

future_df = pd.read_csv("future.csv")
future_df = add_US(future_df)

diseases = ['Asbestosis', 'Asthma',
       'Chronic obstructive pulmonary disease', 'Chronic respiratory diseases',
       'Coal workers pneumoconiosis',
       'Interstitial lung disease and pulmonary sarcoidosis',
       'Other chronic respiratory diseases', 'Other pneumoconiosis',
       'Pneumoconiosis', 'Silicosis']

pollution =['Carbon monoxide',
       'Nitrogen dioxide (NO2)', 'Outdoor Temperature', 'Ozone',
       'PM10 Total 0-10um STP', 'Sulfur dioxide']



############ Introduction #############

st.title("US Respiratory Illness Death Rate vs Air Quality Dashboard")
st.write("Welcome! :grin:")
st.write("This interactive website visualises the affect of air quality on respiratory health using data from the US.")
st.write("<- To get started you can change which US State you want to look at on the left hand side.")

space()






#### line graph plots #########
st.write("COMPARISON")
st.write("You can compare a range of different illnesses and air quality metrics and the correlation between the two will be calculated.")

state_option = st.sidebar.selectbox("Which state do you want to look at?",df.reset_index()["State Name"].unique())
resp_illness = st.selectbox("Which illness do you want to focus on?", diseases )
air_quality = st.selectbox("Which air quality metric do you want to compare against?", pollution)

comparison_df = df.loc[state_option][[resp_illness, air_quality]]
corr_df = df.corr()
correlation = corr_df .loc[resp_illness][air_quality]

sns.lineplot(x=resp_illness, y=air_quality, data=comparison_df,legend = 'auto', label='Correlation = {:.2f}'.format(correlation))
st.pyplot()
space()

##### correlation plot #########

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr_df , dtype=bool))
# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))
# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)
# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr_df , mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
st.pyplot()

space()

##########  bar chart for the disease in a given year
st.write("YEARLY")
st.write("You can see how respiratory illness death rate has changed over the years by sliding the time bar.")
year = st.slider('What year?', df.reset_index().Year.min(), df.reset_index().Year.max())

bar_df = pd.DataFrame()
bar_df['Death Rate'] = df.loc[state_option,year][diseases].values
bar_df['Respiratory Disease'] = diseases
plt.figure()
sns.barplot(x='Respiratory Disease', y='Death Rate', data=bar_df)
plt.xticks(rotation=90)
plt.ylim(0,60)
st.pyplot()
space()





#### future line graph plots #########
st.write("FORECASTING")
st.write("We forecasted future values using a temporal convolutional neural network that is trained on over thirty years of data to predict into 2025, the machine learning model architecture is seen below.")

image = Image.open('TCN.png')
st.image(image, caption='Sequence to sequence machine learning model used')

st.write("By selecting different metrics you can see how respiratory illness death rate and air quality will change in the future.")


air_quality_option = st.multiselect("Which future values would you like to see?", pollution + ['Chronic respiratory disease death rate'],default=['Chronic respiratory disease death rate'])
future_df = future_df.rename(columns = {'Chronic respiratory diseases':'Chronic respiratory disease death rate'})
try: ## prevents errors if there is no option selected
    line_df = future_df.loc[state_option][air_quality_option]
    line_df.index = pd.to_datetime(line_df.index, format="%Y")
    sns.lineplot(data = line_df)
    st.pyplot()
except:
    pass
space()


####### map ####
st.write("MAP")
st.write("You can see how the death rate of respiratory illnesses changes over time.")


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


code = {'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'}

map_option = st.selectbox("What would you like to map?", diseases + pollution )
map_year = st.slider('What year?', df.reset_index().Year.min(), df.reset_index().Year.max(), key="map")

map_df = df.copy().reset_index()

map_df['Code'] = map_df['State Name'].map(code)
min_val = map_df[map_option].min()
max_val = map_df[map_option].max()
map_df = map_df.loc[map_df['Year'] == map_year]
fig = px.choropleth(map_df, #
                    locations='Code', #plot based on state code
                    color=map_option, #chose a column to show values
                    color_continuous_scale='spectral_r', #color scheme
                    range_color=(min_val , max_val),
                    hover_name='State Name', #label options
                    locationmode='USA-states', #join on state
                    scope='usa' # only show US map
                   )
#fig.show()
st.plotly_chart(fig)






#
# import geopandas as gpd
# import geoplot
# import pandas as pd
#
#
# usa = gpd.read_file('states.shp')
# usa =  usa.rename(columns = {'STATE_NAME':'State Name'})
# usa = usa[['State Name','geometry']]
# map_df = df.reset_index().set_index('Year').loc[year].set_index('State Name')
# map_df = df.loc[state_names].merge(usa, on = 'State Name')
# gdf = gpd.GeoDataFrame(map_df, geometry='geometry')
# gdf.plot('Asthma')
# st.pyplot()


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
