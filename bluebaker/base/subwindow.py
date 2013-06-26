# -*- encoding: utf-8 -*-
from PySide import QtGui, QtCore
from bluebaker.app import Application


class Window(QtGui.QMdiSubWindow):

    def __init__(self):
        def initWindow():
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.setWindowFlags((self.windowFlags() | QtCore.Qt.CustomizeWindowHint) &
                                ~QtCore.Qt.WindowMaximizeButtonHint & ~QtCore.Qt.WindowMinimizeButtonHint)
            self.setMinimumWidth(200)

        def createMainLayot():
            self.mainLayout = QtGui.QVBoxLayout()
            self.mainLayout.setContentsMargins(0, 0, 0, 0)
            self.mainLayout.setAlignment(QtCore.Qt.AlignTop)
            self.layout().addLayout(self.mainLayout)

        def createBinder():
            self.binder = self.get_binder()(self)
            self.mainLayout.addWidget(self.binder)

        super(Window, self).__init__()
        initWindow()
        createMainLayot()
        createBinder()

    def setParent(self, parent):
        self._parent = parent

    def opened(self):
        pass  # pragma: no cover

    def show(self):
        super(Window, self).show()
        self.opened()

    def closeEvent(self, *args, **kwargs):
        self._parent.removeWindow(self)
        return super(Window, self).closeEvent(*args, **kwargs)

    @property
    def id(self):
        return self.binder.get_id()

    @classmethod
    def open(cls, action, *args, **kwargs):
        window = cls()
        window.binder.make_controller_action(action, *args, **kwargs)
        if Application().main.isOpened(window):
            Application().main.getWindow(window.id).setFocus()
        else:
            Application().main.openWindow(window)
