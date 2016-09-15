MY_LARLITE=[your larlite folder]
MY_LARCV=[your larcv folder]

cd $MY_LARLITE/config
source setup.sh
cd -
source $MY_LARCV/configure.sh
source [env-name]/bin/activate