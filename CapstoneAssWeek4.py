#!/usr/bin/env python
# coding: utf-8

# In[1]:


# importing libraries
import numpy as np # library to handle data in a vectorized manner
import pandas as pd # library for data analsysis
from bs4 import BeautifulSoup
import requests # library to handle requests
import json # library to handle JSON files
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# !conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
import geopy.geocoders # convert an address into latitude and longitude values

# !conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries are imported.')


# Postal Codes in Toronto

# In[ ]:


# Loading the dataset which is about postal codes in Toronto
# This dataset was created in week 3. 
df_toronto = pd.read_csv('toronto_base.csv')
df_toronto.head()


# Create a Map of Toronto City (with its Postal Codes' Regions)

# In[ ]:


# for the city Toronto, latitude and longtitude are manually extracted via google search
toronto_latitude = 43.6932; toronto_longitude = -79.3832
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


# Focusing on the "Scarorough" Borough in Toronto (its neighborhoods)

# In[ ]:


# df_toronto['Borough'] == 'Scarborough'

# selecting only neighborhoods regarding to "Scarborough" borough.
scarborough_data = df_toronto[df_toronto['Borough'] == 'Scarborough']
scarborough_data = scarborough_data.reset_index(drop=True).drop(columns = 'Unnamed: 0')
scarborough_data.head()


# Create a Map of Scarborough and Its Neighbourhoods

# In[ ]:


address_scar = 'Scarborough, Toronto'
latitude_scar = 43.773077
longitude_scar = -79.257774
print('The geograpical coordinate of "Scarborough" are: {}, {}.'.format(latitude_scar, longitude_scar))

map_Scarborough = folium.Map(location=[latitude_scar, longitude_scar], zoom_start=11.5)

# add markers to map
for lat, lng, label in zip(scarborough_data['Latitude'], scarborough_data['Longitude'], scarborough_data['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius = 10,
        popup = label,
        color ='blue',
        fill = True,
        fill_color = '#3186cc',
        fill_opacity = 0.7).add_to(map_Scarborough)  
    
map_Scarborough


# In[ ]:


def foursquare_crawler (postal_code_list, neighborhood_list, lat_list, lng_list, LIMIT = 500, radius = 1000):
    result_ds = []
    counter = 0
    for postal_code, neighborhood, lat, lng in zip(postal_code_list, neighborhood_list, lat_list, lng_list):
         
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, CLIENT_SECRET, VERSION, 
            lat, lng, radius, LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        tmp_dict = {}
        tmp_dict['Postal Code'] = postal_code; tmp_dict['Neighborhood(s)'] = neighborhood; 
        tmp_dict['Latitude'] = lat; tmp_dict['Longitude'] = lng;
        tmp_dict['Crawling_result'] = results;
        result_ds.append(tmp_dict)
        counter += 1
        print('{}.'.format(counter))
        print('Data is Obtained, for the Postal Code {} (and Neighborhoods {}) SUCCESSFULLY.'.format(postal_code, neighborhood))
    return result_ds;


# In[ ]:


# @hiddel_cell
CLIENT_ID = '0MJA3NYYG3U2ZY1LTZN2OYEHS3Y3WVSON2GBSO3IL4EDYVIR' # your Foursquare ID
CLIENT_SECRET = 'WGWSAF2TKVUQPE3PD0N3EOITFVBY5EYP1VCZI3BMUG0ROUS5' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version


# Crawling Internet (in fact only Foursquare database) for
# 
# Venues in the Neighborhoods inside "Scarborough"

# In[ ]:


print('Crawling different neighborhoods inside "Scarborough"')
Scarborough_foursquare_dataset = foursquare_crawler(list(scarborough_data['Postcode']),
                                                   list(scarborough_data['Neighbourhood']),
                                                   list(scarborough_data['Latitude']),
                                                   list(scarborough_data['Longitude']),)


# Breakpoint:
#     
# Saving results of Foursquare, 
# so that we would not need to connect every time to Foursquare (and use our portions) .

# In[ ]:


import pickle
with open("Scarborough_foursquare_dataset.txt", "wb") as fp:   #Pickling
    pickle.dump(Scarborough_foursquare_dataset, fp)
print('Received Data from Internet is Saved to Computer.')


# In[ ]:


with open("Scarborough_foursquare_dataset.txt", "rb") as fp:   # Unpickling
    Scarborough_foursquare_dataset = pickle.load(fp)
# print(type(Scarborough_foursquare_dataset))
# Scarborough_foursquare_dataset


# Cleaning the RAW Data Received from Foursquare Database

# In[ ]:


# This function is created to connect to the saved list which is the received database. It will extract each venue 
# for every neighborhood inside the database

def get_venue_dataset(foursquare_dataset):
    result_df = pd.DataFrame(columns = ['Postal Code', 'Neighborhood', 
                                           'Neighborhood Latitude', 'Neighborhood Longitude',
                                          'Venue', 'Venue Summary', 'Venue Category', 'Distance'])
    # print(result_df)
    
    for neigh_dict in foursquare_dataset:
        postal_code = neigh_dict['Postal Code']; neigh = neigh_dict['Neighborhood(s)']
        lat = neigh_dict['Latitude']; lng = neigh_dict['Longitude']
        print('Number of Venuse in Coordination "{}" Posal Code and "{}" Negihborhood(s) is:'.format(postal_code, neigh))
        print(len(neigh_dict['Crawling_result']))
        
        for venue_dict in neigh_dict['Crawling_result']:
            summary = venue_dict['reasons']['items'][0]['summary']
            name = venue_dict['venue']['name']
            dist = venue_dict['venue']['location']['distance']
            cat =  venue_dict['venue']['categories'][0]['name']
            
            
            # print({'Postal Code': postal_code, 'Neighborhood': neigh, 
            #                   'Neighborhood Latitude': lat, 'Neighborhood Longitude':lng,
            #                   'Venue': name, 'Venue Summary': summary, 
            #                   'Venue Category': cat, 'Distance': dist})
            
            result_df = result_df.append({'Postal Code': postal_code, 'Neighborhood': neigh, 
                              'Neighborhood Latitude': lat, 'Neighborhood Longitude':lng,
                              'Venue': name, 'Venue Summary': summary, 
                              'Venue Category': cat, 'Distance': dist}, ignore_index = True)
            # print(result_df)
    
    return(result_df)


# In[ ]:


scarborough_venues = get_venue_dataset(Scarborough_foursquare_dataset)


# Showing Venues for Each Neighborhood in Scarborough

# In[ ]:


scarborough_venues.head()


# In[ ]:


scarborough_venues.tail()


# Breakpoint:
#     
# End of Processing the Retrieved Information from Foursquare
# Saving a Cleaned Version of DataFrame as the Results from Foursquare

# In[ ]:


scarborough_venues.to_csv('scarborough_venues.csv')


# Loading Data from File (Saved "Foursquare " DataFrame for Venues)

# In[ ]:


scarborough_venues = pd.read_csv('scarborough_venues.csv')


# Some Summary Information about Neighborhoods inside "Scarborough"

# In[ ]:


neigh_list = list(scarborough_venues['Neighborhood'].unique())
print('Number of Neighborhoods inside Scarborough:')
print(len(neigh_list))
print('List of Neighborhoods inside Scarborough:')
neigh_list


# Some Summary Information about Neighborhoods inside "Scarborough" Cont'd

# In[ ]:


neigh_venue_summary = scarborough_venues.groupby('Neighborhood').count()
neigh_venue_summary.drop(columns = ['Unnamed: 0']).head()


# In[ ]:


print('There are {} uniques categories.'.format(len(scarborough_venues['Venue Category'].unique())))

print('Here is the list of different categories:')
list(scarborough_venues['Venue Category'].unique())


# In[ ]:


# Just for fun and deeper understanding
print(type(scarborough_venues[['Venue Category']]))

print(type(scarborough_venues['Venue Category']))


# One-hot Encoding the "categroies" Column into Every Unique Categorical Feature.

# In[ ]:


# one hot encoding
scarborough_onehot = pd.get_dummies(data = scarborough_venues, drop_first  = False, 
                              prefix = "", prefix_sep = "", columns = ['Venue Category'])
scarborough_onehot.head()


# Manually Selecting (Subsetting) Related Features for the Groceries Contractor

# In[ ]:


# This list is created manually 
important_list_of_features = [
 
 'Neighborhood',
 'Neighborhood Latitude',
 'Neighborhood Longitude',

 'African Restaurant',
 'American Restaurant',
 'Asian Restaurant',

 
 'BBQ Joint',
 
 'Bakery',
 
 
 
 
 
 'Breakfast Spot',

 'Burger Joint',
 
 
 
 'Cajun / Creole Restaurant',
 'Cantonese Restaurant',
 'Caribbean Restaurant',
 'Chinese Restaurant',
 
 'Diner',


 'Fast Food Restaurant',
 'Filipino Restaurant',
 'Fish Market',
 'Food & Drink Shop',
 'Fried Chicken Joint',
 'Fruit & Vegetable Store',
 
 'Greek Restaurant',
 'Grocery Store',
 
 'Hakka Restaurant',
 
 'Hong Kong Restaurant',

 'Hotpot Restaurant',
 
 'Indian Restaurant',

 'Italian Restaurant',
 'Japanese Restaurant',
 'Korean Restaurant',
 'Latin American Restaurant',



 'Malay Restaurant',
 
 'Mediterranean Restaurant',
 
 'Mexican Restaurant',
 'Middle Eastern Restaurant',
 
 'Noodle House',
 
 'Pizza Place',
 
 'Restaurant',
 'Sandwich Place',
 'Seafood Restaurant',
 'Shanghai Restaurant',
 
 'Sushi Restaurant',
 'Taiwanese Restaurant',
 
 'Thai Restaurant',
 
 'Vegetarian / Vegan Restaurant',
 
 'Vietnamese Restaurant',
 'Wings Joint']


# Updating the One-hot Encoded DataFrame and
# 
# Grouping the Data by Neighborhoods

# In[ ]:


scarborough_onehot = scarborough_onehot[important_list_of_features].drop(
    columns = ['Neighborhood Latitude', 'Neighborhood Longitude']).groupby(
    'Neighborhood').sum()


scarborough_onehot.head()


# Integrating Different Restaurants and Different Joints
# 
# (Assuming Different Resaturants Use the Same Raw Groceries)
# 
# This Assumption is made for simplicity and due to not having very large dataset about neighborhoods.

# In[ ]:


feat_name_list = list(scarborough_onehot.columns)
restaurant_list = []


for counter, value in enumerate(feat_name_list):
    if value.find('Restaurant') != (-1):
        restaurant_list.append(value)
        
scarborough_onehot['Total Restaurants'] = scarborough_onehot[restaurant_list].sum(axis = 1)
scarborough_onehot = scarborough_onehot.drop(columns = restaurant_list)


feat_name_list = list(scarborough_onehot.columns)
joint_list = []


for counter, value in enumerate(feat_name_list):
    if value.find('Joint') != (-1):
        joint_list.append(value)
        
scarborough_onehot['Total Joints'] = scarborough_onehot[joint_list].sum(axis = 1)
scarborough_onehot = scarborough_onehot.drop(columns = joint_list)


# Showing the Fully-Processed DataFrame about Neighborhoods inside Scarborrough.
# 
# This Dataset is Ready for any Machine Learning Algorithm.

# In[ ]:


scarborough_onehot


# Run k-means to Cluster Neighborhoods into 5 Clusters

# In[ ]:


# import k-means from clustering stage
from sklearn.cluster import KMeans

# run k-means clustering
kmeans = KMeans(n_clusters = 5, random_state = 0).fit(scarborough_onehot)


# Showing Centers of Each Cluster

# In[ ]:


means_df = pd.DataFrame(kmeans.cluster_centers_)
means_df.columns = scarborough_onehot.columns
means_df.index = ['G1','G2','G3','G4','G5']
means_df['Total Sum'] = means_df.sum(axis = 1)
means_df.sort_values(axis = 0, by = ['Total Sum'], ascending=False)


# Result:
# 
# Best Group is G5;
# 
# Second Best Group is G1;
# 
# Third Best Group is G4;
# 
# Inserting "kmeans.labels_" into the Original Scarborough DataFrame
# 
# Finding the Corresponding Group for Each Neighborhood.

# In[ ]:


neigh_summary = pd.DataFrame([scar_ds.index, 1 + kmeans.labels_]).T
neigh_summary.columns = ['Neighborhood', 'Group']
neigh_summary


# Deducing Results:
#     
# Best Neighborhood Are...

# In[ ]:


neigh_summary[neigh_summary['Group'] == 5]


# In[ ]:


name_of_neigh = list(neigh_summary[neigh_summary['Group'] == 5]['Neighborhood'])[0]
scarborough_venues[scarborough_venues['Neighborhood'] == name_of_neigh].iloc[0,1:5].to_dict()


# Second Best Neighborhoods

# In[ ]:


neigh_summary[neigh_summary['Group'] == 1]


# Third Best Neighborhood

# In[ ]:


neigh_summary[neigh_summary['Group'] == 4]


# In[ ]:


name_of_neigh = list(neigh_summary[neigh_summary['Group'] == 4]['Neighborhood'])[0]
scarborough_venues[scarborough_venues['Neighborhood'] == name_of_neigh].iloc[0,1:5].to_dict()


# In[ ]:




