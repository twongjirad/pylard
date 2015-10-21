# pylard: python Liquid Argon (Event) Display

Goal is to provide a easily customizable MicroBooNE event display for both the TPC and PMT data.

The idea is to provide basic displays which the user can draw on top of.

### installation

I recommend installing everything inside a python virtual environment.  This is because this tool brings in a lot of python dependencies. At the end of the day, you might not want all of this.

To do start, get virtualenv
"""   
pip install virtualenv
"""
   
Then make a folder somewhere not in the base pylard directory.  

In the new folder, create a new virtualenv.
* To make an environment which will use the python packages you've already installed
"""
    virtualenv --system-site-packages [env-name, e.g. env]
"""
* To start with a completely clean python environment 
"""
    virtualenv [env-name, e.g. env]
"""

To activate the environment
"""
source [env-name]/bin/activate
"""

You should now have a prompt indicating the environment is active
    ([env-name]) Taritreees-MacBook-Pro:test twongjirad$

To get out of the environment
    deactive

To destroy this installation
   rm -rf [env-name]
Desotrying the python setup is that easy. That's why I like this.

## sub-packages

## Dependencies

Being lazy, so have a few that serves merely for convenience:

* ROOT
* pyqtgraph
* numpy
* root_numpy
* pandas
* lz
* collada

## Installation

* install ROOT
* install dependencies
* install pylard by running
```
python setup.py install
```
* Third, hope I didn't ruin your python distribution. To be safe, I recommend using virtualenv.
