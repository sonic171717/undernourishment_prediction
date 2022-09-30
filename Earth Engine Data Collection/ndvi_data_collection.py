#import of necessary libraries
import ee
import time
import numpy as np
import pandas as pd

#activate google earth engine API
ee.Authenticate()
ee.Initialize()

#create empty lists to store our values
ndvi_values = []
country_index = []
time_index = []

#function to collect the satellite data and produce a yearly country specific average NDVI value
def ndvi_collection(country, year):
    location = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0").filter(ee.Filter.eq("ADM0_NAME", str(country)))
    dataset = ee.ImageCollection("NOAA/CDR/AVHRR/NDVI/V5").select("NDVI").filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def set_property(image):
        dict = image.reduceRegion(ee.Reducer.mean(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(set_property)
    aggregate_pixel_values = (pixel_values.aggregate_array("NDVI").getInfo())
    mean_pixel_value = np.mean(aggregate_pixel_values)

    return mean_pixel_value

#importing the "base" dataset to create a list of the included countries
ee_collection = pd.read_csv("ee_collection_dataset.csv")
countries = ee_collection["Area"].tolist()
print(countries)

#taking the time it takes to iterate through all the countries
print("Data Collection Started")
time_begin = time.time()

#iterating through years and countries to get each NDVI value
i = 0
while i < len(countries):
    year = 2001
    while year <= 2020:
        result = ndvi_collection(country = countries[i], year = year)
        ndvi_values.append(result)
        country_index.append(countries[i])
        time_index.append(year)
        year += 1
    i += 1

#timing again
time_end = time.time()
print("Data collection finished, it took " + str(time_end - time_begin) + " seconds.")

#saving the results to a dataframe which can later be merged with the "base" dataframe
df_ndvi = pd.DataFrame()
df_ndvi["Area"] = country_index
df_ndvi["Year"] = time_index
df_ndvi["NDVI"] = ndvi_values
df_ndvi.to_csv("ndvi_data.csv")