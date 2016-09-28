#thanks vic

import os
import sys
import copy
import re
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
#from .. import larcv

import numpy as np
import time
from pylard.pylardata.tpcdataplottable import TPCdataPlottable

#from ..lib.datamanager import DataManager
#from ..lib import storage as store

#from ..lib.hoverrect import HoverRect
#from ..lib.roislider import ROISlider

#try:
#    from cv2layout import CV2Layout
#except:
#    pass

#try:
#    from caffelayout import CaffeLayout
#    from ..rgb_caffe.testwrapper import TestWrapper
#except:
#    pass

#from roilayout import ROIToolLayout

import pyqtgraph.exporters

class RGBDisplay(QtGui.QWidget):

    def __init__(self):
        super(RGBDisplay, self).__init__()

        # Size the canvas
        self.resize(1200, 700)

        # FIXME: get rid of dependence of this variable
        self.planes = 3 # this is really the number of RGB channels, always 3

        # Graphics window which will hold the image
        self.win = pg.GraphicsWindow()
        self.plt = self.win.addPlot()
        self.imi = pg.ImageItem(np.zeros((100,100))) # dummy
        self.plt.addItem( self.imi )

        # Handles to the axis which we will update with wire/tick
        self.plt_x = self.plt.getAxis('bottom')
        self.plt_y = self.plt.getAxis('left')

        # Main Layout
        self.layout = QtGui.QGridLayout()

        # run information up top
        self.runinfo = QtGui.QLabel(
            "<b>Run:</b> -1 <b>Subrun:</b> -1 <b>Event:</b> -1")
        self.layout.addWidget(self.runinfo, 0, 0)
        self.layout.addWidget(self.win, 1, 0, 1, 10)
        self.setLayout(self.layout)

        # Input Widgets
        # Layouts
        self.lay_inputs = QtGui.QGridLayout()
        self.layout.addLayout(self.lay_inputs, 2, 0, 1, 10)
        
        # -------------------------------------------------------
        # Navigation box
        self.navheight = 4
        self.navwidth  = 2
        navstart = 0
        self._makeNavFrame()
        self.lay_inputs.addWidget( self._navframe, 0, navstart, self.navheight, self.navwidth  )
        
        # -------------------------------------------------------
        # Thresholding
        threshstart = navstart+self.navwidth
        self.contrast_frame = self._makeContrastFrame()
        self.lay_inputs.addWidget(self.contrast_frame, 0, threshstart, self.navheight, self.navwidth )
        
        # --------------------------------------------------------
        # Image 2D selection
        imagepanelstart = threshstart+self.navwidth
        self.image_panel = self._makeImage2Dcontrol()
        self.lay_inputs.addWidget(self.image_panel, 0, imagepanelstart, self.navheight, self.navwidth )
        self.src_rgbchannels = [self.image_src_rch,self.image_src_gch,self.image_src_bch]
        self.src_views = []
        self.ovr_rgbchannels = [self.image_ovr_rch,self.image_ovr_gch,self.image_ovr_bch]
        self.ovr_views = []
        #self.high_res = False # cruft?
        
        # --------------------------------------------------------
        # ROI panel
        roipanelstart = imagepanelstart+self.navwidth
        self.roi_panel = self._makeROIpanel()
        self.lay_inputs.addWidget(self.roi_panel, 0, roipanelstart, self.navheight, self.navwidth)

        # --------------------------------------------------------
        # user item tree widget
        useritemstart = roipanelstart + self.navwidth
        self.user_item_frame = self._makeUserItemTreeFrame()
        self.lay_inputs.addWidget(self.user_item_frame, 0, useritemstart, self.navheight, self.navwidth)
        self.user_plot_items = {}       # stores whatever user is tryig to draw onto image
        self.user_plot_checkboxes = {}  # stores checkboxes that tell us to track item or not
        self.user_subitem_cbxs = {}
        self.map_user_checkboxes2name = {}
        
        # --------------------------------------------------------

        # False color mode
        self.use_false_color = QtGui.QCheckBox("Use False Color")
        self.use_false_color.setChecked(False)
        self.use_false_color.stateChanged.connect( self.enableFalseColor )
        self.false_color_widget = pyqtgraph.GradientWidget(orientation='right')
        # initial map
        state = { 'mode':'rgb', 'ticks':[ (0.0, (0,0,100,255)), (0.5, (128,255,255,255)), (1.0, (255, 0, 0, 255) ) ] }
        self.false_color_widget.restoreState( state )
        self.false_color_widget.sigGradientChangeFinished.connect( self.applyGradientFalseColorMap )
        self.layout.addWidget(self.false_color_widget, 1, 10, 1, 1)
        self.layout.addWidget(self.use_false_color, 0, 8, 1, 2)
        self.false_color_widget.hide()

        # --------------------------------------------------------
        
        self.clearImage2Ddata()

