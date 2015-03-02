from pylard.pylardisplay.mainwindow import mainwindow
from pyqtgraph.Qt import QtGui

def run_daefile(daefile):
    app = QtGui.QApplication([])
    mw = mainwindow(daefile)
    app.exec_()


if __name__ == "__main__":
    pass
