Building of our dataset

How to read:

Every file that ends in _data.csv_ is a data file that has not been processed yet.
Everything else is created in the corresponding jupyter notebooks.

Goal is the creation of a main dataset, combining all the individual sources.

The steps in this procedure are as follows:

1) create_country_time_index -> here we use the dataset on undernourishment as a base, as we want to predict this variable
2) create_ee_country_check -> we use earth engine for climate data, and some countries don't work, this creates a df of working countries
3) create_combined_dataset -> here the final dataset is being created
