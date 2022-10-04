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

#function to collect the satellite data and produce a yearly country specific average NDVI value
def ndvi_collection(country, year):
    location = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0"
    ).filter(ee.Filter.eq("ADM0_CODE", country))
    dataset = ee.ImageCollection("NASA/GIMMS/3GV0"
    ).select("ndvi").filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def set_property(image):
        dict = image.reduceRegion(ee.Reducer.mean(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(set_property)
    aggregate_pixel_values = (pixel_values.aggregate_array("ndvi").getInfo())
    mean_pixel_value = np.mean(aggregate_pixel_values)

    return mean_pixel_value

#taking the time it takes to iterate through all the countries
print("Starting data collection...")
time_begin = time.time()

#importing the dataset created in "ee_country_check.py" and transforming the GAUL column to a list
ee_collection = pd.read_csv(path + r"\ee_collection_dataset.csv")
countries = ee_collection["GAUL"].tolist()

#creating empty lists to store the values of the loop below
ndvi_values = []
country_index = []
time_index = []

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
print("Data collection finished, it took " + str(round((time_end - time_begin) / 60)) + " minutes.")

#creating a dataframe containing the results
df_ndvi = pd.DataFrame()
df_ndvi["GAUL"] = country_index
df_ndvi["Year"] = time_index
df_ndvi["NDVI"] = ndvi_values

#saving the results
df_ndvi.to_csv(path + (r"\ndvi_data.csv"))

print("Results saved locally, path:")
print(path)