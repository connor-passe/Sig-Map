# Overview
Sig-Map is an iOS app developed as an MVP to explore the feasibility of performing signal propagation modeling on a mobile device. While signal propagation modeling is not a new field (it dates back to the 1950's), the concept of doing so accurately and in a computationally-constrained environment is fairly novel. Most simulation packages are firmly focused on accuracy above all else and can only be run in a dedicated desktop environment. I was interested in developing an application that could do the following:
* Perform calculations on a mobile device
* Handle a wide range of transmission frequencies and physical terrain
* Balance accuracy and runtime

This project would be considered a simple example of Surrogate Modeling. Surrogate Modeling uses Machine Learning (ML) and other techniques to approximate computationally expensive simulations / calculations with simpler / faster algorithms.

A pair of articles written about the development of Sig-Map by the creator Connor Passe, can be found [here](https://medium.com/@quill.giro0l/developing-a-surrogate-modeling-based-signal-propagation-model-1010cf4f85e8) and [here](https://medium.com/@quill.giro0l/ios-on-device-signal-propagation-modeling-5987eae60aa2). 

The example map data required to run the iOS app can be downloaded [here](https://drive.google.com/drive/folders/1CzM30kBMjmx7pSHBKRhcDSdEZj0B2_Uy?usp=share_link) and installed in the /TileElevationData folder.

# iOS App
For additional detail on the contents of this folder see [here](https://medium.com/@quill.giro0l/ios-on-device-signal-propagation-modeling-5987eae60aa2).

## SignalMapper
Sig-Map follows Model–view–viewmodel architectural pattern to separate UI from logic
### ContentView
App home / main screen UI information. 
### ContentView-VM
ContentView extension: houses functions and main app logic
### MapView
Powers the main underlying map for the app. Also responsible for heat-map and transmitter pin rendering / placement.

### /PowerLossPrediction
Houses ML model and observable object struct for holding PowerLoss array.
### /ExtensionsModifications
Houses extensions and ViewModifiers 
### /TileElevationData
Houses .CSV files. Imported from elevationCSVs. Download from Google Drive [here](https://drive.google.com/drive/folders/1CzM30kBMjmx7pSHBKRhcDSdEZj0B2_Uy?usp=share_link).
### Tiles
Houses data structure and information pertaining to tile rendering
### /TransmitterAnnotation
Houses information pertaining to the transmitter pin annotation rendering

# /Data Processing

## /Data
### /dted/UK
This folder contains seven subfolders, each with the corresponding raw DTED files for each of the seven UK cities (the same seven from the Ofcom study).
### /elevationCSVs
This folder contains the output of elevationCSVBuild.ipynb. These serve as the data input for the iOS app.
### /trainingDataset
This folder contains the output of trainingDataBuild. These serve as the training data for the ML models.
### /UKDataset
This folder contains the 42 .CSV files from the Ofcom study. The data spans seven cities across six different frequencies. Each contains the lat, long, power loss, and frequency for each of the points.

### constants.py
A mapping from key to city values for the seven cities.
### dtedParser.py
Defines the function `get_dted` that returns three arrays (latitude, longitude, elevation) for each of the points contained in the multiple DTED tiles that surround each city. Also creates a plot of the map, color mapped to elevation values.
### elevationCSVBuild.ipynb
The script combines the results of `get_dted` for a single DTED tile into a .CSV saved to /elevationCSVs.
### helpers.py
Defines a variety of functions used by trainingDataBuild.py to calculate a variety of features.
### loadUK.py
Defines the function `load` that returns the data contained within each of the files in /UKDataset.

### pathProfile.py
Used by trainingDataBuild for feature generation.
### trainingDataBuild.py
Loads elevation, power, and location data and saves as a .CSV:


| Column Name            | Unit | Description                                    |
| ---------------------- | ---- | ---------------------------------------------- |
| Frequency              | MHz  | Transmission frequency                         |
| Power Loss             | dB   | Amount of power loss measured                  |
| Distance               | km   | Transmission distance                          |
| Height Difference      | m    | Difference in transmitter and receiver heights |
| Peak Avg. Height Diff. | m    | Average height of peaks on path                |
| Peak Avg. Distance     | km   | Average distance away from transmitter on path |
| Max Peak               | m    | Highest peak on path                           |
| Peak Count             |      | Number of peaks on path                        |


## /ML Model
For additional detail on the contents of this folder see [here](https://medium.com/@quill.giro0l/developing-a-surrogate-modeling-based-signal-propagation-model-1010cf4f85e8).
### environmentVersionCheck.ipynb
Script to check environemnt matches requirements
### featureAnalysis.ipynb
Analysis of dataset features
### MLDev.ipynb
Development, training, and evaluation of ML models
### parameterTuning.ipynb
Hyperparameter tuning

