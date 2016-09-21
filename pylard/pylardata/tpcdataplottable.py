from pylard.pylardata.plotimage import PlotImage
import numpy as np

class TPCdataPlottable(PlotImage):
    """ thanks vic. """
    def __init__(self, producer, img_v, roi_v, planes):
        super(TPCdataPlottable, self).__init__(img_v, roi_v, planes)
        self.name = "TPCdataPlottable"
        self.producer = producer

    def __caffe_copy_image__(self):
        return self.work_mat.copy()