#         # --------------------------------------------------------
#         # Options
#         optstart = parstart + 1
#         # Auto range function
#         self.auto_range = QtGui.QPushButton("AutoRange")
#         self.lay_inputs.addWidget(self.auto_range, 0, optstart)
        
#         # Save image
#         self.savecounter = int(0)
#         self.saveimage = QtGui.QPushButton("Save Image")
#         self.saveimage.clicked.connect(self.saveImage)
#         self.lay_inputs.addWidget(self.saveimage,1,optstart)

        # --------------
        # Main window
        # --------------
        self.themainwindow = None

    def setMainWindow(self,window):
        self.themainwindow  = window

    # put the runinfo right above the graphics window
    def setRunInfo(self, run, subrun, event):
        self.runinfo.setText(
            "<b>Run:</b> {} <b>Subrun:</b> {} <b>Event:</b> {}".format(run, subrun, event))

    # set the ticks axis to be absolute coordinates
    def get_ticks(self):
        # everywhere USE ABSOLUTE COORDINATE (which is in tick/wire)
        meta = self.image.imgs[0].meta()
        xmax, ymax = meta.max_x(), meta.max_y()
        xmin, ymin = meta.min_x(), meta.min_y()

        comp_y = meta.height() / meta.rows()
        comp_x = meta.width() / meta.cols()

        dx = meta.width()
        dy = meta.height()

        ymajor = []
        yminor = []
        yminor2 = []
        xmajor = []
        xminor = []
        xminor2 = []

        for ix, y in enumerate(np.arange(int(ymin), int(ymax), comp_y)):

            label = (ix, int(y))

            if ix % 10 != 0:
                yminor2.append(label)
                continue

            if ix % 25 != 0:
                yminor.append(label)
                continue

            ymajor.append(label)

        for ix, x in enumerate(np.arange(int(xmin), int(xmax), comp_x)):

            label = (ix, int(x))

            if ix % 100 != 0:
                xminor2.append(label)
                continue

            if ix % 200 != 0:
                xminor.append(label)
                continue

            xmajor.append(label)

        return ([xmajor, xminor, xminor2], [ymajor, yminor, yminor2])

    # autorange button
    def autoRange(self):

        xticks, yticks = self.get_ticks()

        self.plt_y.setTicks(yticks)
        self.plt_x.setTicks(xticks)

        self.plt.autoRange()

        #if self.cv2_enabled == True:
        #    self.plt.addItem(self.swindow)
        #    self.swindow.setZValue(10)

    #which type of ROI do you want, BNB/particle/both?
    def which_type(self):

        for button in self.kTypes:
            if self.kTypes[button][0].isChecked():
                return self.kTypes[button][1]
        return None

    # =================================================================
    # Event Navigation

    # go to the previous event
    def previousEvent(self):
        ok = self.themainwindow.prevEntry()

    # go to the next event
    def nextEvent(self):
        ok = self.themainwindow.nextEntry()

    # go to an entry
    def gotoEntry(self):
        entry = int( self.event.text() )
        ok = self.themainwindow.getEntry( entry )
        if not ok:
            return ok

    # go to an RSE
    def gotoRSE(self):
        run = int(self.run.text())
        subrun = int(self.subrun.text())
        event = int(self.event_num.set_text())
        ok = self.themainwindow.getRSE(run,subrun,event)
        return ok

    def setEntryNumbers( self, entry, run, subrun, event ):
        self.run.setText("%d"%(run))
        self.subrun.setText("%d"%(subrun))
        self.event_num.setText("%d"%(event))
        self.event.setText("%d"%(entry))
        self.setRunInfo( run, subrun, event )

    def clearVisItems(self):
        self.clearUserVisItems()
        return

    def parentUserItemCheckBoxChanged(self):
        """ we change the values of the sub items if they exist"""
        sender = self.sender()
        name = self.map_user_checkboxes2name[sender]
        state = sender.isChecked()
        if name in self.user_subitem_cbxs:
            for subitembox in self.user_subitem_cbxs[name]:
                subitembox.setChecked(state)

    # =================================================================

    def plotData(self):

        # get the images, both src and overlay (ovr)
        src = self.getSrcProducer()
        ovr = self.getOvrProducer()
        if src=="":
            return True

        self.image     = self.images[ src ]
        if ovr!="":
            self.image_ovr = self.images[ ovr ]
        else:
            self.image_over = None

        # Clear out plot
        self.plt.clear()

        # Add image
        self.imi = pg.ImageItem()
        self.plt.addItem(self.imi)

        # whoops no image, return
        if self.image == None: return
        
        self.setContrast()

        # get list of views
        src_view = self.getSrcChannels()
        ovr_view = self.getOvrChannels()

        print src_view,ovr_view

        # threshold for contrast, this image goes to the screen
        self.pimg = self.image.set_plot_mat(self.iimin,self.iimax,src_view)
        #print "pimg shape: ",self.pimg.shape

        if self.image_ovr is not None:
            self.pimg_ovr = self.image_ovr.set_plot_mat(self.iimin,self.iimax,ovr_view)
            #print "pimg_ovr shape: ",self.pimg_ovr.shape

        drawnimg = np.zeros( self.pimg.shape )
        
        # get mix factor from slider bar
        slider_val = self.image_slider.value()
        slider_max = self.image_slider.maximum()
        slider_min = self.image_slider.minimum()
        mixfactor = float(slider_val-slider_min)/float( slider_max-slider_min )

        ovr_rgbfactors = {0:[self.ovr_rcolor.red(),self.ovr_rcolor.green(), self.ovr_rcolor.blue()],
                          1:[self.ovr_gcolor.red(),self.ovr_gcolor.green(), self.ovr_gcolor.blue()],
                          2:[self.ovr_bcolor.red(),self.ovr_bcolor.green(), self.ovr_bcolor.blue()]}

        if self.image_ovr is not None and self.pimg.shape==self.pimg_ovr.shape and slider_val>slider_min:
            ovrmix = np.zeros( self.pimg_ovr.shape )
            for rgb in range(0,3):
                for chovr in range(0,3):
                    ovrmix[:,:,rgb] += float(ovr_rgbfactors[chovr][rgb])/255.0*self.pimg_ovr[:,:,chovr]
            drawnimg = self.pimg*(1.0-mixfactor) + ovrmix*mixfactor
        else:
            drawnimg += self.pimg

        # Emplace the image on the canvas
        #self.imi.setImage(self.pimg)
        self.setImage(drawnimg)


        # draw user items
        self.drawUserItems()

        # draw ROIs

