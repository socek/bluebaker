from __future__ import print_function
from bluebaker.log import info, start_file_logging, start_stdout_logging
from bluebaker.app import Application
import argparse


class Command(object):

    def __init__(self, main, settings):
        self.app().set_main_module(main, settings)

    def app(self):
        return Application()  # pragma: no cover

    def parse_arguments(self, parse_class=argparse.ArgumentParser):
        parser = parse_class()
        parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                            help='Turn on the debug mode.')

        return parser.parse_args()

    def prepere_settings(self, args):
        self.app().set_debug(args.debug)
        self.app().make_settings()

    def start_logging(self):
        if self.app().debug:
            self.print_(
                "Player is running with debug mode! Are logs are sent to stdout.")
            start_stdout_logging()
        else:
            self.print_("All logs are hidden: %s" %
                       (self.app().settings['log_path']))
            start_file_logging(self.app().settings[
                               'log_path'])

    def print_(self, *args, **kwargs):
        print(*args, **kwargs)  # pragma: no cover

    def print_info(self):
        self.print_("Press CTRL+C to quit.")
        info(' === Program start ===')

    def prepere_app(self):
        self.app().additionMethod()
        self.app().initQtApp()

    def run(self):
        args = self.parse_arguments()
        self.prepere_settings(args)
        self.start_logging()
        self.print_info()
        self.prepere_app()
        self.app().run()
