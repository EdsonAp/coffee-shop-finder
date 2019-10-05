#search for business url -- https://api.yelp.com/v3/businesses/search

#Import modules requests and Api Key
from flask import Flask
import requests
from yelp_api import apiKey

# Define API key, endpoint and headers
api_key = apiKey
end_point = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'bearer %s' %api_key}

# Define parameters for search request 
parameters = {
        'term' : 'coffee',
        'location' : 'Keller' ,
        'radius':10000,
        'limit': 10 }

# Make request to the Yelp Api
response = requests.get(url = end_point, params = parameters , headers = headers) 

#convert JSON to Dictionary
data_results = response.json()

print(data_results)
# print(data_results.keys())

# def api_results():
#         for biness in data_results['businesses']:
#             print(biness['name'])
#             print(biness['rating'])
#             print(biness['phone'])

# api_results()