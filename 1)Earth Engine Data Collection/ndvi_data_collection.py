#import of necessary libraries
import ee
import time
import numpy as np
import pandas as pd

#path to import and export data (paste your own file location here)
path = (r"C:\Users\nmart\OneDrive - fs-students.de\Dokumente\Office\FS"
r"\S1\Data Analytics in Business\code_daib\undernourishment_prediction\data")

#activate google earth engine API
ee.Authenticate()
ee.Initialize()

#importing the "base" dataset and creating a list of the included countries
base_df = pd.read_csv(path + r"\ee_collection_dataset.csv")
countries = base_df["Area"].tolist()

time_begin = time.time()
print("Checking country names...")

#checking if the countries are recognized by the USDOS countries feature set
working_countries = []
error_countries = []

for i in countries:
    location = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017"
    ).filter(ee.Filter.eq("country_na", i))
    if location.size().getInfo() > 0:
        working_countries.append(i)
    else:
        error_countries.append(i)

def ndvi_collection_usdos(country, year):
    """
    Collect the mean ndvi pixel values from the satellite per year per country.
    ndvi is more granular than Temperature and Precipitation. The USDOS
    country filter is less precise and works with more complex geometries.
    Only countries that are not recognized here (by name) get processed with 
    their GAUL-Code in the other function below.

    :param country: Current Country Name
    :param year: Current Year

    :return float: mean pixel value of given year and country
    """

    location = ee.FeatureCollection("USDOS/LSIB_SIMPLE/2017"
    ).filter(ee.Filter.eq("country_na", str(country)))
    dataset = ee.ImageCollection("NOAA/CDR/AVHRR/NDVI/V5").select("NDVI"
    ).filterDate(str(year)+"-01-01", str(year+1)+"-01-01")
    
    def setProperty(image):
        dict = image.reduceRegion(ee.Reducer.mean(), location, bestEffort=True)
        return image.set(dict)

    pixel_values = dataset.map(setProperty)
    aggregate_pixel_values = (pixel_values.aggregate_array("NDVI").getInfo())
    mean_pixel_value = np.mean(aggregate_pixel_values)

    return mean_pixel_value

def ndvi_collection_gaul(adm0, year):
    """
    Collect the mean ndvi pixel values from the satellite per year per country,
    for countries that don't work with their name.

    :param adm0: Current Country GAUL Code
    :param year: Current Year

    :return float: mean pixel value of given year and country
    """

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

#iterating through years and countries to get each ndvi value of the USDOS countries
i = 0
while i < len(working_countries):
    year = 2001
    while year <= 2020:
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
print("USDOS countries finished, it took " + str(round((time_middle_2 - time_middle_1) / 60)) + " minutes.")

#Now same for the countries that the USDOS feature set doesn't recognize
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
    while year <= 2020:
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
