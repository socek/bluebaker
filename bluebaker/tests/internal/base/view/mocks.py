class MockBinder(object):

    def __init__(self):
        self._parent = self
        self.title = None
        self._size = None

    def setWindowTitle(self, title):
        self.title = title

    def open(self, name, index):
        self.name = name
        self.index = index

    def height(self):
        return 100

    def width(self):
        return 100

    def resize(self, width, height):
        self._size = width, height


class ListMock(object):

    def __init__(self):
        self.rows = []

    def rowCount(self):
        return len(self.rows)

    def insertRow(self, rowCount):
        self.rows.insert(rowCount, [])

    def setItem(self, row, index, col):
        self.rows[row].insert(index, col)


class ObjectMock(object):

    def __init__(self, _id, *args):
        self.id = _id
        self.args = args


class IndexMock(object):

    def __init__(self, row, col):
        self._row = row
        self._col = col

    def row(self):
        return self._row

    def column(self):
        return self._col


class ClickedMockup(object):

    def __init__(self):
        self.method = None

    def connect(self, method):
        self.method = method
