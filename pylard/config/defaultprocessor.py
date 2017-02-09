import os,sys

def getDefaultProcessorConfig(filetype):
    """ makes a default processor file to load at beginning. """
    print "returning ",filetype
    if filetype=="LARLITE":
        default_processor_cfg = """
# ===================================================================
# Example PyAnalyzer
# -------------------
# use modules like this to develop new algorithms and data products.
# an instance of the storage manager is provided. So one has access
# to all data products in the file or those created upstream.
# ===================================================================
#LArLiteData: {
#  # Note. for LArLite this module is a dummy module
#  # It will pass through.
#  # However, for PyLArD, the pylard version will fill the RGB and 
#  module_type: "PyAnalyzer"
#  PyFilePath: "pylard/eventprocessor/example.py"
#  StorageVariableName : "event_storage_manager"
#}

# ===================================================================
# Configure converters of larlite data products to things
# pylard can draw.
#
# ===================================================================

VisProcessor: {
  opdata: {
    # Note. for LArLite this module is a dummpy module
    # However, for PyLArD, the pylard version will fill the RGB
    # FIXME: opdetdisplay expects product with name opdata
    isactive: true
    module_file: "vislarlite/drawopdata"
    module_type: "PyLArLiteDrawOpdata"
    destination: "opdetdisplay"
    opdata_producer: "pmtreadout"
    trigger_producer: "triggersim"
  }
  caldata: {
    isactive: true    
    module_file: "vislarlite/drawimage2d"
    module_type: "PyLArLiteDrawImage2D"
    destination: "rgbdisplay"
    wire_producer: "caldata"
    wire_downsampling: 1
    time_downsampling: 6
    start_tick:  2400
    tick_offset: 2400
  }
}
"""
    elif filetype=="LARCV":
        default_processor_cfg = """
# ===================================================================
# Example LArCV Processor
# -----------------------
ProcessDriver: {
  Verbosity: 2
  EnableFilter: false
  RandomAccess: false
  ProcessType: []
  ProcessName: []

  IOManager: {
    Verbosity: 2
    Name: "IOManager"
    IOMode:  0 # 0=read-only, 1=write-only, 2=read&write
    OutFileName: "" # put output file name if write mode
    InputFiles:  []
    InputDirs:   []
    ReadOnlyType: [0,1] # 0=Image2D, 1=partroi
    ReadOnlyName: ["tpc","tpc"]
    StoreOnlyType: []
    StoreOnlyName: []
  }

  ProcessList: {
  }
}

VisProcessor: {
  DrawImage2D: {
    isactive: false
    module_file: "vislarcv/drawimage2d"
    module_type: "DrawImage2D"
    destination: "rgbdisplay"
    image2d_producer: "tpc"
    roi_producer: "tpc"
    TimeDownsamplingFactor: 1.0
    WireDownsamplingFactor: 1.0
  }
}

"""
    elif filetype=="RAWDIGITS":
        default_processor_cfg = """
# ===================================================================
# Example RawDigits Processor
# -----------------------------
# we can choose to convert into larlite product
# ===================================================================

ProcessDriver: {

  #RawDigits2LArLite: {
  # makes an output larlite tree
  # module_type: "PyAnalyzer"
  # PyFilePath: "pylard/eventprocessor/example.py"
  # StorageVariableName : "event_storage_manager"
  #}
}

VisProcessor: {

  # use native format
  opdata: {
    module_file: "visrawdigits/drawopdigits"
    module_type: "RawDigitsDrawOpDigits"
    destination: "opdetdisplay"
    isactive: true
  }

  tpcdata: {
    module_file: "visrawdigits/drawtpcrawdigits"
    module_type: "DrawTPCRawDigits"
    TimeDownsamplingFactor: 6.0
    WireDownsamplingFactor: 1.0
    destination: "rgbdisplay"
    isactive: false
  }



  # if we converted to larlite
  #DrawOpHits: {
  #  Note. for LArLite this module is a dummy module
  #  However, for PyLArD, the pylard version will fill the RGB and 
  #  module_file: "vislarlite/drawopdata"
  #  module_type: "PyLArLiteDrawOpdata"
  #  destination: "opdetdisplay"
  #  opdata_producer: "pmtreadout"
  #  trigger_producer: "triggersim"
  #} 

} 
"""
    return default_processor_cfg
