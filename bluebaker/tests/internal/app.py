import sys
from contextlib import nested
from mock import patch

from bluebaker.tests.base import TestCase
from bluebaker.app import Application
from bluebaker.singleton import Singleton
from bluebaker.tests.mocker import ClassMockup


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


class SettingsMock(ClassMockup):

    def __init__(self, test):
        super(SettingsMock, self).__init__(test)
        self.add_method('make_settings')


class MainAppTest(TestCase):

    def setUp(self):
        super(MainAppTest, self).setUp()
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
        settings = SettingsMock(self)
        app = Application()
        app.modules = {
            'settings': settings,
        }
        app.make_settings()

        settings.assertMethod('make_settings')

    def test_additionMethod(self):
        app = Application()
        app.settings = {
            'additionMethod': self.generateMock('name')[1]
        }

        app.additionMethod()
        self.assertMock('name', app)

    @patch('bluebaker.app.QApplication')
    def test_initQtApp(self, qtapp):
        app = Application()
        app.initQtApp()

        qtapp.assert_called_once_with(sys.argv)
        self.assertEqual(qtapp.return_value, app.qtApp)

    def test_createMainWindow(self):
        from bluebaker.topwindow import TopWindow
        app = Application()
        app.settings = {
            'top window title': 'my top window title',
        }
        app.createTopWindow()

        self.assertEqual(TopWindow, type(app.main))

    def test_run(self):
        def mockup(self):
            self._mainloop = True

        app = Application()
        with nested(
                patch.object(app, 'createTopWindow'),
                patch.object(Application, 'mainloop', mockup),
                patch('bluebaker.app.info'),
        ) as (createTopWindow, mainloop, info):
            app.run()
            info.assert_called_once_with(' === Program ended ===')
        self.assertTrue(app._mainloop)

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
                patch('bluebaker.app.info'),
        ) as (createTopWindow, mainloop, info):
            app.run()
            info.assert_called_with(' === Program ended ===')
        self.assertFalse(app._mainloop)

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
