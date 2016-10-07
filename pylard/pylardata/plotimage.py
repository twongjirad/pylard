from larcv import larcv
import numpy as np

import abc


class PlotImage(object):
    __metaclass__ = abc.ABCMeta

    # notes
    # work_mat is the ndarray representation of image2d data
    # orig is the 3 channels we will manipulate on the screen
    # plot_mat is modified to have overlays
    # when loading, we manip orig_mat to have the orientation we want
    # before going to caffe, __revert_image__ is called to rearrange the image
    
    def __init__(self, img_v, roi_v, planes):
        print "PlotImage class being made. Nchannels= ",img_v.size()

        # list of image2d objects
        self.imgs = [img_v[i] for i in xrange(img_v.size())]

        if roi_v is not None:
            self.roi_v = [roi_v[i] for i in xrange(roi_v.size())]

        # list of channels to go into views. default to 0,1,2 (or less)
        if img_v.size()>=3:
            self.views  = [0,1,2]
        else:
            self.views = [ x for x in xrange(img_v.size()) ]
            for i in xrange(img_v.size(),3):
                self.views.append(-1)
        print "init views: ",self.views

        # pyqtgraph sucks I have to make a union of all the images
        ometa = None
        comp_x,comp_y = (1,1)
        for img in self.imgs:
            if ometa == None:
                ometa  = larcv.ImageMeta(img.meta())
                comp_x = ometa.width() / ometa.cols()
                comp_y = ometa.height() / ometa.rows()
            else:
                ometa = ometa.inclusive(img.meta())

        tmp_img_v = []
        for i in xrange(len(self.imgs)):
            meta = larcv.ImageMeta(ometa.cols() * comp_x, ometa.rows() * comp_y,
                                   ometa.rows(), ometa.cols(),
                                   ometa.min_x(), ometa.max_y(), i)
            img = larcv.Image2D(meta)
            img.paint(0.)
            img.overlay(self.imgs[i])
            tmp_img_v.append(img)

        # img_v should never change
        self.imgs = tmp_img_v
        self.img_v = [larcv.as_ndarray(img) for img in tmp_img_v]

        # self.orig_mat is always 3 in ch dim: RGB
        if len(self.img_v)>0:
            #self.orig_mat = np.zeros(list(self.img_v[0].shape) + [3])
            matshape = list(self.img_v[0].shape)+[3]
        else:
            matshape = [10,10,3]
        self.orig_mat = np.zeros( matshape )
        print "ORIG MAT: ",self.orig_mat.shape

        # self.work_mat is N images in a matrix, we store our manipulations of
        # orig_mat here and exchange them when we change the channel number 
        #self.work_mat = np.zeros(list(self.img_v[0].shape) + [len(self.img_v)])
        if len(self.img_v)>0:
            workshape = list(self.img_v[0].shape) + [len(self.img_v)]
        else:
            workshape = [10,10,3]
        self.work_mat = np.zeros( workshape )
        print "WORK MAT: ",self.work_mat.shape


        # min and max of orig_mat
        self.iimin = 0.0
        self.iimax = 256.0
        
        # create orig_mat and work_mat for the first time i put 2 underlines
        # before to make sure I only call this method internally. __XX__ style is for
        # ABC
        self.__create_mat()

        # list of the ROIs or bounding boxes we will see on the screen
        self.rois = []

        # deprecated I think
        self.reverted = False

    def __create_mat(self):

        # load all the images into working matrix
        for ix, img in enumerate(self.img_v):
            self.work_mat[:, :, ix] = self.img_v[ix]

        # put only the selected ones from work_mat into orig_mat
        for p, ch in enumerate(self.views):
            if ch != -1: 
                self.orig_mat[:, :, p] = self.work_mat[:, :, ch]
            else:
                self.orig_mat[:, :, p] = np.zeros((self.orig_mat.shape[0], self.orig_mat.shape[1]))

        # pyqtgraph quirk -- flip the middle axis so it's displayed upright for now
        # we have to keep this standard between all Image2D i'm sorry!
        self.work_mat = self.work_mat[:,::-1,:]
        self.orig_mat = self.orig_mat[:,::-1,:]


    def set_imin_imax(self):
        self.iimin = np.min(self.orig_mat)
        self.iimax = np.max(self.orig_mat)
        
    # do you want to make any changes to work_mat before it goes to caffe? If not just return a
    # copy of work_mat
    @abc.abstractmethod
    def __caffe_copy_image__(self):
       """make a copy of work_mat, and do something to it so that it matches"""
       """the way training was done, for most images this means in the subclass"""
       """just return self.work_mat.copy(), in some cases you may want to transpose"""
       """as in the case of the 12 channel image"""


    # apply thresholding for contrast and make sure RGB pixels do not overlap
    def set_plot_mat(self,imin,imax,views=None):
        if len(views)!=3:
            raise ValueError("Number of views/channels is not 3. should be list of 3.")

        if views is not None:
            self.views = views

        self.plot_mat = np.zeros( self.orig_mat.shape )
        for i,ch in enumerate(self.views):
            if ch>=0 and ch<len(self.img_v):
                self.plot_mat[:,:,i] = self.work_mat[:,:,ch]

        # do contrast thresholding
        self.plot_mat[self.plot_mat < imin] = 0
        self.plot_mat[self.plot_mat > imax] = imax

        # make sure pixels do not block each other
        self.plot_mat[:, :, 0][self.plot_mat[:, :, 1] > 0.0] = 0.0
        self.plot_mat[:, :, 0][self.plot_mat[:, :, 2] > 0.0] = 0.0
        self.plot_mat[:, :, 1][self.plot_mat[:, :, 2] > 0.0] = 0.0

        return self.plot_mat

    # take what's in orig_mat and put it in work_mat
    def __store_orig_mat(self):
         # store the current state of the orig_mat into the working matrix
        for p, ch in enumerate(self.views):
            if ch != -1:
                self.work_mat[:, :, ch] = self.orig_mat[:, :, p]  # don't put a blank in there

    # swap channels that are shown
    def swap_plot_mat(self,imin,imax,newchs):

        print "swap channels to: ", newchs

        # store the original matrix into the working matrix
        self.__store_orig_mat()

        # swap the planes
        self.views = newchs
        
        # put work mat values into orig_mat
        for p, ch in enumerate(self.views):
            if ch != -1:
                self.orig_mat[:, :, p] = self.work_mat[:, :, ch]
            else:
                self.orig_mat[:, :, p] = np.zeros((self.orig_mat.shape[0], self.orig_mat.shape[1]))

        # make the viewing plot_mat and return
        return self.set_plot_mat(imin, imax)

    # create the ROIs if they exists and return them
    def parse_rois(self):

        # loop over larcv::ROI
        for ix, roi in enumerate(self.roi_v):

            # how many bbox are there?
            nbb = roi.BB().size()

            if nbb == 0:  # there was no ROI continue...
                continue
            
            r = {}

            # particle type
            r['type'] = roi.Type()

            # the bounding boxes
            r['bbox'] = []

            for iy in xrange(nbb):
                bb = roi.BB()[iy]
                r['bbox'].append(bb)

            self.rois.append(r)

        return self.rois

    # internal method to make the copy of work_mat[...]
    def __caffe_copy_image(self):
        assert self.reverted == True
        return self.__caffe_copy_image__()

    # revert the image, flip operation on the second dimension
    def revert_image(self):
        self.work_mat = self.work_mat[:,::-1,:]
        self.orig_mat = self.orig_mat[:,::-1,:]
        self.reverted = True

    # insert thresholded image into self.img_v 
    def emplace_image(self):

        # original mat may have changed, lets store it 
        self.__store_orig_mat()

        # get the image for caffe
        self.caffe_image = self.__caffe_copy_image()

    # reset the presets if there are any in this product
    def reset_presets(self):
        for key,val in self.presets.iteritems():
            self.preset_layout.removeWidget(val)
            val.setParent(None)
        self.presets = {}

    def nchannels(self):
        return len(self.imgs)
