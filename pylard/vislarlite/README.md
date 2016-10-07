# PyLArD LArLite Visualization 

These modules visualize some of the most used LArLite data products.

## Modules

### drawmimage2d.py

This file contains the module `PyLArLiteDrawImage2D` which draws the TPC data. It converts the larlite `wire` data product into a larcv `Image2D` product.  The latter is visualizable using the RGB event display viewer.

Example configuration:

    caldata: {
      isactive: true
      module_file: "vislarlite/drawimage2d"
      module_type: "PyLArLiteDrawImage2D"
      destination: "rgbdisplay"
      wire_producer: "caldata"
      wire_downsampling: 1
      time_downsampling: 6
      start_tick: 2400
      tick_offset: 2400
    }

Parameter descriptions

| Parameter | Description |
|-----------|-------------|
| wire_producer | name of tree containing wire data. (ex. for wire_caldata_tree wire_producer='caldata' |
| wire_downsampling | (not in use yet) |
