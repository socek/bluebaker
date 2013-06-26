from greentree.controller import Controller as BaseController


class Controller(BaseController):

    @classmethod
    def generate_id(cls, *args):
        args = [cls.__name__] + list(args)
        return '_'.join(args)

    def set_id(self, name, *args):
        _id = self.generate_id(name, *args)
        self.add_binder_signal('set_id', _id)
