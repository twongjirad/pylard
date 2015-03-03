import pylard.pylardisplay as pd
#import pylard.pylarsoftzmq as larzmq

# Physics/Reconstruction Goals
# (1) study low energy [10-100 MeV] reconstruct
# (2) study low energy [10-100 MeV] backgrounds
# (3) NC-proton oscillations

# To Do List:
# (1) connect and bring in data for wires and PMTs: first raw data
# (1B) data cache/background data loading
# (2) next bring in first level recon objects: ROIs, OpFlashes
# (2B) ROI wireinfo only to reduce loading time
# (2C) console/restartable chain
# (3) 2nd level: spacepoints+OpFlashes-interaction bundles
# (4) 3rd level: tracks/showers
# (5) 4th level: pid
# (6) 5th level: classification, energy

pd.run_daefile( "microboone_32pmts_nowires_cryostat.dae" )
#eventzmq = larzmq.EventServer()
