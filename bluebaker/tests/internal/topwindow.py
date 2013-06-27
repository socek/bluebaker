from mock import patch, MagicMock
from PySide.QtGui import QMdiArea, QMenuBar, QStatusBar

from bluebaker.topwindow import TopWindow
from bluebaker.tests.base import TestCase
from bluebaker.singleton import Singleton


class SubWindowMock(object):
    _ids = 0

    def __init__(self):
        self.parent = None
        self._show = False
        SubWindowMock._ids += 1
        self.id = SubWindowMock._ids

    def setParent(self, parent):
        self.parent = parent

    def show(self):
        self._show = True


class ApplicationMock(object):

    def __init__(self):
        self._close = False

    def close(self):
        self._close = True


class TopWindowTest(TestCase):

    def setUp(self):
        super(TopWindowTest, self).setUp()
        self.window = TopWindow()

    def test_init(self):
        self.assertEqual('Finlog', self.window.windowTitle())
        self.assertEqual(400, self.window.minimumSize().width())
        self.assertEqual(600, self.window.minimumSize().height())
        self.assertEqual([], self.window.subWindows)
        self.assertEqual(QMdiArea, type(self.window._mdi_area))
        self.assertEqual(self.window._mdi_area, self.window.centralWidget())
        self.assertEqual(QMenuBar, type(self.window.menuBar()))
        self.assertEqual(QStatusBar, type(self.window.status))
        self.assertEqual(self.window.status, self.window.statusBar())

    def test_openWindow(self):
        subwindow = SubWindowMock()
        with patch.object(self.window._mdi_area, *self.generateMock('addSubWindow')):
            self.window.openWindow(subwindow)

        self.assertMock('addSubWindow', subwindow)
        self.assertEqual(self.window, subwindow.parent)
        self.assertTrue(subwindow._show)

    def test_subWindowsIds(self):
        subWindow1 = SubWindowMock()
        subWindow2 = SubWindowMock()
        subWindow3 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)
            self.window.openWindow(subWindow2)
            self.window.openWindow(subWindow3)

        id_list = self.window.subWindowsIds()
        expected_data = [subWindow1.id, subWindow2.id, subWindow3.id]
        self.assertEqual(expected_data, id_list)

    def test_isOpened_true(self):
        subWindow1 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertTrue(self.window.isOpened(subWindow1))

    def test_isOpened_false(self):
        subWindow1 = SubWindowMock()
        subWindow2 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertFalse(self.window.isOpened(subWindow2))

    def test_isOpenedId_true(self):
        subWindow1 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertTrue(self.window.isOpenedId(subWindow1.id))

    def test_isOpenedId_false(self):
        subWindow1 = SubWindowMock()
        subWindow2 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertFalse(self.window.isOpenedId(subWindow2.id))

    def test_getWindow_success(self):
        subWindow1 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertEqual(subWindow1, self.window.getWindow(subWindow1.id))

    def test_getWindow_fail(self):
        subWindow1 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.assertEqual(None, self.window.getWindow('fake_id'))

    def test_removeWindow_success(self):
        subWindow1 = SubWindowMock()
        subWindow2 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)
            self.window.openWindow(subWindow2)

        self.window.removeWindow(subWindow1)
        self.assertFalse(self.window.isOpened(subWindow1))

    def test_removeWindow_fail(self):
        subWindow1 = SubWindowMock()
        subWindow2 = SubWindowMock()
        with patch.object(self.window._mdi_area, 'addSubWindow'):
            self.window.openWindow(subWindow1)

        self.window.removeWindow(subWindow2)
        self.assertFalse(self.window.isOpened(subWindow2))

    def test_closeEvent(self):
        app = ApplicationMock()
        with patch.object(Singleton, '__call__', lambda x: app):
            self.assertRaises(TypeError, self.window.closeEvent, MagicMock())
        self.assertTrue(app._close)
