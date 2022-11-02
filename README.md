## Undernourishment Prediction

This is the backyard of Badass Datenjungs (distracted franklin), herzlich willkommen!

In the beginning we wanted to use crop yield data from kaggle and satelite images from google earth engine to anaylze and predict future crop yield.
Unfortunately the kaggle data was of low quality and many other teams predicted crop yield from satellite data before us. We now settled on predicting
prevalence of undernourishment in a given coutry and year. We use climate data (earth engine), economic data (FAO) and violent conflict data (UCDP)
to do so. Feel free to have a look around :)

Team member:
Nils - https://github.com/nilsmart96 ;
Neelesh - https://github.com/neelblabla ;
Jerome - https://github.com/sonic171717

Description of files:

data -> Raw input datasets as well as everything that is being created during the project

Dataset Construction -> Steps that are needed to build our final dataset, combining climate, economics and conflict data

Earth Engine Data Collection -> As the name suggests, python scripts that collect data from google earth engine

Models -> Analysing our self-created dataset and making predictions

Further information can be found here:

https://docs.google.com/document/d/1LRx-RHb_BrDnaqMHl_3nnihoNGNaeNGI/edit#heading=h.30j0zll
