# -*- encoding: utf-8 -*-
from PySide import QtGui

from bluebaker.app import Application
from bluebaker.topwindow.menugenerator import TopMenuGenerator


class TopWindow(QtGui.QMainWindow):

    def __init__(self):
        super(TopWindow, self).__init__()

        def createWindow():
            self.setWindowTitle(u'Finlog')
            self.setMinimumSize(400, 600)
            self.subWindows = []

        def createMainLayout():
            self._mdi_area = QtGui.QMdiArea()
            self.setCentralWidget(self._mdi_area)

        def createMenu():
            TopMenuGenerator(self)

        def createSatusBar():
            self.status = QtGui.QStatusBar(self)
            self.setStatusBar(self.status)

        createWindow()
        createMainLayout()
        createMenu()
        createSatusBar()

    def openWindow(self, window):
        self.subWindows.append(window)
        window.setParent(self)
        self._mdi_area.addSubWindow(window)
        window.show()
        return window

    def subWindowsIds(self):
        return [window.id for window in self.subWindows]

    def isOpened(self, window):
        return self.isOpenedId(window.id)

    def isOpenedId(self, _id):
        return _id in self.subWindowsIds()

    def getWindow(self, _id):
        for window in self.subWindows:
            if window.id == _id:
                return window

    def removeWindow(self, window):
        if self.isOpened(window):
            self.subWindows.remove(window)

    def closeEvent(self, event):
        Application().close()
        return super(TopWindow, self).closeEvent(event)
