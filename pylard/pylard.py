# ============================================================
# pyLArD: python Liquid Argon Display
#
# package is meant to provide an easily modifyable event
# display to assist in algorithm development for 
# reconstructing neutrino interactions in liquid argon TPCS.
#
# ============================================================


# Modules
# pylarsoftzmq: ZMQ socket application for requesting data
# pylarev: class to flexibly pass data around
# pylardisplay: the event display
# pylaralgo: manager of the algorithm chain
#
# envisioned flow
# (1) provide pylargo the algoorithms to process
# (2) request data from file(s), along with the different LArSoft products
# (3) process data:
#     - each algorithm gets the data and the event display 
#       instance so it can draw what it wants
#     - each algostep gets it owns panel. it can choose to modify others, too.
#       it's python, offer a suggestion, but do whatever you want
# (4) after an event process, the user can rerun at different stages!
#     this is what running in ipython will allow
# 
# Event Display


