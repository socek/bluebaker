from mock import patch
import logging

import bluebaker
from bluebaker.tests.base import TestCase
from bluebaker.tests.mocker import ClassMockup
from bluebaker import log
from bluebaker.app import Application


class LogMock(ClassMockup):

    def __init__(self, test):
        super(LogMock, self).__init__(test)
        self.add_method('addHandler')
        self.add_method('setLevel')


class TestLogClassTest(TestCase):

    def test_info(self):
        log.info('test1')
        with self.log.tester(self, 'info') as loger:
            loger.assertLog('test1')

    def test_warning(self):
        log.warning('test2')
        with self.log.tester(self, 'warning') as loger:
            loger.assertLog('test2')

    def test_debug(self):
        Application().set_main_module(bluebaker, None)
        log.debug('test3')
        with self.log.tester(self, 'debug') as loger:
            # number in the line belowe should be the line number of the
            # "log.debug" line
            loger.assertLog('./tests/internal/log.py:33 test3')

    def test_error(self):
        log.error('test4')
        with self.log.tester(self, 'warning') as loger:
            loger.assertLog('test4')

    def test_start_file_logging(self):
        path = '/tmp/something.log'
        log_mock = LogMock(self)
        with patch.dict(log.data, {'log': log_mock}):
            log.start_file_logging(path)

        log_mock.assertMethod('setLevel', logging.DEBUG)

        hdlr = logging.FileHandler(path)
        self.assertEqual(type(hdlr), type(log_mock._data['addHandler'][0][0]))
