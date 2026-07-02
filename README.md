# Deepsea SAM Experiments

Code to reproduce a series of tests prompting SAM with existing human annotations on ocean imagery. More information can be found in our [Frontiers](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1469396/full) paper. 

The tests relied on several datasets: 

### FathomNet
[FathomNet](https://www.nature.com/articles/s41598-022-19939-2) is an globally distributed repository for annotated marine imagery. The database is extremely diverse and can be accessed through a [web interface](https://database.fathomnet.org/fathomnet/#/) or via the [python client](https://github.com/fathomnet/fathomnet-py). The subset used for these tests can be downloaded directly using the `download_images.sh` script in the FathomNet directory.

### OBSEA 
The Seafloor Observatory (OBSEA) Image Dataset is an annotated subsample of image data collected by a cabled video-platform deployed in a marine protected area 4 km off the coast of Barcelona, Spain. The full dataset is available on [Pangeo](https://doi.pangaea.de/10.1594/PANGAEA.946149). Download images and the annotations to reproduce results using the `download_data.sh` script in the OBSEA directory.  