#         # no ROI's -- finish early
#         if hasroi == False:
#             self.autoRange()
#             return

#         xmin, xmax, ymin, ymax = (1e9, 0, 1e9, 0)
#         for roi in self.rois:
#             for bb in roi['bbox']:
#                 if xmin > bb.min_x():
#                     xmin = bb.min_x()
#                 if xmax < bb.max_x():
#                     xmax = bb.max_x()
#                 if ymin > bb.min_y():
#                     ymin = bb.min_y()
#                 if ymax < bb.max_y():
#                     ymax = bb.max_y()

#         if self.roi_exists == True:
#             self.drawBBOX(self.which_type())

        self.autoRange()

    def regionChanged(self):

        # the boxed changed but we don't intend to transform the image
        if self.cv2_layout is not None and self.cv2_layout.transform == False:
            return

        # the box has changed location, if we don't have a mask, create on
        if self.modimage is None:
            self.modimage = np.zeros(list(self.image.orig_mat.shape))

        # get the slice for the movable box
        sl = self.swindow.getArraySlice(self.image.orig_mat, self.imi)[0]

        # need mask if user doesn't want to overwrite their manipulations
        if self.cv2_layout is not None and self.cv2_layout.overwrite == False:
            idx = np.where(self.modimage == 1)
            pcopy = self.image.orig_mat.copy()

        # do the manipulation
        if self.cv2_layout is not None:
            self.image.orig_mat[sl] = self.cv2_layout.paint( self.image.orig_mat[sl] )

        # use mask to updated only pixels not already updated
        if self.cv2_layout is not None and self.cv2_layout.overwrite == False:
            # reverts prev. modified pixels, preventing double change
            self.image.orig_mat[idx] = pcopy[idx]
            self.modimage[sl] = 1

        # we manipulated orig_mat, threshold for contrast, make sure pixels do not block
        self.pimg = self.image.set_plot_mat(self.iimin,self.iimax)  

        # return the plot image to the screen
        #self.imi.setImage(self.pimg) # send it back to the viewer
        self.setImage(self.pimg) # send it back to the viewer

    def drawBBOX(self, kType):

        # set the planes to be drawn
        self.setViewPlanes()

        # no image to draw ontop of
        if self.image is None:
            return

        # no type to draw
        if kType is None:
            return

        # remove the current set of boxes
        for box in self.boxes:
            self.plt.removeItem(box)

        # if thie box is unchecked don't draw it
        if self.draw_bbox.isChecked() == False:
            return

        # clear boxes explicitly
        self.boxes = []

        # and makew new boxes
        for roi_p in self.rois:

            if roi_p['type'] not in kType:
                continue

            for ix, bbox in enumerate(roi_p['bbox']):

                if ix not in self.views: 
                    continue

                imm = self.image.imgs[ix].meta()

                # x,y  relative coordinate of bounding-box w.r.t. image in original unit
                x = bbox.min_x() - imm.min_x()
                y = bbox.min_y() - imm.min_y()

                # dw_i is an image X-axis unit legnth in pixel. dh_i for
                # Y-axis. (i.e. like 0.5 pixel/cm)
                dw_i = imm.cols() / (imm.max_x() - imm.min_x())
                dh_i = imm.rows() / (imm.max_y() - imm.min_y())

                # w_b is width of a rectangle in original unit
                w_b = bbox.max_x() - bbox.min_x()
                h_b = bbox.max_y() - bbox.min_y()

                ti = pg.TextItem(text=larcv.ROIType2String(roi_p['type']))
                ti.setPos(x * dw_i, (y + h_b) * dh_i + 1)

                print str(self.event.text()),x * dw_i, y * dh_i, w_b * dw_i, h_b * dh_i,"\n"

                r1 = HoverRect(x * dw_i,
                               y * dh_i,
                               w_b * dw_i,
                               h_b * dh_i,
                               ti,
                               self.plt)
                
                r1.setPen(pg.mkPen(store.colors[ix]))
                r1.setBrush(pg.mkBrush(None))
                self.plt.addItem(r1)
                self.boxes.append(r1)

    # user scrolled to another channel
    def changeChannelViewed(self):

        # fill self.views -- the indicies of the chosen channels
        self.setViewPlanes()

        # get the contrast
        self.setContrast()
        
        # swap what is in work_mat to orig_mat and do the thresholding
        self.pimg = self.image.swap_plot_mat( self.iimin, self.iimax, self.views )

        # set the image for the screen
        #self.imi.setImage(self.pimg)
        self.setImage(self.pimg)

    # you probably hit "forward" so load the current image into the wrapper
    # through caffe_layout.py
    def load_current_image(self):

        print "Loading current image!"
        
        # revert the image back to Image2D.nd_array style
        self.image.revert_image()

        # make caffe_image which would be different than image2d, i.e.
        # do some operation on work_mat if you want
        self.image.emplace_image()

        # revert work_mat/orig_mat back since we made a copy into
        # self.image.caffe_copy
        self.image.revert_image()

        # send off to the network (through caffe_layout.py)
        return self.image.caffe_image

    def setContrast(self):

        if self.user_contrast.isChecked() == True:
            self.iimin = float(self.imin.text())
            self.iimax = float(self.imax.text())
        else: # get it from the max and min value of image
            self.iimin = self.image.iimin
            self.iimax = self.image.iimax
            self.imin.setText("%.2f"%(self.iimin))
            self.imax.setText("%.2f"%(self.iimax))
            #print "Setting self.imin text {}=>{}".format(self.image.iimin,self.iimin)
            #print "Setting self.imax text {}=>{}".format(self.image.iimax,self.iimax)

    def saveImage(self):
        exporter = pg.exporters.ImageExporter(self.plt)
        #not sure what it the best way to do this...
        #exporter.parameters()['width']  = 700   # (note this also affects height parameter)
        exporter.parameters()['height'] = 700 
        exporter.export('R{}_S{}_E{}.png'.format(str(self.run.text()),str(self.subrun.text()),str(self.event.text())))
