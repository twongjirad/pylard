import os,sys

def getDefaultProcessorConfig():
    """ makes a default processor file to load at beginning. """
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
DrawOpHits: {
  # Note. for LArLite this module is a dummpy module
  # However, for PyLArD, the pylard version will fill the RGB and 
  module_type: "PyLarliteDrawOpHits"
  item_set: "opdata"
  producer: "pmtreadout"
}  
"""
    return default_processor_cfg
