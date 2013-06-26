from bluebaker.tests.base import TestCase
from bluebaker.base.controller import Controller


class ControllerTest(TestCase):

    def test_generate_id(self):
        _id = Controller.generate_id('elo', 'elo2')
        self.assertEqual('Controller_elo_elo2', _id)

    def test_set_id(self):
        controller = Controller()
        controller.set_id('myid', 'arg')

        signal = controller.signals[0]
        self.assertEqual(None, signal.view_name)
        self.assertEqual('set_id', signal.name)
        self.assertEqual((('Controller_myid_arg',), {}), signal.args)
