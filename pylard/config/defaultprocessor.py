import os,sys

def getDefaultProcessorConfig():
    """ makes a default processor file to load at beginning. """
    processor_cfg = """{
LArLiteData: {
  # Note. for LArLite this module is a dummy module
  # It will pass through.
  # However, for PyLArD, the pylard version will fill the RGB and 
  module_type: "LArLitePyLArD_DataInterface"
  
}
DrawX: {
  # Note. for LArLite this module is a dummpy module
  # However, for PyLArD, the pylard version will fill the RGB and 
  module_type: "LArLitePyLArD_DataInterface"
}  
"""
    return processor_cfg
