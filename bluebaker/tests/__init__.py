from sys import argv

from soktest import TestRunner


class BlueBakerTestRunner(TestRunner):

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
