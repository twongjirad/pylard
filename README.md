# PyLArD 2: The Lardening

## python Liquid Argon (Event) Display 2

Goal is to provide a visual algorithm development framework using data products from LArCV and LArLite

## Dependencies

* Python
* PIP
* VirtualEnv (optional, but recommended)
* ROOT
* Cython (part of installation script)
* numpy (part of installatino script)
* sip
* PyQt4
* PyOpenGL
* PyQtGraph (part of installation script)
* LArLite (branch feature/tmw_larlite_interface, will merge into develop soon)
* PIL: python larlite interface
* LArCV

## Installation

### Summary
* install sip
* install PyQt4
* install PyOpenGL
* install pyqtgraph
* install virtualenv
* install ROOT
* install LArLite
* install LArCV
* make environment
* run setup.py

### Details

Installation can be split between packages best installed by a package manager and those installed by hand.

#### Package Manager Installation

For python, pip, virtualenv, sip, PyQt4, PyOpenGL, pyqtgraph, these are best installed using package managers. Here are some examples:

* Ubuntu: apt-get
* MacOSX: macports or homebrew. Note! For Mac, do not install both macports and homebrew. This will really mess up your system. Pick only one. Examples in this readme will assume homebrew

Mac Commands (assuming homebrew)
* python: brew install python
* pip (part of brew installation of python)
* pip install virtualenv
* sip: brew install sip
* PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate
* PyQt4: brew install pyqt
* pyqtgraph: pip install pyqtgraph
* numpy: pip install numpy

#### Dependencies best installed by Hand 

* ROOT: High-energy physics staple. Note: you need the pyroot module to be installed. This is typically setup by default.
* larlite: see below
* larcv: see blow

#### LArLite

For larlite, we need to setup a special version that provides additional python-larlite interfaces. Find a suitable place for your copy of larlite and clone it:

    git clone https://github.com/larlight/larlite

Go into the repo and then switch to the special branch

   cd larlite
   git checkout feature/tmw_pylard_interface

Go into the UserDev folder and clone in a submodule

   cd UserDev
   git clone https://github.com/twongjirad/PLI pylard

Go back to the base larlite directory, then configure larlite

   cd ..
   source config/setup.sh

Make the core, UserDev/BasicTool, and UserDev/pylard/PyAnalyzer

   make -j4
   cd UserDev/BasicTool
   make -j4
   cd ../pylard/PyAnalzyer
   make -j4

OK. To check if this got built correctly. Check to see if you see 'libpylard_PyAnalyzer.so' in the library folder (lib).

#### LArCV

Make a new directory somewhere that LArCV will go into

   git clone https://github.com/larbys/LArCV LArCV

Go into the repo and configure the build:

   source configure.sh

Make sure you see that the larlite package was found (and in the right place):

   Found larlite set up @ $LARLITE_BASEDIR=/Users/twongjirad/working/uboone/larlite

Make
 
   make -j4

### pylard itself

Find a good place for your copy of pylard and clone the repository:

   git clone https://github.com/twongjirad/pylard

Right now, PyLArD version 2 is in a special branch

   git checkout tmw_pylard2

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

# Running PyLArD

Make sure your environment is setup. This requires LArCV and larlite environment variables to be set.  To quickly set these whenever you start a new shell session, you might create a script that does:

    MY_LARLITE=[your larlite folder]
    MY_LARCV=[you larcv folder]
    cd $MY_LARLITE/config
    source setup.sh
    cd -
    source $MY_LARCV/configure.sh
    source [env-name]/bin/activate

You can find such a script in example_setup.sh.

Then you can start up pylard using

    python run_pylard2.py

The way you load files is somewhat different depending on the file format.

## Loading RawDigitsWriter files

Basically this format is a dump of uboone data into simple vectors stored in a TTree.  
Note that one needs to use an updated copy of RawDigitWriter for pylard2 to work.  
One can get a copy from 'origin/feature/tmw_rawdigitswriter_update' feature branch. 
It is based on tagged uboonecode version v06_04_00.

Input files go into pylard through a textfile with a list of files.  For example, if you have my_rawdigits.root, make a file doing:

    find my_rawdigits.root > myfiles.txt

In the 'EventLoop' panel (navigate it using the tabs above), enter 'myfile.txt' into 'Input File List' box and hit 'Load File'. You may also use the 'Select' button to choose the file.

You should see the above table get filled in.  Under RAWDIGITS, you'll see the number of events (in the second column). There is also a grey arrow that if you click on it will expand into the list of run, subrun, and event IDs in the filelist you provided.

    rsync -av --progress [username]@uboonegpvm02.fnal.gov:/uboone/app/users/tmw/pylardsample/rawdigits_sample.root .

Test this via:

    python view_opdata.py rawdigits_sample.root

Now in the same panel, click on the 'rawdigits' checkbox.  This shows you the configuration file for the RawDigits event loop processor. You don't need to change anything for now.  

Below the configuration file panel, you'll see places to enter an entry number, run, subrun, or event ID.  Leave that as is, which should be showing info for the first entry.  However, change the filetype to 'RAWDIGITS' and hit 'Go'.

If everything worked, you should be able to navigate to the 'OpDet Display' panel and see the event data plotted.  You can use the nvaigation tools on this panel to look through the rest of the events.

### Making RawDigitWriter data for the viewer

Check out the wiki page [here](https://github.com/twongjirad/pylard/wiki/Making-data-for-the-viewer).

## Loading LArLite/LArCV files

One has to provide seperate text files for larlite and larcv files, with each listing the path of files one wants to open.  (Don't mix file types!)



