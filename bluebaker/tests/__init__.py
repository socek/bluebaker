from sys import argv
import logging
import unittest
from os import path

import venusian

from bluebaker.tests.base import TestCase


class SokTestRunner(object):

    def __init__(self, module, log_file_name='test.log', log_file_dir=''):
        self.module = module
        self.log_file_name = log_file_name
        self.log_file_dir = log_file_dir
        self.tests = []
        self.verbosity = None

    def import_tests(self):
        # we use venusian scanner for "import all tests"
        scanner = venusian.Scanner()
        scanner.scan(self.module, categories=('tests',))

    def prepere_all_test_cases(self, suite):
        test_cases = []
        for test_case in TestCase.alltests:
            test_cases.append(
                suite.loadTestsFromTestCase(test_case)
            )
        return test_cases

    def prepere_specyfic_test_cases(self, suite, tests_names):
        def unpack_name(name):
            tab = name.split(':')
            if len(tab) < 2:
                tab.append(None)
            return tab

        test_cases = []
        for name in tests_names:
            name, method_name = unpack_name(name)

            try:
                test_case = TestCase.alltests_dict[name]
            except KeyError:
                names = '\n\t'.join(TestCase.alltests_dict.keys())
                raise RuntimeError(
                    'Bad test name: %s. Use one of:\n\t%s' % (name, names)
                )
            if test_case is None:
                filter_names = lambda test_name: test_name.endswith(
                    name) and test_name != name
                names = '\n\t'.join(filter(
                    filter_names, TestCase.alltests_dict.keys()))
                raise RuntimeError(
                    'Test name is ambiguous. Please provide full package name:\n\t%s' % (
                        names,)
                )
            if method_name is None:
                test_cases.append(
                    suite.loadTestsFromTestCase(test_case)
                )
            else:
                suite = unittest.TestSuite()
                suite.addTest(test_case(method_name))
                test_cases.append(suite)

        return test_cases

    def start_logging(self):
        from soklog import init
        if path.exists(self.log_file_dir):
            filename = path.join(self.log_file_dir, self.log_file_name)
        else:
            filename = self.log_file_name

        init(self.module, 'sok_test')

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)-15s:%(message)s",
            filename=filename,
        )
        logging.getLogger('finlog').info('\n\t*** TESTING STARTED ***')

    def get_all_test_suite(self):
        self.start_logging()
        self.additional_preparation()
        self.import_tests()
        suite = unittest.TestLoader()

        if len(self.tests) == 0:
            return unittest.TestSuite(self.prepere_all_test_cases(suite))
        else:
            return unittest.TestSuite(self.prepere_specyfic_test_cases(suite, self.tests))

    def additional_preparation(self):
        pass

    def update_verbosity(self, force_number=None):
        if force_number:
            self.force_number = force_number
        else:
            if len(self.tests) == 0:
                self.verbosity = 1
            else:
                self.verbosity = 2

    def update_tests_from_argv(self):
        self.tests = argv[1:]

    def do_tests(self):
        self.update_tests_from_argv()
        self.update_verbosity()
        suite = self.get_all_test_suite()
        unittest.TextTestRunner(verbosity=self.verbosity).run(suite)


class BlueBakerTestRunner(SokTestRunner):

    def additional_preparation(self):
        super(BlueBakerTestRunner, self).additional_preparation()
        # need qt app for testing qwidgets
        from PySide.QtGui import QApplication
        global qtApp
        qtApp = QApplication(argv)

def get_all_test_suite():
    import bluebaker
    runner = BlueBakerTestRunner(bluebaker)
    return runner.get_all_test_suite()
