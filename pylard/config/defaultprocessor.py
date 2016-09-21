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

opdata: {
  # Note. for LArLite this module is a dummpy module
  # However, for PyLArD, the pylard version will fill the RGB
  # FIXME: opdetdisplay expects product with name opdata
  module_file: "vislarlite/drawopdata"
  module_type: "PyLArLiteDrawOpdata"
  destination: "opdetdisplay"
  opdata_producer: "pmtreadout"
  trigger_producer: "triggersim"
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

  # use native format
  DrawOpDigits: {
    module_file: "visrawdigits/drawopdigits"
    module_type: "RawDigitsDrawOpDigits"
    destination: "opdetdisplay"
  }
} 
"""
    return default_processor_cfg
