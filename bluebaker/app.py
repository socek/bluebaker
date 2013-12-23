# -*- encoding: utf-8 -*-
import sys

from PySide.QtGui import QApplication
from gevent import sleep, spawn
from soklog import info, init

from bluebaker.singleton import Singleton


class Application(object):

    __metaclass__ = Singleton

    def __init__(self):
        self.debug = False
        self.qtApp = None
        self.running = True
        self.settings = None
        self.db = None
        self.modules = None

    def set_main_module(self, main, settings):
        self.modules = {
            'main': main,
            'settings': settings,
        }
        init(self.modules['main'], 'bluebaker')

    def set_debug(self, debug=False):
        self.debug = debug

    def make_settings(self):
        self.settings = self.modules['settings'].make_settings()

    def sleep(self, *args):
        return sleep(*args)  # pragma: no cover

    def mainloop(self):
        while self.running:
            self.qtApp.processEvents()
            while self.qtApp.hasPendingEvents():
                self.qtApp.processEvents()
                self.sleep()
            self.sleep(0.01)

    def additionMethod(self):
        if self.settings and 'additionMethod' in self.settings:
            self.settings['additionMethod'](self)

    def initQtApp(self):
        self.qtApp = QApplication(sys.argv)

    def createTopWindow(self):
        from bluebaker.topwindow import TopWindow
        self.main = TopWindow(self)
        self.main.show()
        self.init_window()

    def init_window(self):
        pass

    def run(self):
        try:
            self.createTopWindow()
            spawn(self.mainloop).join()
        except KeyboardInterrupt:
            info('\r', end='')  # clearing CTRL+R character
        finally:
            info(' === Program ended ===')

    def close(self):
        self.running = False
