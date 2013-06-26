import logging
import inspect
from os import path

data = {
    'log': logging.getLogger("bluebaker"),
}


class TestLog(object):

    def __init__(self):
        self.clear()
        self._name = None

    def clear(self):
        self._info = []
        self._warning = []
        self._debug = []

    def tester(self, test, name):
        self._name = name
        self._test = test
        return self

    def get(self, name):
        return getattr(self, '_' + name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._name = None
        self._test = None

    def assertLog(self, text, *args, **kwargs):
        args = tuple([text] + list(args))
        log = self.get(self._name).pop(0)
        self._test.assertEqual(args, log[0])
        self._test.assertEqual(kwargs, log[1])

    def info(self, *args, **kwargs):
        self._info.append((args, kwargs))

    def warning(self, *args, **kwargs):
        self._warning.append((args, kwargs)) # pragma: no cover

    def debug(self, *args, **kwargs):
        self._debug.append((args, kwargs)) # pragma: no cover


def _get_args_as_string(args):
    args = list(args)
    args = [str(arg) for arg in args]
    return ' '.join(args)


def info(*args, **kwargs):
    msg = _get_args_as_string(args)
    data['log'].info(msg, **kwargs)


def warning(*args, **kwargs):
    msg = _get_args_as_string(args)
    data['log'].warning(msg, **kwargs)


def debug(*args, **kwargs):
    from bluebaker.app import Application
    msg = _get_args_as_string(args)
    main_path = path.dirname(Application().modules['main'].__file__)
    src_path = inspect.stack()[1][1]
    src_path = '.' + src_path[len(main_path):]
    line = inspect.stack()[1][2]
    msg = '%s:%d %s' % (src_path, line, msg)
    data['log'].debug(msg, **kwargs)


def error(*args, **kwargs):
    data['log'].warning(*args, **kwargs)


def start_file_logging(path):
    hdlr = logging.FileHandler(path)
    fmt = logging.Formatter("%(asctime)-10s %(message)s")
    hdlr.setFormatter(fmt)
    data['log'].addHandler(hdlr)
    data['log'].setLevel(logging.DEBUG)


def start_test_logging():
    data['log'] = TestLog()


def start_stdout_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-10s %(message)s",
        datefmt="%H:%M:%S"
    )
