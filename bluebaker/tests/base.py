import unittest
from mock import patch

from bluebaker.log import data
from bluebaker.tests.mocker import BinderMockup


class TestCaseType(type):

    def __init__(cls, name, bases, dct):
        super(TestCaseType, cls).__init__(name, bases, dct)
        fullname = '.'.join([str(dct['__module__']), name])
        if 'base' not in dct or dct['base'] == False:
            keys = TestCase.alltests_dict.keys()
            if fullname in keys:
                raise RuntimeError(
                    'Name "%s" defined more the once.' % (name,))
            if name in keys:
                TestCase.alltests_dict[name] = None
            else:
                TestCase.alltests_dict[name] = cls
            TestCase.alltests.append(cls)
            TestCase.alltests_dict[fullname] = cls


class TestCase(unittest.TestCase):

    __metaclass__ = TestCaseType
    base = True
    alltests = []
    alltests_dict = {}

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self.log = data['log']

    def setUp(self):
        self.log.clear()
        self.data = {}

    def generateMock(self, name, clsmethod=False, return_fun=None):
        def mock(*args, **kwargs):
            self.data[name].append(list(args) + [kwargs])
            if return_fun:
                return return_fun(name, *args, **kwargs)
        self.data[name] = []
        if clsmethod:
            return name, classmethod(mock)
        else:
            return name, mock

    def getMock(self, name):
        return self.data[name].pop(0)

    def assertMock(self, name, *args, **kwargs):
        exptected_data = list(args) + [kwargs]
        self.assertEqual(exptected_data, self.getMock(name))

    def tearDown(self):
        if self.currentResult.wasSuccessful():
            for key, mock in self.data.items():
                if len(mock) > 0:
                    raise RuntimeError('Not all mocks were asserted!')

    def patch(self, obj, *args, **kwargs):
        return patch.object(obj, *self.generateMock(*args, **kwargs))

    def assertType(self, type_, obj):
        self.assertEqual(type_, type(obj))

    def run(self, result=None):
        self.currentResult = result # remember result for use in tearDown
        unittest.TestCase.run(self, result) # call superclass run method


class ControllerTest(TestCase):

    def setUp(self):
        super(ControllerTest, self).setUp()
        self.ctrl = self.controller()
        self.signal_number = 0

    def tearDown(self):
        super(ControllerTest, self).tearDown()
        if self.signal_number != len(self.ctrl.signals + self.ctrl.signals_end):
            raise RuntimeError('Not all signal were asserted!')

    def action(self, *args, **kwargs):
        return self.ctrl.do_action(*args, **kwargs)

    def get_signal(self, index):
        signals = self.ctrl.signals + self.ctrl.signals_end
        return signals[index]

    def next_signal(self):
        signal = self.get_signal(self.signal_number)
        self.signal_number += 1
        return signal

    def assert_signal(self, signal, view_name, signal_name):
        self.assertEqual(signal_name, signal.name)
        self.assertEqual(view_name, signal.view_name)
        self.assertEqual(view_name, signal.view_name)
        return signal.args

    def assert_signal_with_args(self, signal, view_name, signal_name, *args, **kwargs):
        self.assert_signal(signal, view_name, signal_name)
        self.assertEqual((args, kwargs), signal.args)

    def assert_next_signal(self, *args, **kwargs):
        signal = self.next_signal()
        return self.assert_signal(signal, *args, **kwargs)

    def assert_next_signal_with_args(self, *args, **kwargs):
        signal = self.next_signal()
        return self.assert_signal_with_args(signal, *args, **kwargs)


class ViewTest(TestCase):

    def setUp(self):
        super(ViewTest, self).setUp()
        self.binder = BinderMockup(self)
        self.view = self.viewcls(self.binder)


class BinderTest(TestCase):

    def setUp(self):
        super(BinderTest, self).setUp()
        self.binder = self.bindercls()


class WindowTest(TestCase):

    def setUp(self):
        super(WindowTest, self).setUp()
        self.window = self.windowcls()


class FormTest(TestCase):

    def setUp(self):
        super(FormTest, self).setUp()
        self.form = self.formcls()
