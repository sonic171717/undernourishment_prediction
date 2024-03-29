"""
Description

This program retrieves country- and year-specific sums
of the precipitation using the list of working geographies
(create_ee_country_check.py).
"""

#import of necessary libraries
import ee
import time
import numpy as np
import pandas as pd

#path to import and export data (paste your own file location here)
path = (r"C:\Users\nmart\OneDrive - fs-students.de\Dokumente"
r"\Office\FS\S1\Data Analytics in Business\code_daib"
r"\Analysing-crop-yields-and-predicting-food-sustainability-of-nations-in-near-future"
r"\Earth Engine Data Collection")

#connecting to google earth engine
ee.Authenticate()
ee.Initialize()

def rain_collection(country, year):
    """
    Collect the satellite data and produce a yearly country specific total precipitation value.

    :param country: Current Country GAUL code
    :param year: Current Year

    :return float: mean pixel value of given year and country
    """

    location = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0"
    ).filter(ee.Filter.eq("ADM0_CODE", country))
    dataset = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY"
    ).select("total_precipitation").filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def set_property(image):
        dict = image.reduceRegion(ee.Reducer.sum(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(set_property)
    aggregate_pixel_values = (pixel_values.aggregate_array("total_precipitation").getInfo())
    mean_pixel_value = np.sum(aggregate_pixel_values)

    return mean_pixel_value

#taking the time it takes to iterate through all the countries
print("Starting data collection...")
time_begin = time.time()

#importing the dataset created in "ee_country_check.py" and transforming the GAUL column to a list
ee_collection = pd.read_csv(path + r"\ee_collection_dataset.csv")
countries = ee_collection["GAUL"].tolist()

#creating empty lists to store the values of the loop below
rain_values = []
country_index = []
time_index = []

#iterating through years and countries to get each rain value
i = 0
while i < len(countries):
    year = 2001
    while year <= 2020:
        result = rain_collection(country = countries[i], year = year)
        rain_values.append(result)
        country_index.append(countries[i])
        time_index.append(year)
        year += 1
    i += 1

#timing again
time_end = time.time()
print("Data collection finished, it took " + str(round((time_end - time_begin) / 60)) + " minutes.")

#creating a dataframe containing the results
df_rain = pd.DataFrame()
df_rain["GAUL"] = country_index
df_rain["Year"] = time_index
df_rain["Precipitation"] = rain_values

#saving the results
df_rain.to_csv(path + (r"\rain_data.csv"))

print("Results saved locally, path:")
print(path)
