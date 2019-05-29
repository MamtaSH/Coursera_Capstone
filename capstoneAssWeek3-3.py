#!/usr/bin/env python
# coding: utf-8

# In[2]:


# importing old libraries
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup as bs


# In[3]:


# importing new libraries
import numpy as np # library to handle data
import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# !conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests

# !conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# "Load the pandas dataframe"

# In[5]:


wikipedia_link='https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
raw_wikipedia_page= requests.get(wikipedia_link).text

soup = BeautifulSoup(raw_wikipedia_page,'lxml')


# In[6]:


# extracting the table inside that webpage
table = soup.find('table')

Postcode      = []
Borough       = []
Neighbourhood = []

# extracting a clean form of the table
for tr_cell in table.find_all('tr'):
    
    counter = 1
    Postcode_var      = -1
    Borough_var       = -1
    Neighbourhood_var = -1
    
    for td_cell in tr_cell.find_all('td'):
        if counter == 1: 
            Postcode_var = td_cell.text
        if counter == 2: 
            Borough_var = td_cell.text
            tag_a_Borough = td_cell.find('a')
            
        if counter == 3: 
            Neighbourhood_var = str(td_cell.text).strip()
            tag_a_Neighbourhood = td_cell.find('a')
            
        counter +=1
        
    if (Postcode_var == 'Not assigned' or Borough_var == 'Not assigned' or Neighbourhood_var == 'Not assigned'): 
        continue
    try:
        if ((tag_a_Borough is None) or (tag_a_Neighbourhood is None)):
            continue
    except:
        pass
    if(Postcode_var == -1 or Borough_var == -1 or Neighbourhood_var == -1):
        continue
        
    Postcode.append(Postcode_var)
    Borough.append(Borough_var)
    Neighbourhood.append(Neighbourhood_var)


# In[7]:


unique_p = set(Postcode)
# print('num of unique Postal codes:', len(unique_p))
Postcode_u      = []
Borough_u       = []
Neighbourhood_u = []


for postcode_unique_element in unique_p:
    p_var = ''; b_var = ''; n_var = ''; 
    for postcode_idx, postcode_element in enumerate(Postcode):
        if postcode_unique_element == postcode_element:
            p_var = postcode_element;
            b_var = Borough[postcode_idx]
            if n_var == '': 
                n_var = Neighbourhood[postcode_idx]
            else:
                n_var = n_var + ', ' + Neighbourhood[postcode_idx]
    Postcode_u.append(p_var)
    Borough_u.append(b_var)
    Neighbourhood_u.append(n_var)


# In[8]:


get_ipython().system('pip install geocoder')


# In[9]:


import geocoder


# In[ ]:


latitude = []
longitude = []
for elem in Postcode_u:
# initialize your variable to None
    lat_lng_coords = None

# loop until you get the coordinates
    while (lat_lng_coords is None):
        g = geocoder.google('{}, Toronto, Ontario'.format(elem))
        lat_lng_coords = g.latlng
        # print(lat_lng_coords)

    latitude.append(lat_lng_coords[0])
    longitude.append(lat_lng_coords[1])
    print(elem, 'is RECEIVED.')
    # print(lat_lng_coords[0])
    # print(lat_lng_coords[1])


# In[ ]:


toronto_dict = {'Postcode':Postcode_u, 'Borough':Borough_u, 'Neighbourhood':Neighbourhood_u,
              'Latitude': latitude, 'Longitude':longitude}
df_toronto = pd.DataFrame.from_dict(toronto_dict)
df_toronto.to_csv('toronto_base.csv')
df_toronto.head(10)


# In[ ]:


df_toronto = pd.read_csv('toronto_base.csv')
df_toronto.head()


# "Creating a map of Toronto"

# In[ ]:


# for the city Toronto, latitude and longtitude are manually extracted via google search
toronto_latitude = 43.6532; toronto_longitude = -79.3832
map_toronto = folium.Map(location = [toronto_latitude, toronto_longitude], zoom_start = 10.7)

