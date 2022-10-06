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

#activate google earth engine API
ee.Authenticate()
ee.Initialize()

#importing the "base" dataset to create a list of the included countries
base_df = pd.read_csv(path + r"\ee_collection_dataset.csv")

countries = base_df["Area"].tolist()

time_begin = time.time()
print("Checking country sizes and complexity...")

working_countries = []
error_countries = []

for i in countries:
    location = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017"
    ).filter(ee.Filter.eq("country_na", i))
    if location.size().getInfo() > 0:
        working_countries.append(i)
    else:
        error_countries.append(i)

#function to collect the mean ndvi pixel values from the satellite per year per country
def ndvi_collection_usdos(country, year):
    location = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017"
    ).filter(ee.Filter.eq("country_na", str(country)))
    dataset = ee.ImageCollection("NOAA/CDR/AVHRR/NDVI/V5").select("NDVI"
    ).filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def setProperty(image):
        dict = image.reduceRegion(ee.Reducer.median(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(setProperty)
    aggregate_pixel_values = (pixel_values.aggregate_array("NDVI").getInfo())
    mean_pixel_value = np.mean(aggregate_pixel_values)

    return mean_pixel_value

#second function for countries that usdos doesn't recognize
def ndvi_collection_gaul(adm0, year):
    location = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0"
    ).filter(ee.Filter.eq("ADM0_CODE", adm0))
    dataset = ee.ImageCollection("NOAA/CDR/AVHRR/NDVI/V5").select("NDVI"
    ).filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def set_property(image):
        dict = image.reduceRegion(ee.Reducer.mean(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(set_property)
    aggregate_pixel_values = (pixel_values.aggregate_array("NDVI").getInfo())
    mean_pixel_value = np.mean(aggregate_pixel_values)

    return mean_pixel_value

#taking the time it takes to iterate through all the countries
time_middle_1 = time.time()
print("Countries are classified, it took " + str(round((time_middle_1 - time_begin) / 60)) + " minutes.")
print("Data Collection Started...")

#create empty lists to store our values
ndvi_values_usdos = []
country_index_usdos = []
time_index_usdos = []

#iterating through years and countries to get each ndvi value
i = 0
while i < len(working_countries):
    year = 2001
    while year <= 2005:
        result = ndvi_collection_usdos(country = working_countries[i], year = year)
        ndvi_values_usdos.append(result)
        country_index_usdos.append(working_countries[i])
        time_index_usdos.append(year)
        year += 1
    i += 1

ndvi_usdos_df = pd.DataFrame()
ndvi_usdos_df["Area"] = country_index_usdos
ndvi_usdos_df["Year"] = time_index_usdos
ndvi_usdos_df["ndvi_usdos"] = ndvi_values_usdos

time_middle_2 = time.time()
print("Usdos countries finished, it took " + str(round((time_middle_2 - time_middle_1) / 60)) + " minutes.")

#Now for the countries that the usdos dataset doesnt recognize.
error_df = pd.DataFrame()
error_df["Area"] = error_countries
error_df = error_df.merge(base_df, on="Area", how="left")

working_gaul = error_df["GAUL"].tolist()

ndvi_values_gaul = []
country_index_gaul = []
time_index_gaul = []

i = 0
while i < len(working_gaul):
    year = 2001
    while year <= 2005:
        result = ndvi_collection_gaul(adm0 = working_gaul[i], year = year)
        ndvi_values_gaul.append(result)
        country_index_gaul.append(working_gaul[i])
        time_index_gaul.append(year)
        year += 1
    i += 1

ndvi_gaul_df = pd.DataFrame()
ndvi_gaul_df["GAUL"] = country_index_gaul
ndvi_gaul_df["Year"] = time_index_gaul
ndvi_gaul_df["ndvi_gaul"] = ndvi_values_gaul

#timing again
time_end = time.time()
print("Gaul countries finished, it took " + str(round((time_end - time_middle_2) / 60)) + " minutes.")
print("Total time was " + str(time_end - time_begin) + " seconds.")

#saving the results to a dataframe which can later be merged with the "base" dataframe
index_df = pd.read_csv(path + r"\country_time_base.csv")

ndvi_df = index_df.merge(ndvi_usdos_df, on=["Area", "Year"], how="left"
).merge(ndvi_gaul_df, on=["GAUL", "Year"], how="left")

ndvi_df["NDVI"] = ndvi_df["ndvi_usdos"
].fillna(ndvi_df["ndvi_gaul"])
ndvi_df = ndvi_df.drop(columns=["Unnamed: 0", "ndvi_usdos", "ndvi_gaul"])

ndvi_df.to_csv(path + r"\ndvi_data.csv")

print("Results locally, path:")
print(path + r"\ndvi_data.csv")