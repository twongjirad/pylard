This module is what pylard will use to process events.

# to do

* configure c-extension in setup.py

# design description

## inputs

* filelist of larlite and larcv files
* larlite/larcv processor configuration file

## outputs

* will make larlite objects, larcv objects, also the draw analyzers should make numpy objects for pylard to be able to draw

## controls/features

* some overhead is involved for parsing a list of larcv and larlite files
* so we can make a hash based on the filelist and things like event indices and stuff