from PySide.QtGui import QTableWidget, QVBoxLayout, QTableWidgetItem, QPushButton
from PySide.QtGui import QAbstractItemView, QToolTip
from PySide.QtCore import Qt, QPoint
from greentree.view import View as BaseView

from bluebaker.base.form import LineEdit


class View(BaseView):
    base = True

    def show(self):
        super(View, self).show()
        self.binder._parent.setWindowTitle(self.get_title())


class ListView(View):
    base = True

    def show(self):
        super(ListView, self).show()
        win = self.binder._parent
        minimum = self.get_minimal_size()
        height = win.height() if win.height() > minimum[0] else minimum[0]
        width = win.width() if win.width() > minimum[1] else minimum[1]
        win.resize(width, height)

    def create_design(self):
        header = self.get_header_labels()
        self.lay = QVBoxLayout(self)
        self.list = QTableWidget(0, len(header), self)
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list.setHorizontalHeaderLabels(header)
        self.list.doubleClicked.connect(self.on_doubleClicked)

        self.lay.addWidget(self.list)

    def append_row(self, cols, element_id=None):
        rowCount = self.list.rowCount()
        self.list.insertRow(rowCount)

        for index, value in enumerate(cols):
            col = QTableWidgetItem(value)
            col.element_id = element_id
            col.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.list.setItem(rowCount, index, col)

    def on_doubleClicked(self, index):
        item = self.list.item(index.row(), index.column())
        self.binder._parent.open('edit', item.element_id)

    def clear_list(self):
        while self.list.rowCount():
            self.list.removeRow(0)

    def generate_signals(self):
        super(ListView, self).generate_signals()
        self.add_signal(self.fill)

    def fill(self, elements):
        self.clear_list()
        for element in elements:
            cols = self.get_row_from_obj(element)
            self.append_row(cols, element.id)


class FormViewBase(View):

    def __init__(self, *args, **kwargs):
        super(FormViewBase, self).__init__(*args, **kwargs)
        self._inputs = {}
        self._labels = {}
        self._buttons = {}
        self._is_form_generated = False

    def create_line_edit(self, name, enabled=True):
        return LineEdit(self, name, enabled=enabled)

    def add_line_edit(self, name, label, enabled=True):
        LineEdit(
            self, name, self.form.field_patterns[name].label, enabled=enabled)

    def add_button(self, name, label, method):
        if name not in self._buttons:
            self._buttons[name] = []
        button = QPushButton(label)
        self.formLay.addWidget(button)
        button.clicked.connect(method)
        self._buttons[name].append(button)

    def add_submit_button(self, label, name='submit'):
        self.add_button(name, label, self.on_submit)

    def form_data(self):
        data = {
            'form_name': [self.form.name, ],
        }
        for name, inputs in self._inputs.items():
            values = self._get_field_values(name)
            data[name] = values
        return data

    def _set_field_value(self, name, value, index=0):
        edit = self._inputs[name][index]
        edit.value = value

    def _get_field_values(self, name):
        edits = self._inputs[name]
        return [_input.value for _input in edits]

    def update_form(self):
        for name, fields in self.form.fields.items():
            for index, field in enumerate(fields):
                self._set_field_value(name, field.value, index)
                if field.error:
                    edit = self._inputs[name][index]
                    tooltip_point = edit.widget.mapToGlobal(QPoint())
                    tooltip_point -= QPoint(-10, 15)
                    QToolTip.showText(tooltip_point, field.message)

    def on_submit(self):
        if self.form(self.form_data()):
            self.success()
        else:
            self.update_form()
            self.fail()

    def set_form(self, form):
        self.form = form
        if not self._is_form_generated:
            self.generate_form()
            self._is_form_generated = True

        for name, fields in self.form.fields.items():
            for index, field in enumerate(fields):
                self._set_field_value(name, field.value, index)

    def generate_form(self):
        pass  # pragma: no cover

    def fail(self):
        pass  # pragma: no cover

    def success(self):
        pass  # pragma: no cover

    def generate_signals(self):
        super(FormViewBase, self).generate_signals()
        self.add_signal(self.set_form)

    def create_design(self):
        self.formLay = QVBoxLayout(self)
