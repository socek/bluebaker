import logging
from argparse import ArgumentParser
from contextlib import nested
from mock import patch

from bluebaker.cmd import Command
from bluebaker.tests.base import TestCase
from bluebaker.tests.mocker import ClassMockup


class ArgsMockup(object):

    def __init__(self, debug):
        self.debug = debug


class ArgumentParserMockup(ArgumentParser):

    def parse_args(self):
        return False


class ApplicationMock(ClassMockup):

    def __init__(self, test):
        super(ApplicationMock, self).__init__(test)
        self.add_method('set_debug')
        self.add_method('make_settings')
        self.add_method('initDatabase')
        self.add_method('initQtApp')
        self.add_method('run')


class CmdTest(TestCase):

    def setUp(self):
        super(CmdTest, self).setUp()
        self.cmd = Command()
        self.app = ApplicationMock(self)
        self.cmd.app = lambda: self.app

    def test_prepere_settings(self):
        args = ArgsMockup(False)

        self.cmd.prepere_settings(args)

        self.app.assertMethod('set_debug', False)
        self.app.assertMethod('make_settings')

    def test_prepere_app(self):
        self.cmd.prepere_app()

        self.app.assertMethod('initDatabase')
        self.app.assertMethod('initQtApp')

    def test_parse_arguments(self):
        self.assertFalse(self.cmd.parse_arguments(ArgumentParserMockup))

    def test_run(self):
        self.app.debug = False
        with nested(
                patch.object(self.cmd, 'parse_arguments'),
                patch.object(self.cmd, 'start_logging'),
                patch.object(self.cmd, 'print_info'),
        ):
            self.cmd.run()
        self.app.assertMethod('run')

    def test_print_info(self):
        with self.patch(self.cmd, 'print_'):
            self.cmd.print_info()

        self.assertMock('print_', "Press CTRL+C to quit.")

        with self.log.tester(self, 'info') as log:
            log.assertLog(' === Program start ===')

    def test_start_logging_with_debug(self):
        self.app.debug = True
        with nested(
            self.patch(logging, 'basicConfig'),
            self.patch(self.cmd, 'print_'),
        ):
            self.cmd.start_logging()

        self.assertMock('basicConfig',
                        level=logging.DEBUG,
                        format="%(asctime)-10s %(message)s",
                        datefmt="%H:%M:%S")

        self.assertMock(
            'print_', "Player is running with debug mode! Are logs are sent to stdout.")

    def test_start_logging(self):
        self.app.debug = False
        self.app.settings = {
            'log_path': '/tmp/test_path'
        }
        with self.patch(self.cmd, 'print_'):
            self.assertRaises(AttributeError, self.cmd.start_logging)

        self.assertMock('print_', "All logs are hidden: /tmp/test_path")
