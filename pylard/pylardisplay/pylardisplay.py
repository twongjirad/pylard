from pylard.pylardisplay.mainwindow import mainwindow
from pyqtgraph.Qt import QtGui

def run():
    app = QtGui.QApplication([])
    mw = mainwindow()
    app.exec_()


if __name__ == "__main__":
    run()
