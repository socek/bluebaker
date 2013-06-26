from sys import argv

import logging
import unittest
import venusian

from bluebaker.tests.base import TestCase


def import_tests(module):
    # we use venusian scanner for "import all tests"
    scanner = venusian.Scanner()
    scanner.scan(module, categories=('tests',))


def get_all_test_suite(module, tests):
    def prepere_all_test_cases(suite):
        test_cases = []
        for test_case in TestCase.alltests:
            test_cases.append(
                suite.loadTestsFromTestCase(test_case)
            )
        return test_cases

    def prepere_specyfic_test_cases(suite, tests_names):
        test_cases = []
        for name in tests_names:
            try:
                test_case = TestCase.alltests_dict[name]
            except KeyError:
                names = '\n\t'.join(TestCase.alltests_dict.keys())
                raise RuntimeError(
                    'Bad test name: %s. Use one of:\n\t%s' % (name, names)
                )
            test_cases.append(
                suite.loadTestsFromTestCase(test_case)
            )
        return test_cases

    def start_logging():
        from bluebaker.log import start_test_logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)-15s:%(message)s",
            filename='data/test.log'
        )
        logging.getLogger('finlog').info('\n\t*** TESTING STARTED ***')
        start_test_logging()

    def create_qt_app():
        # need qt app for testing qwidgets
        from PySide.QtGui import QApplication
        global qtApp
        qtApp = QApplication(argv)
    #-------------------------------------------------------------------------
    start_logging()
    create_qt_app()
    import_tests(module)
    suite = unittest.TestLoader()
    if tests == []:
        return unittest.TestSuite(prepere_all_test_cases(suite))
    else:
        return unittest.TestSuite(prepere_specyfic_test_cases(suite, tests))


def runner(module):
    tests = argv[1:]
    if len(tests) == 0:
        verbosity = 2
    else:
        verbosity = 2
    suite = get_all_test_suite(module, tests)
    unittest.TextTestRunner(verbosity=verbosity).run(suite)
