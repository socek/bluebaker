from mock import patch, MagicMock

from PySide.QtCore import QSize
import venusian

from bluebaker.tests.base import TestCase
from bluebaker.base.binder import Binder, add_view, get_module_name
from bluebaker.base.controller import Controller
from bluebaker.app import Application


class ParentMock(object):

    def __init__(self):
        self.size = (50, 50)
        self._close = False

    def sizeHint(self):
        return QSize(100, 100)

    def width(self):
        return self.size[0]

    def height(self):
        return self.size[1]

    def resize(self, sizeHint):
        self.sizeHint = sizeHint

    def close(self):
        self._close = True


class MainWindowMock(object):

    def __init__(self, binder):
        self.binder = binder

    def getWindow(self, _id):
        if self.binder:
            return self
        else:
            return False


class ExampleControler(Controller):

    def list(self):
        self.add_binder_signal('list')


class BinderExample(Binder):

    def __init__(self):
        super(BinderExample, self).__init__()
        self._parent = ParentMock()
        self.views = {}
        self._list = False

    def create_controller(self):
        return ExampleControler()

    def list(self):
        self._list = True

    def generate_signals(self):
        super(BinderExample, self).generate_signals()
        self.add_signal(self.list)

    def make_controller_action(self, *args, **kwargs):
        return super(Binder, self).make_controller_action(*args, **kwargs)


class BaseBinder_update_sizeTest(TestCase):

    def test_current_size_is_smaller(self):
        binder = BinderExample()
        binder.update_size()

        self.assertEqual(100, binder._parent.sizeHint.width())
        self.assertEqual(100, binder._parent.sizeHint.height())

    def test_current_size_is_bigger(self):
        binder = BinderExample()
        binder._parent.size = (200, 200)
        binder.update_size()

        self.assertEqual(200, binder._parent.sizeHint.width())
        self.assertEqual(200, binder._parent.sizeHint.height())

    def test_current_window_is_widder(self):
        binder = BinderExample()
        binder._parent.size = (200, 50)
        binder.update_size()

        self.assertEqual(200, binder._parent.sizeHint.width())
        self.assertEqual(100, binder._parent.sizeHint.height())

    def test_current_window_is_higher(self):
        binder = BinderExample()
        binder._parent.size = (50, 200)
        binder.update_size()

        self.assertEqual(100, binder._parent.sizeHint.width())
        self.assertEqual(200, binder._parent.sizeHint.height())


class BaseBinderTest(TestCase):

    def test_hide_all(self):
        binder = BinderExample()

        with patch.object(binder, *self.generateMock('update_size')):
            binder.hide_all().join()

        self.assertMock('update_size')

    def test_set_status(self):
        binder = BinderExample()
        Application().settings = {
            'top window title': 'my top window title',
        }
        Application().createTopWindow()

        with patch.object(Application().main.status,
                          *self.generateMock('showMessage')):
            binder.set_status('text', 10)

            del Application().main
        self.assertMock('showMessage', 'text', 10)

    def test_generate_signals(self):
        binder = BinderExample()

        with patch.object(binder, *self.generateMock('add_signal')):
            binder.generate_signals()

        self.assertMock('add_signal', binder.hide_all)
        self.assertMock('add_signal', binder.update_size)
        self.assertMock('add_signal', binder.set_status)
        self.assertMock('add_signal', binder.set_id)
        self.assertMock('add_signal', binder.close)
        self.assertMock('add_signal', binder.update_list)
        self.assertMock('add_signal', binder.list)

    def test_add_view(self):
        with patch.object(venusian, 'attach') as attach:
            add_view({'wrapped': True})
            attach.assert_called_once()
            args = attach.call_args

        self.assertEqual({'wrapped': True}, args[0][0])
        self.assertEqual('views', args[1]['category'])

        callback = args[0][1]
        obj = MagicMock()
        scanner = MagicMock()
        scanner.binder = obj
        callback(scanner, 'name', obj)
        obj.add_view.assert_called_once(obj)

    def test_set_id(self):
        binder = BinderExample()
        binder.set_id('value')

        self.assertEqual('value', binder._id)

    def test_close(self):
        binder = BinderExample()
        binder.close()

        self.assertTrue(binder._parent._close)

    def test_update_list(self):
        binder = BinderExample()
        Application().main = None
        with patch.object(Application(), 'main', MainWindowMock(binder)):
            binder.update_list()

        self.assertTrue(binder._list)

    def test_update_list_when_no_window(self):
        binder = BinderExample()
        Application().main = None
        with patch.object(Application(), 'main', MainWindowMock(False)):
            binder.update_list()

        self.assertFalse(binder._list)

    def test_get_module_name(self):
        self.assertEqual(
            'bluebaker.tests.internal.base', get_module_name(self))
