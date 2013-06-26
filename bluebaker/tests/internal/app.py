from contextlib import nested
from mock import patch

from bluebaker.tests.base import TestCase
from bluebaker.app import Application
from bluebaker.singleton import Singleton


class QtAppMock(object):

    def __init__(self, app):
        self._processEvents = 0
        self._hasPendingEvents = False
        self.app = app

    def processEvents(self):
        self._processEvents += 1
        if self._processEvents >= 4:
            self.app.running = False

    def hasPendingEvents(self):
        result = not self._hasPendingEvents
        self._hasPendingEvents = True
        return result


class MainAppTest(TestCase):

    def setUp(self):
        self._instances = Singleton._instances
        Singleton._instances = {}

    def tearDown(self):
        Singleton._instances = self._instances

    def test_init(self):
        app = Application()

        self.assertEqual(False, app.debug)
        self.assertEqual(None, app.qtApp)
        self.assertEqual(True, app.running)
        self.assertEqual(None, app.settings)
        self.assertEqual(None, app.db)

    def test_set_debug(self):
        app = Application()
        app.set_debug(True)

        self.assertEqual(True, app.debug)

    def test_make_settings(self):
        app = Application()
        app.make_settings()

        self.assertEqual(dict, type(app.settings))
        self.assertEqual('finlog', app.settings['project_name'])
        self.assertTrue('paths' in app.settings)

    def test_initDatabase(self):
        app = Application()
        app.settings = {
            'dbpath': 'unrelevant',
        }

        with patch('cdborm.connection.connec_to_database') as mock:
            mock.return_value = (1, 2)
            app.initDatabase()

            self.assertEqual(1, app.db)

    def test_initQtApp(self):
        # I can not test if the QApplication was sucessfully initalized.
        # Only one QApplication can be initalized during program run
        app = Application()
        self.assertRaises(RuntimeError, app.initQtApp)

    def test_createMainWindow(self):
        from bluebaker.topwindow.window import TopWindow
        app = Application()
        app.createTopWindow()

        self.assertEqual(TopWindow, type(app.main))

    def test_run(self):
        def mockup(self):
            self._mainloop = True

        app = Application()
        with nested(
                patch.object(app, 'createTopWindow'),
                patch.object(Application, 'mainloop', mockup),
        ):
            app.run()
        log = self.log.get('info')
        self.assertTrue(app._mainloop)
        with self.log.tester(self, 'info') as log:
            log.assertLog(' === Program ended ===')

    def test_run_KeyboardInterrupt(self):
        def side_effect():
            raise KeyboardInterrupt()

        def mockup(self):
            self._mainloop = True

        app = Application()
        app._mainloop = False
        with nested(
                patch.object(app, 'createTopWindow', side_effect=side_effect),
                patch.object(Application, 'mainloop', mockup),
        ):

            app.run()
        log = self.log.get('info')
        self.assertFalse(app._mainloop)
        with self.log.tester(self, 'info') as log:
            log.assertLog('\r', end='')
            log.assertLog(' === Program ended ===')

    def test_close(self):
        app = Application()
        app.close()

        self.assertFalse(app.running)

    def test_mainloop(self):
        app = Application()
        qtApp = QtAppMock(app)
        with nested(
                patch.object(app, 'qtApp', qtApp),
                patch.object(app, 'sleep'),
        ):
            app.mainloop()

            self.assertEqual(4, qtApp._processEvents)
            self.assertTrue(qtApp._hasPendingEvents)
