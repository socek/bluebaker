from mock import patch

from PySide.QtGui import QVBoxLayout, QTableWidget

from bluebaker.base.view import ListView
from bluebaker.tests.base import TestCase
from bluebaker.tests.internal.base.view.mocks import MockBinder, ListMock, IndexMock, ObjectMock


class ExampleListView(ListView):

    def get_title(self):
        return 'my title'

    def get_minimal_size(self):
        return 50, 50

    def get_header_labels(self):
        return [
            'one',
            'two',
            'three',
        ]

    def get_row_from_obj(self, element):
        return element.args


class ListViewTest(TestCase):

    def setUp(self):
        super(ListViewTest, self).setUp()
        self.binder = MockBinder()
        self.view = ExampleListView(self.binder)

    def test_init(self):
        self.assertEqual(QVBoxLayout, type(self.view.lay))
        self.assertEqual(QTableWidget, type(self.view.list))

    def test_append_row(self):
        qlist = ListMock()
        with patch.object(self.view, 'list', qlist):
            self.view.append_row(['col one', 'col two', 'col three'])

        row = qlist.rows[0]
        self.assertEqual('col one', row[0].text())
        self.assertEqual('col two', row[1].text())
        self.assertEqual('col three', row[2].text())

    def test_on_doubleClicked(self):
        self.view.append_row(['col one', 'col two', 'col three'], 11)
        self.view.on_doubleClicked(IndexMock(0, 1))
        self.assertEqual('edit', self.binder.name)
        self.assertEqual(11, self.binder.index)

    def test_show(self):
        self.view.show()
        self.assertEqual((100, 100), self.binder._size)

    def test_clear_list(self):
        self.view.append_row(['col one', 'col two', 'col three'], 11)
        self.view.append_row(['col one', 'col two', 'col three'], 11)

        self.view.clear_list()
        self.assertEqual(0, self.view.list.rowCount())

    def test_fill(self):
        elements = [
            ObjectMock('one', 'two', 'three'),
            ObjectMock('2 one', '2 two', '2 three'),
        ]
        self.view.fill(elements)

        self.assertEqual(2, self.view.list.rowCount())
        expected_data = [
            ['two', 'three'],
            ['2 two', '2 three'],
        ]
        expected_ids = ['one', '2 one']
        for row in xrange(2):
            for col in xrange(2):
                item = self.view.list.item(row, col)
                text = expected_data[row][col]
                self.assertEqual(text, item.text())
                self.assertEqual(expected_ids[row], item.element_id)
