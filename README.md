# pylard 2: The Lardening

Again! But this time, better! Well, maybe.

## python Liquid Argon (Event) Display 2

Goal is to provide a visual algorithm development framework using data products from LArCV and LArLite

## Dependencies

* ROOT
* Cython
* PyQtGraph
* LArLite
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

### More details

For sip, PyQt4, PyOpenGL, pyqtgraph, these are best installed using package managers. Here are some examples:

* Ubuntu: apt-get
* MacOSX: macports or homebrew

Note! For Mac, do not install both macports and homebrew. This will really mess up your system.

For ROOT, LArCV installation is fairly straight forward.

For LArLite, one should clone the larlite repository.  Then go into UserDev and clone [this](https://github.com/twongjirad/PLI) repository into the folder.

    git clone https://github.com/twongjirad/PLI

This repository contains some python-larlite interfaces pylard can use.

Note go back into the larlite base directory and make. Hopefully it builds.

### pylard itself

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

Make sure your environment is setup. This requires LArCV and larlite environment variables to be set.  To set these, you might create a script that does:

    MY_LARLITE=[your larlite folder]
    MY_LARCV=[you larcv folder]
    cd $MY_LARLITE/config
    source setup.sh
    cd -
    source $MY_LARCV/configure.sh
    source [env-name]/bin/activate

You can find such a script in example_setup.sh.

