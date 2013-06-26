from bluebaker.tests.base import TestCase
from bluebaker.tests.internal.base.view.mocks import MockBinder
from bluebaker.base.view import View


class ExampleView(View):

    def get_title(self):
        return 'example title'

    def create_design(self):
        pass


class ViewTest(TestCase):

    def test_show(self):
        binder = MockBinder()
        view = ExampleView(binder)
        view.show()
        self.assertEqual('example title', binder.title)
