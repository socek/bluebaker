from mock import patch, MagicMock
from PySide.QtGui import QMdiArea, QMenuBar, QStatusBar

from bluebaker.topwindow import TopWindow
from bluebaker.tests.base import TestCase


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
        self.parent = MagicMock()
        self.window = TopWindow(self.parent)

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
        self.assertEqual(self.parent, self.window._parent)

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

    @patch('bluebaker.topwindow.super')
    def test_closeEvent(self, super_mock):
        with patch.object(self.window, '_parent') as parent_mock:
            event = MagicMock()
            result = self.window.closeEvent(event)

            parent_mock.close.assert_called_once_with()
            super_mock.assert_called_once_with(TopWindow, self.window)
            super_mock.return_value.closeEvent.assert_called_once_with(event)
            self.assertEqual(
                super_mock.return_value.closeEvent.return_value, result)