#        exporter.export('saved_image_{}_{}.png'.format(str(self.event.text()),self.savecounter))
        print "Saved image {}".format(self.savecounter)
        self.savecounter += 1

    def setImage( self, img ):
        """Wrapper for hacking. """
        if img is None:
            print "No image?"
            # sometimes no image to set yet
            return

        if not self.use_false_color.isChecked():
            self.imi.setImage( img )
        else:
            self.applyGradientFalseColorMap()
            #print "flatten image and set it"
            flatten = np.sum( img, axis=2 )
            self.imi.setImage( flatten )
        

    def enableContrast(self):

        if self.user_contrast.isChecked() == True:
            self.imin.setDisabled(False)
            self.imax.setDisabled(False)
        else :
            self.imin.setDisabled(True)
            self.imax.setDisabled(True)

    def applyGradientFalseColorMap(self):
        """ connected to false color widget signal: sigGradientChangeFinished.
            job is to set the color map of the image plot (self.imi)"""
        if self.use_false_color.isChecked():
            #print "Set false color scale"
            self.lut = self.false_color_widget.colorMap().getLookupTable(0.0, 1.0, 256)
            try:
                self.imi.setLookupTable(self.lut)
            except:
                pass

    def enableFalseColor(self):
        """ connected to false color check box: self.use_false_color. 
            when checkbox toggled, this is called to activate false color drawing.
            you can find how that is being done in setImage. """
        # colorscale:
        if self.use_false_color.isChecked():
            self.false_color_widget.show()
            self.applyGradientFalseColorMap()
            self.setImage( self.pimg )
        else:
            # attempt to reset it
            #print "restore false color scale"
            self.false_color_widget.hide()
            try:
                self.imi.setLookupTable(None)
                self.imi.setLevels( [[0,255],[0,255],[0,255]] )
            except:
                pass
            self.setImage( self.pimg )

    def _makeNavFrame(self):
        self._navframe = QtGui.QFrame()
        self._navframe.setLineWidth(1)
        self._navframe.setFrameShape( QtGui.QFrame.Box )
        self._navlayout = QtGui.QGridLayout()

        labelwidth = 40
        inputwidth = 60

        # Navigation between entries
        self.event = QtGui.QLineEdit("%d" % 0)      # entries number
        entry_label = QtGui.QLabel("entry")
        entry_label.setFixedWidth(labelwidth)
        
        # -------------------------------------------------------
        # erez - July-21, 2016
        # -------------------------------------------------------
        # Navigation - run / sub / event from run-info
        self.run = QtGui.QLineEdit("%d" % -1)      # run
        self.subrun = QtGui.QLineEdit("%d" % -1)      # subrun
        self.event_num = QtGui.QLineEdit("%d" % -1)      # event
        run_label = QtGui.QLabel("run")
        run_label.setFixedWidth(labelwidth)
        event_label = QtGui.QLabel("event")
        event_label.setFixedWidth(labelwidth)
        subrun_label = QtGui.QLabel("subrun")
        subrun_label.setFixedWidth(labelwidth)
        for input in [ self.run, self.subrun, self.event_num, self.event ]:
            input.setFixedWidth( inputwidth )
        
        self._navlayout.addWidget( run_label, 0, 0 )
        self._navlayout.addWidget( subrun_label, 1, 0 )
        self._navlayout.addWidget( event_label, 2, 0 )
        self._navlayout.addWidget( entry_label, 3, 0 )

        self._navlayout.addWidget( self.run, 0, 1 )
        self._navlayout.addWidget( self.subrun, 1, 1 )
        self._navlayout.addWidget( self.event_num, 2, 1 )
        self._navlayout.addWidget( self.event,  3, 1 )

        # select choice options
        self.axis_plot = QtGui.QPushButton("Go/Replot")
        self.previous_plot = QtGui.QPushButton("Prev")
        self.next_plot = QtGui.QPushButton("Next")
        self.goto_entry = QtGui.QPushButton("Goto Entry")
        self.goto_rse   = QtGui.QPushButton("Goto RSE")

        # prev, next, replot
        self._navlayout.addWidget( self.previous_plot, 0, 2, 1, 1 )
        self._navlayout.addWidget( self.next_plot,     0, 3, 1, 1 )
        self._navlayout.addWidget( self.goto_entry,    1, 2, 1, 2 )
        self._navlayout.addWidget( self.goto_rse,      2, 2, 1, 2 )
        self._navlayout.addWidget( self.axis_plot,     3, 2, 1, 2 )

        # [ signal connect ]

        # (Re)Plot button
        self.axis_plot.clicked.connect(self.plotData)

        # Previous and Next event
        self.previous_plot.clicked.connect(self.previousEvent)
        self.next_plot.clicked.connect(self.nextEvent)
        self.goto_entry.clicked.connect(self.gotoEntry)
        self.goto_rse.clicked.connect(self.gotoRSE)

        # set frame
        self._navframe.setLayout( self._navlayout )

    def _makeContrastFrame(self):
        contrast_frame = QtGui.QFrame()
        contrast_frame.setLineWidth(1)
        contrast_frame.setFrameShape( QtGui.QFrame.Box )
        contrast_layout = QtGui.QGridLayout()

        ### use user constrast -- threshold
        #Lock imin/imax between events
        self.user_contrast = QtGui.QCheckBox("User Contrast")
        self.user_contrast.setChecked(False)
        self.user_contrast.clicked.connect(self.enableContrast)
        contrast_layout.addWidget( self.user_contrast, 0, 0, 1, 2 )

        ### imin -- threshold
        self.imin = QtGui.QLineEdit("%d" % (5))
        iminlabel = QtGui.QLabel("imin")
        iminlabel.setFixedWidth(30)
        contrast_layout.addWidget( iminlabel, 1, 0, 1, 1 )
        contrast_layout.addWidget( self.imin, 1, 1, 1, 1 )

        ### imax -- threshold
        self.imax = QtGui.QLineEdit("%d" % (400))
        imaxlabel = QtGui.QLabel("imax")
        imaxlabel.setFixedWidth(30)
        contrast_layout.addWidget( imaxlabel, 2, 0, 1, 1 )
        contrast_layout.addWidget( self.imax, 2, 1, 1, 1 )
        contrast_frame.setLayout( contrast_layout )

        self.enableContrast()
        return contrast_frame

    def _makeImage2Dcontrol(self):
        image_frame = QtGui.QFrame()
        image_frame.setLineWidth(1)
        image_frame.setFrameShape( QtGui.QFrame.Box )
        image_layout = QtGui.QGridLayout()
        
        image_label = QtGui.QLabel( "Image2D panel" )
        image_layout.addWidget(image_label, 0, 0, 1, 4)
        
        # SRC: source image
        image_src_label  = QtGui.QLabel( "SRC" )
        image_src_rlabel = QtGui.QLabel( "R" )
        
        image_src_glabel = QtGui.QLabel( "G" )
        image_src_blabel = QtGui.QLabel( "B" )
        image_src_label.setFixedWidth(30)
        for l in [ image_src_rlabel,image_src_glabel,image_src_blabel]:
            l.setFixedWidth(30)
        self.image_src_producer = QtGui.QComboBox()
        self.image_src_producer.currentIndexChanged.connect( self.setSrcProducerChannels )
        self.image_src_rch = QtGui.QComboBox()
        self.image_src_gch = QtGui.QComboBox()
        self.image_src_bch = QtGui.QComboBox()
        image_layout.addWidget(image_src_label,   1,0,1,1)
        image_layout.addWidget(self.image_src_producer,1,1,1,1)
        image_layout.addWidget(image_src_rlabel,  2,0,1,1)
        image_layout.addWidget(self.image_src_rch,     2,1,1,1)
        image_layout.addWidget(image_src_glabel,  3,0,1,1)
        image_layout.addWidget(self.image_src_gch,     3,1,1,1)
        image_layout.addWidget(image_src_blabel,  4,0,1,1)
        image_layout.addWidget(self.image_src_bch,     4,1,1,1)
        self.src_rgbchs = [self.image_src_rch, self.image_src_gch, self.image_src_bch ]

        # OVRL: source image
        image_ovr_label  = QtGui.QLabel( "OVR" )
        self.image_ovr_rlabel = QtGui.QPushButton( "1" )
        self.image_ovr_rlabel.setStyleSheet( "QPushButton {background-color: #FF0000;}" )
        self.image_ovr_glabel = QtGui.QPushButton( "2" )
        self.image_ovr_glabel.setStyleSheet( "QPushButton {background-color: #00FF00;}" )
        self.image_ovr_blabel = QtGui.QPushButton( "3" )
        self.image_ovr_blabel.setStyleSheet( "QPushButton {background-color: #0000FF;}" )
        image_ovr_label.setFixedWidth(30)
        for l in [ self.image_ovr_rlabel,self.image_ovr_glabel,self.image_ovr_blabel]:
            l.setFixedWidth(20)
            l.setFixedHeight(20)
        self.image_ovr_producer = QtGui.QComboBox()
        self.image_ovr_producer.currentIndexChanged.connect( self.setOvrProducerChannels )
        self.image_ovr_rch = QtGui.QComboBox()
        self.image_ovr_gch = QtGui.QComboBox()
        self.image_ovr_bch = QtGui.QComboBox()
        image_layout.addWidget(image_ovr_label,        1,3,1,1)
        image_layout.addWidget(self.image_ovr_producer,1,2,1,1)
        image_layout.addWidget(self.image_ovr_rlabel,  2,3,1,1)
        image_layout.addWidget(self.image_ovr_rch,     2,2,1,1)
        image_layout.addWidget(self.image_ovr_glabel,       3,3,1,1)
        image_layout.addWidget(self.image_ovr_gch,     3,2,1,1)
        image_layout.addWidget(self.image_ovr_blabel,       4,3,1,1)
        image_layout.addWidget(self.image_ovr_bch,     4,2,1,1)
        # setup color buttons/colors
        self.image_ovr_rlabel.clicked.connect( self.setOvrRcolor )
        self.image_ovr_glabel.clicked.connect( self.setOvrGcolor )
        self.image_ovr_blabel.clicked.connect( self.setOvrBcolor )
        self.ovr_rcolor = QtGui.QColor("#FF0000")
        self.ovr_gcolor = QtGui.QColor("#00FF00")
        self.ovr_bcolor = QtGui.QColor("#0000FF")
        self.ovr_rgbchs = [self.image_ovr_rch, self.image_ovr_gch, self.image_ovr_bch ]
        self.ovr_colors = [self.ovr_rcolor, self.ovr_gcolor, self.ovr_bcolor ]
        
        # Mixture Slider
        self.image_slider = QtGui.QSlider( QtCore.Qt.Horizontal )
        image_layout.addWidget(self.image_slider,5,0,1,4)

        image_frame.setLayout(image_layout)

        # connect buttons to replot
        self.image_src_producer.currentIndexChanged.connect( self.plotData )
        self.image_ovr_producer.currentIndexChanged.connect( self.plotData )
        for ch in self.src_rgbchs:
            ch.currentIndexChanged.connect( self.plotData )
        for ch in self.ovr_rgbchs:
            ch.currentIndexChanged.connect( self.plotData )        
        self.image_slider.sliderReleased.connect( self.plotData )
        
        return image_frame

    def _makeROIpanel(self):

        roipanel = QtGui.QFrame()
        roipanel.setLineWidth(1)
        roipanel.setFrameShape( QtGui.QFrame.Box )

        roipanel_label = QtGui.QLabel("ROI panel")

        self.comboBoxROI = QtGui.QComboBox()
        self.roi_producer = None
        self.roi_exists = False

        # BNB
        self.kBNB = QtGui.QRadioButton("BNB")
        self.kBNB.setChecked(True)

        # Particle
        self.kOTHER = QtGui.QRadioButton("Particle")
        
        # Yes or no to draw ROI (must hit replot)
        self.draw_bbox = QtGui.QCheckBox("Draw ROI")
        self.draw_bbox.setChecked(True)

        roipanel_layout = QtGui.QGridLayout()
        roipanel_layout.addWidget( roipanel_label,   0, 0, 1, 1 )
        roipanel_layout.addWidget( self.comboBoxROI, 1, 0, 1, 1 )
        roipanel_layout.addWidget( self.kBNB,        2, 0, 1, 1 )
        roipanel_layout.addWidget( self.kOTHER,      3, 0, 1, 1 )
        roipanel_layout.addWidget( self.draw_bbox,   4, 0, 1, 1 )
        
        roipanel.setLayout( roipanel_layout )

        return roipanel

    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # User Item Handling

    def _makeUserItemTreeFrame(self):
        user_frame = QtGui.QFrame()
        user_frame.setLineWidth(1)
        user_frame.setFrameShape( QtGui.QFrame.Box )
        user_layout = QtGui.QGridLayout()

        self.user_items = pg.TreeWidget()
        self.user_items.setColumnCount(2)
        user_layout.addWidget( QtGui.QLabel("user items"), 0, 0 )
        user_layout.addWidget( self.user_items, 1, 0 )
        user_frame.setLayout( user_layout )
        return user_frame

    def addUserVisItem(self,name,visitem):
        self.user_plot_items[name] = visitem
        # make checkbox for parent user item
        self.user_plot_checkboxes[name] = QtGui.QCheckBox('')
        self.map_user_checkboxes2name[self.user_plot_checkboxes[name]] = name # provide a way to map back
        self.user_plot_checkboxes[name].setChecked(False)
        self.user_plot_checkboxes[name].stateChanged.connect( self.parentUserItemCheckBoxChanged )
        if type(visitem) is list:
            # multiple sub-objects!
            self.user_subitem_cbxs[name] = []
            for ix,subitem in enumerate(visitem):
                self.user_subitem_cbxs[name].append( QtGui.QCheckBox('') )
                self.user_subitem_cbxs[name][ix].setChecked(False)
            
        item = pg.TreeWidgetItem(['',name])
        item.setWidget(0,self.user_plot_checkboxes[name])
        self.user_items.addTopLevelItem( item )

        if type(visitem) is list:
            for ix in range(0,len(visitem)):
                subitem = pg.TreeWidgetItem([name+"_%d"%(ix)])
                item.addChild(subitem)
                self.user_items.setItemWidget( subitem, 1, self.user_subitem_cbxs[name][ix] )

        
    def clearUserVisItems(self):
        self.user_items.clear()
        self.user_plot_item = {}
        self.user_plot_checkboxes = {}
        self.user_subitem_cbxs = {}
        self.map_user_checkboxes2name = {}

    def drawUserItems(self):
        meta = self.image.imgs[0].meta()
        dw_i = meta.pixel_width()
        dh_i = meta.pixel_height()
        for name,visitem in self.user_plot_items.items():

            if type(visitem) is not list and not self.user_plot_checkboxes[name].isChecked():
                continue
            print "RGB drawing user item: ",name
            visitems = visitem
            if type(visitems) is not list:
                visitems = [visitem]

            for idx,item in enumerate(visitems):
                if name in self.user_subitem_cbxs:
                    # if we have subitems, we check to not plot it
                    if self.user_subitem_cbxs[name][idx].isChecked()==False:
                        continue
                if not isinstance(item,pg.PlotDataItem):
                    print "EGB display does not support this type for visualzation: ",type(item)
                    continue
                # we need to convert positions into image coorindates

                if not hasattr(item,"pylardconverted"):
                    xy = item.getData()
                    npts = len(xy[0])
                    xarr = np.zeros( len(xy[0]) )
                    yarr = np.zeros( len(xy[1]) )
                    print "converted data: ",len(xarr),len(yarr)

                    for i in xrange(0,npts):
                        x = (xy[0][i]-meta.min_x())/dw_i
                        y = (xy[1][i]-meta.min_y())/dh_i
                        xarr[i] = x
                        yarr[i] = y
                    item.pylardconverted = True                    
                    item.setData(x=xarr,y=yarr)

                self.plt.addItem(item)
                

    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # Color buttons
    
    def setOvrRcolor(self):
        self.ovr_rcolor = QtGui.QColorDialog.getColor()
        self.image_ovr_rlabel.setStyleSheet("QPushButton { background-color: %s; };"%(self.ovr_rcolor.name()))
    def setOvrGcolor(self):
        self.ovr_gcolor = QtGui.QColorDialog.getColor()
        self.image_ovr_glabel.setStyleSheet("QPushButton { background-color: %s; };"%(self.ovr_gcolor.name()))
    def setOvrBcolor(self):
        self.ovr_bcolor = QtGui.QColorDialog.getColor()
        self.image_ovr_blabel.setStyleSheet("QPushButton { background-color: %s; };"%(self.ovr_bcolor.name()))

    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # image2d options
    
    def addImage2Ddata(self,image2d):
        """ add image set to display """
        # once received we must
        # 1) update list of producer options in src and overlay
        # 2) (implicit) once src and overlay set, then default RGB channel options must be set
        # 3) make viewing copies of images and put it into the screen
        if not issubclass(image2d,TPCdataPlottable) and type(image2d) is not TPCdataPlottable:
            print "Error, image2d data given to rgbdisplay must be inherited from TPCdataPlottable"
            return
        # put into store
        self.images[image2d.producer] = image2d
        # update list of producers
        self.updateProducerList()
        self.setSrcProducerChannels()
        self.setOvrProducerChannels()
        
    def clearImage2Ddata(self):
        self.images = {}

    def updateProducerList(self):
        # we silence the redraws until updated
        self.image_src_producer.blockSignals(True)
        self.image_ovr_producer.blockSignals(True)

        self.image_src_producer.clear()
        producers = self.images.keys()
        producers.sort()
        print producers
        for i,producer in enumerate(producers):
            self.image_src_producer.insertItem(i,producer)

        self.image_ovr_producer.clear()
        for i,producer in enumerate(producers):
            self.image_ovr_producer.insertItem(i,producer)

        # reactivate
        self.image_src_producer.blockSignals(False)
        self.image_ovr_producer.blockSignals(False)


    def setSrcProducerChannels(self):
        # we silence the redraws until updated
        self.image_src_producer.blockSignals(True)
        for ch in self.src_rgbchs:
            ch.blockSignals(True)
        producer = str(self.image_src_producer.currentText())
        image2d = self.images[producer]
        nimgchs = len(image2d.imgs)
        # set the default RGB channels
        for ich,rgbch in enumerate(self.src_rgbchannels):
            rgbch.clear()
            for idx,ch in enumerate(image2d.imgs):
                rgbch.insertItem( idx, str(idx) )
            rgbch.insertItem(len(image2d.imgs),"(none)")
            if ich<len(image2d.imgs):
                rgbch.setCurrentIndex(ich)
            else:
                rgbch.setCurrentIndex(len(image2d.imgs))

        # reactivate
        self.image_src_producer.blockSignals(False)
        for ch in self.src_rgbchs:
            ch.blockSignals(False)


    def setOvrProducerChannels(self):
        # we silence the redraws until updated
        self.image_ovr_producer.blockSignals(True)
        for ch in self.ovr_rgbchs:
            ch.blockSignals(True)
        
        producer = str(self.image_ovr_producer.currentText())
        image2d = self.images[producer]
        nimgchs = len(image2d.imgs)
        # set the default RGB channels
        for ich,rgbch in enumerate(self.ovr_rgbchannels):
            rgbch.clear()
            for idx,ch in enumerate(image2d.imgs):
                rgbch.insertItem( idx, str(idx) )
            rgbch.insertItem(len(image2d.imgs),"(none)")
            if ich<len(image2d.imgs):
                rgbch.setCurrentIndex(ich)
            else:
                rgbch.setCurrentIndex(len(image2d.imgs))

        # reactivate
        self.image_ovr_producer.blockSignals(False)
        for ch in self.ovr_rgbchs:
            ch.blockSignals(False)

    def getSrcProducer(self):
        return str(self.image_src_producer.currentText())

    def getOvrProducer(self):
        return str(self.image_ovr_producer.currentText())

    def getSrcChannels(self):
        views = []
        for rgbch in self.src_rgbchs:
            if rgbch.currentText()!="(none)":
                views.append( int(rgbch.currentText()) )
            else:
                views.append(-1)
        return views

    def getOvrChannels(self):
        views = []
        for rgbch in self.ovr_rgbchs:
            if rgbch.currentText()!="(none)":
                views.append( int(rgbch.currentText()) )
            else:
                views.append(-1)
        return views

    # -----------------------------------------------------------------
    # -----------------------------------------------------------------
    # MainWindow Interface

    def addVisItem( self, name, visitem ):
        if type(visitem) is TPCdataPlottable or isinstance(visitem,TPCdataPlottable):
            print "RGBdisplay received Image2D item"
            self.addImage2Ddata(visitem)
        else:
            print "RGBdisplay recieved user item name=",name," type=",type(visitem)
            self.addUserVisItem(name,visitem)
        return True
    
    
