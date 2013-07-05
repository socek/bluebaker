class ClassMockup(object):

    def __init__(self, test):
        self._data = {}
        self.test = test

    def _set_data(self, name, args, kwargs):
        self._data[name] = (args, kwargs)

    def assertMethod(self, name, *args, **kwargs):
        self.test.assertEqual(args, self._data[name][0])
        self.test.assertEqual(kwargs, self._data[name][1])

    def add_method(self, name):
        def method(*args, **kwargs):
            self._set_data(name, args, kwargs)

        setattr(self, name, method)

class BinderMockup(ClassMockup):

    def __init__(self, *args, **kwargs):
        super(BinderMockup, self).__init__(*args, **kwargs)
        self.add_method('make_controller_action')
        self.add_method('update_size_with_delay')