# add markers to map
for lat, lng, borough, neighborhood in zip(df_toronto['Latitude'], df_toronto['Longitude'], df_toronto['Borough'], df_toronto['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7).add_to(map_toronto)  
    

map_toronto


# Create a new data frame with neighborhoods in Scarborough

# In[ ]:


CLIENT_ID = '0MJA3NYYG3U2ZY1LTZN2OYEHS3Y3WVSON2GBSO3IL4EDYVIR' # your Foursquare ID
CLIENT_SECRET = 'WGWSAF2TKVUQPE3PD0N3EOITFVBY5EYP1VCZI3BMUG0ROUS5' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version


# In[ ]:


scarborough_data = df_toronto[df_toronto['Borough'] == 'Scarborough'].reset_index(drop=True)
scarborough_data.head()


# Create a map of Scarborough and its neighbourhoods

# In[ ]:


address_scar = 'Scarborough,Toronto'
latitude_scar = 43.773077
longitude_scar = -79.257774
print('The geograpical coordinate of Scarborough are {}, {}.'.format(latitude_scar, longitude_scar))


# In[ ]:


map_scarb = folium.Map(location=[latitude_scar, longitude_scar], zoom_start=12)

# add markers to map
for lat, lng, label in zip(scarborough_data['Latitude'], scarborough_data['Longitude'], scarborough_data['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7).add_to(map_scarb)  
    
map_scarb


# Get the top 100 venues in the neighborhood 'Steeles West', from Scarborough

# In[ ]:


neighborhood_latitude = scarborough_data.loc[0, 'Latitude'] # neighbourhood latitude value
neighborhood_longitude = scarborough_data.loc[0, 'Longitude'] # neighbourhood longitude value

neighborhood_name = scarborough_data.loc[0, 'Neighbourhood'] # neighbourhood name

print('Latitude and longitude values of "{}" are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# In[ ]:


LIMIT = 100
radius = 500
url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude_scar, longitude_scar, VERSION, radius, LIMIT)


# In[ ]:


results = requests.get(url).json()
results


# In[ ]:


def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[ ]:


import json # library to handle JSON files
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

venues = results['response']['groups'][0]['items']  
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head(10)


# In[ ]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# In[ ]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# Get venues for each neighborhood in Scarborough

# In[ ]:


scarborough_venues = getNearbyVenues(names=scarborough_data['Neighbourhood'],
                                   latitudes=scarborough_data['Latitude'],
                                   longitudes=scarborough_data['Longitude']
                                  )


# In[ ]:


scarborough_venues.head()


# In[ ]:


scarborough_venues.tail()


# In[ ]:


scarborough_venues.groupby('Neighborhood').count()


# In[ ]:


print('There are {} uniques categories.'.format(len(scarborough_venues['Venue Category'].unique())))


# In[ ]:


# one hot encoding
scarb_onehot = pd.get_dummies(scarborough_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
scarb_onehot['Neighborhood'] = scarborough_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [scarb_onehot.columns[-1]] + list(scarb_onehot.columns[:-1])
scarb_onehot = scarb_onehot[fixed_columns]

scarb_onehot.head()


# In[ ]:


scarb_onehot.shape


# In[ ]:


scarb_grouped = scarb_onehot.groupby('Neighborhood').mean().reset_index()
scarb_grouped.head(7)


# Get top 10 venues per neighborhood

# In[ ]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[ ]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = scarb_grouped['Neighborhood']

for ind in np.arange(scarb_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(scarb_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted


# Run k-means to cluster the neighborhoods into 5 clusters

# In[ ]:


# import k-means from clustering stage
from sklearn.cluster import KMeans

scarb_data = scarborough_data.drop(16)
# set number of clusters
kclusters = 5

scarb_grouped_clustering = scarb_grouped.drop('Neighborhood', 1)


# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(scarb_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 
#len(kmeans.labels_)#=16
#scarborough_data.shape


# Include kmeans.labels_ into the original Scarborough dataframe

# In[ ]:


scarb_merged = scarb_data

# add clustering labels
scarb_merged['Cluster Labels'] = kmeans.labels_

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
scarb_merged = scarb_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighbourhood')

scarb_merged


# Visualize the clusters in the map

# In[ ]:


# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# create map
map_clusters = folium.Map(location = [latitude_scar, longitude_scar], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i+x+(i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(scarb_merged['Latitude'], scarb_merged['Longitude'], scarb_merged['Neighbourhood'], scarb_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# Examine each of the five clusters

# In[ ]:


scarb_merged.loc[scarb_merged['Cluster Labels'] == 0, scarb_merged.columns[[1] + list(range(5, scarb_merged.shape[1]))]]


# In[ ]:


scarb_merged.loc[scarb_merged['Cluster Labels'] == 1, scarb_merged.columns[[1] + list(range(5, scarb_merged.shape[1]))]]


# In[ ]:


scarb_merged.loc[scarb_merged['Cluster Labels'] == 2, scarb_merged.columns[[1] + list(range(5, scarb_merged.shape[1]))]]


# In[ ]:


scarb_merged.loc[scarb_merged['Cluster Labels'] == 3, scarb_merged.columns[[1] + list(range(5, scarb_merged.shape[1]))]]


# In[ ]:


scarb_merged.loc[scarb_merged['Cluster Labels'] == 4, scarb_merged.columns[[1] + list(range(5, scarb_merged.shape[1]))]]


# In[ ]:





# In[ ]:




