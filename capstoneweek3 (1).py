#!/usr/bin/env python
# coding: utf-8

# In[38]:


# importing necessary libraries
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests


# In[40]:


# getting data from internet
wikipedia_link='https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
raw_wikipedia_page= requests.get(wikipedia_link).text

# using beautiful soup to parse the HTML/XML codes.
soup = BeautifulSoup(raw_wikipedia_page,'xml')
#print(soup.prettify())


# Extracting table from a WebPage

# In[41]:


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


# "Postal codes with more than 1 neighbour"

# In[42]:


unique_p = set(Postcode)
print('num of unique Postal codes:', len(unique_p))
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


# "creating an appropriate Pandas Dataframe"

# In[43]:


toronto_dict = {'Postcode':Postcode_u, 'Borough':Borough_u, 'Neighbourhood':Neighbourhood_u}
df_toronto = pd.DataFrame.from_dict(toronto_dict)
df_toronto.to_csv('toronto_part1.csv')
df_toronto.head(14)


# In[44]:


df_toronto.shape


# In[ ]:




