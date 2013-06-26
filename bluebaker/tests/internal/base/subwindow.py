from PySide.QtCore import Qt
from PySide.QtGui import QVBoxLayout

from bluebaker.tests.base import TestCase
from bluebaker.base.subwindow import Window
from bluebaker.base.binder import Binder
from bluebaker.base.controller import Controller
from bluebaker.app import Application


class ExampleController(Controller):

    def action(self):
        pass


class ExampleBinder(Binder):

    def create_controller(self):
        return ExampleController()


class LayoutMock(object):

    def __init__(self):
        self.layouts = []

    def addLayout(self, layout):
        self.layouts.append(layout)


class ParentMock(object):

    def __init__(self):
        self._removeWindow = False

    def removeWindow(self, window):
        self._removeWindow = window


class MainWindowMock(object):

    def __init__(self, is_opened):
        self.is_opened = is_opened
        self._setFocus = False
        self._openWindow = False

    def isOpened(self, window):
        return self.is_opened

    def getWindow(self, _id):
        return self

    def setFocus(self):
        self._setFocus = True

    def openWindow(self, window):
        self._openWindow = True


class ExampleWindow(Window):

    def __init__(self, *args, **kwargs):
        self._layout = LayoutMock()
        self._opened = False
        super(ExampleWindow, self).__init__(*args, **kwargs)

    def get_binder(self):
        return ExampleBinder

    def layout(self):
        return self._layout

    def opened(self):
        self._opened = True


class WindowTest(TestCase):

    def test_init(self):
        window = ExampleWindow()
        self.assertTrue(window.testAttribute(Qt.WA_DeleteOnClose))
        self.assertEqual(200, window.minimumWidth())
        self.assertEqual(QVBoxLayout, type(window.mainLayout))
        self.assertEqual([window.mainLayout], window.layout().layouts)
        self.assertEqual(ExampleBinder, type(window.binder))

    def test_set_parent(self):
        window = ExampleWindow()
        window.setParent(15)
        self.assertEqual(15, window._parent)

    def test_show(self):
        window = ExampleWindow()
        window.show()
        self.assertTrue(window._opened)

    def test_close(self):
        parent = ParentMock()
        window = ExampleWindow()
        window.setParent(parent)
        window.close()
        self.assertEqual(window, parent._removeWindow)

    def test_id(self):
        window = ExampleWindow()
        self.assertEqual(ExampleBinder().get_id(), window.id)

    def test_open_with_opened_window(self):
        Application().main = MainWindowMock(True)
        ExampleWindow.open('action')

        self.assertTrue(Application().main._setFocus)
        self.assertFalse(Application().main._openWindow)

    def test_open_without_opened_window(self):
        Application().main = MainWindowMock(False)
        ExampleWindow.open('action')

        self.assertFalse(Application().main._setFocus)
        self.assertTrue(Application().main._openWindow)
