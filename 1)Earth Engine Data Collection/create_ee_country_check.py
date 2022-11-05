#import of necessary libraries
import ee
import pandas as pd

#path to import and export data (paste your own file location here)
path = (r"C:\Users\nmart\OneDrive - fs-students.de\Dokumente"
r"\Office\FS\S1\Data Analytics in Business\code_daib"
r"\Analysing-crop-yields-and-predicting-food-sustainability-of-nations-in-near-future"
r"\Earth Engine Data Collection")

#connecting to google earth engine
ee.Authenticate()
ee.Initialize()

def country_check(country):
    """
    check if the country will work when collecting data for temperature, 
    precipation and NDVI

    :param country: Current Country

    :return string: working, shape_error or name_error
    """
    
    location = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0"
    ).filter(ee.Filter.eq("ADM0_CODE", country))
    if location.size().getInfo() > 0:
        Perimeter = location.geometry().perimeter()
        PerimeterKm = ee.Number(Perimeter).divide(1e3).round().getInfo()
        if PerimeterKm < 9e4:
            return str("working")
        else:
            return str("shape_error")
    else:
        return str("name_error")

print("Starting country check...")

#importing the list of countries
df_base = pd.read_csv(path + (r"\country_time_base.csv"))
countries_with_doubles = df_base["GAUL"].tolist()
seen = set()
countries = []
for item in countries_with_doubles:
    if item not in seen:
        seen.add(item)
        countries.append(item)

#loop to check every country using the function defined above
check_result = []
country_index = []
i = 0
while i < len(countries):
    result = country_check(country = countries[i])
    check_result.append(result)
    country_index.append(countries[i])
    i += 1

#creating area index
countries_with_doubles = df_base["Area"].tolist()
seen = set()
countries = []
for item in countries_with_doubles:
    if item not in seen:
        seen.add(item)
        countries.append(item)

#saving the results of the function
dict = {"GAUL": country_index, "Area": countries, "ee check": check_result}
df_country_check = pd.DataFrame(dict)
df_country_check.to_csv(path + (r"\ee_country_check.csv"))

#creating a dataset that can be used for data collection
ee_collection = df_country_check[df_country_check["ee check"
].str.contains("working") == True
].reset_index().drop(columns=["index", "ee check"])
ee_collection.to_csv(path + (r"\ee_collection_dataset.csv"))

print("Country check finished, data saved to path:")
print(path)
