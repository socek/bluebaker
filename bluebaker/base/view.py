from greentree.view import View as BaseView
from PySide.QtGui import QTableWidget, QVBoxLayout, QTableWidgetItem, QPushButton
from PySide.QtGui import QAbstractItemView, QLineEdit, QLabel, QHBoxLayout, QToolTip
from PySide.QtCore import Qt, QPoint


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
        self._is_form_generated = False

    def create_line_edit(self, name, enabled=True):
        edit = QLineEdit()
        if not enabled:
            edit.setEnabled(False)
        if not name in self._inputs:
            self._inputs[name] = [edit]
        else:
            self._inputs[name].append(edit)
        return edit

    def add_line_edit(self, name, enabled=True):
        edit = self.create_line_edit(name, enabled)
        label = QLabel(self.form[name].label)
        self._labels[name] = label

        lineLay = QHBoxLayout()
        lineLay.addWidget(label)
        lineLay.addWidget(edit)

        self.formLay.addLayout(lineLay)

    def add_button(self, label, method):
        submitButton = QPushButton(label)
        self.formLay.addWidget(submitButton)
        submitButton.clicked.connect(method)

    def add_submit_button(self, label):
        self.add_button(label, self.on_submit)

    def form_data(self):
        data = {
            'form_name': self.form.name,
        }
        for name, inputs in self._inputs.items():
            values = self._get_field_values(name)
            data[name] = values
        return data

    def _set_field_value(self, name, value, index=0):
        edit = self._inputs[name][index]
        if type(edit) in (QLineEdit,):
            edit.setText(value)
        else:
            raise RuntimeError("Could not set to an input.")

    def _get_field_values(self, name):
        def get_field_value(edit):
            if type(edit) in (QLineEdit,):
                return edit.text()
            else:
                raise RuntimeError("Could not get from an input.")
        edits = self._inputs[name]
        return [get_field_value(edit) for edit in edits]

    def update_form(self):
        for name, field in self.form.fields.items():
            self._set_field_value(name, field.value)
            if field.error:
                edit = self._inputs[name][0] #TODO: make this more flexible, not static first element
                tooltip_point = edit.mapToGlobal(QPoint())
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

        for name, field in self.form.fields.items():
            self._set_field_value(name, field.value)

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
