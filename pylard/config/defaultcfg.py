import os,sys

def default_pylard_cfg():
    dft = """
{
  "larcv_process_cfg": "default_larcv.cfg", 
  "larlite_process_cfg": "default_larlite.cfg", 
  "larlite_filelist": "", 
  "larcv_filelist": "",
  "load_files_on_start":"no",
  "default_filetype_driver":"LARLITE"
}"""
    return dft
