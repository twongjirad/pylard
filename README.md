# pylard: python Liquid Argon (Event) Display

Goal is to provide a easily customizable MicroBooNE event display for both the TPC and PMT data.

The idea is to provide basic displays which the user can draw on top of.

## Screenshots

3D model of detector

![Detector Display Image](https://github.com/twongjirad/pylard/blob/develop/pylard/misc/detectormodel.png)

Viewer for Optical Data
![Optical Data Image](https://github.com/twongjirad/pylard/blob/develop/pylard/misc/example_michel1.png)


## Dependencies

Pre-dependencies:
* pip: I assume that much of the dependencies can be installed using pip.  You can use apt-get (or your OS's equivalent) to install pip. Another option is to follow [these](https://pip.pypa.io/en/stable/installing/) instructions. If you aren't an administrator on your machine, pip can be installed locally following [this](https://forcecarrier.wordpress.com/2013/07/26/installing-pip-virutalenv-in-sudo-free-way/)
* virtualenv: not required, but highly, highly recommended. It allows you to build a sandbox environment for python. If you install pylard in such a sandbox, the package and its dependencies can be removed easily (and installed without root privileges).

Get these first, since they can't be grabbed by PIP via setuptools:
* ROOT: High-energy physics staple. Note: you need the pyroot module to be installed
* pyqt4: best installed using apt-get (or it's equivalent on linux) and macports (or its equivalent on OS X)
* sip: needed by pyqt4. 
ROOT is best installed using it's tools (https://root.cern.ch/). SIP and PYQT4 is best installed using apt-get or in OS X, homebrew or macports.

These should be installed by the setup script:
* pyqtgraph: visualization package used to make GUI and plots. utilizes 3D acceleration.
* pyqt4: what pyqtgraph uses to draw it's objects
* pyopengl: needed for 3D acceleration
* numpy: what raw waveforms will be stored in. you should really install this in your main python install.
* root_numpy: converts ROOT tree information into numpy arrays
* pandas (and by extension pyTables): allows us to quickly query ROOT tree/numpy array content
* lz4: compression
* collada: interface for dealing with COLLADA format, a standard for packaging 3D model information. The 3D model of the MicroBooNE detector is stored in this format
* zmq: socket interface (optional): in my dreams event data is passed back-and-forth via sockets. never going to happen.

## Installation

I recommend installing everything inside a python virtual environment.  pylard brings in a lot of python pacakges. At the end of the day, you might not want all of this. Using a virtualenv sandbox allows you to keep all of this crap separate from your main python installation.

To start, get virtualenv
  
    pip install virtualenv

Then make a folder somewhere not in the base pylard directory.  

In the new folder, create a new virtualenv.
* To make an environment which will use the python packages you've already installed (recommended)

    virtualenv --system-site-packages [env-name, e.g. env]


To activate the environment

    source [env-name]/bin/activate


You should now have a prompt indicating the environment is active

    ([env-name]) Taritreees-MacBook-Pro:test twongjirad$

To get out of the environment

    deactivate

To destroy this installation

   rm -rf [env-name]

Destroying the python setup is that easy. That's why I like this.

Finally, to install the package, go to the base pylard directory and type

    python setup.py install

## Let's test this

### 3D Detector Display

Run

    python run_detdisplay.py


### Optical Data Display
You can run view_opdata.py to see if the installation worked.  To get a datafile (output of RawDigitsWriter) go to the uboonegpvm machines and copy 

   rsync -av --progress [username]@uboonegpvm02.fnal.gov:/uboone/app/users/tmw/pylardsample/rawdigits_sample.root .

Test this via:

   python view_opdata.py rawdigits_sample.root


## sub-packages
* pylardisplay: the main GUI windows are here
* pylardata: interfaces to various types of data. currently supporting output from uboone/RawData/utils/RawDigitsWriter_module.cc and larlite.
* pylareventmanager: zmq interface to data products. vaporware.


