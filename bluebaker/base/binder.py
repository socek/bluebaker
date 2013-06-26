import venusian
from gevent import spawn
from greentree.binder import Binder as BaseBinder

from bluebaker.app import Application


def add_view(wrapped):
    def callback(scanner, name, obj):
        scanner.binder.add_view(obj)
    venusian.attach(wrapped, callback,  category='views')
    return wrapped


class Binder(BaseBinder):
    base = True

    def __init__(self, *args, **kwargs):
        super(Binder, self).__init__(*args, **kwargs)
        self._id = None

    def set_id(self, value):
        self._id = value

    def get_id(self):
        return self._id

    def generate_views(self):
        import inspect
        scanner = venusian.Scanner()
        scanner.binder = self
        module = inspect.getmodule(self)
        module_name = '.'.join(module.__name__.split('.')[:-1])
        module = __import__(module_name)
        scanner.scan(module)

    def hide_all(self, except_name=None):
        super(Binder, self).hide_all(except_name)
        return spawn(lambda: self.update_size())  # I know this is dirty,
                                     # but I do not know to make it better

    def update_size(self):
        window = self._parent
        sizeHint = window.sizeHint()
        if sizeHint.width() < window.width():
            sizeHint.setWidth(window.width())
        if sizeHint.height() < window.height():
            sizeHint.setHeight(window.height())
        self._parent.resize(sizeHint)

    def set_status(self, text, timeout=0):
        Application().main.status.showMessage(text, timeout)

    def generate_signals(self):
        super(Binder, self).generate_signals()
        self.add_signal(self.update_size)
        self.add_signal(self.set_status)
        self.add_signal(self.set_id)
        self.add_signal(self.close)
        self.add_signal(self.update_list)

    def close(self):
        self._parent.close()

    def update_list(self):
        _id = self.create_controller().generate_id('list')
        window = Application().main.getWindow(_id)
        if window:
            window.binder.make_controller_action('list')
