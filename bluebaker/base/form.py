from PySide.QtGui import QLineEdit, QLabel, QHBoxLayout

class FormInput(object):

    def __init__(self, parent, name, label=None, enabled=True):
        self.parent = parent
        self.name = name

        self.widget = None
        self.create_label(label)
        self.create_widget(enabled)
        self.append_to_parent()
        self.append_to_layout()

    def create_label(self, label):
        if label:
            self.label = QLabel(label)
        else:
            self.label = None

    def append_to_parent(self):
        self.parent._inputs.setdefault(self.name, [])
        self.parent._inputs[self.name].append(self)

    def append_to_layout(self):
        lineLay = QHBoxLayout()
        if self.label:
            lineLay.addWidget(self.label)
        lineLay.addWidget(self.widget)
        self.parent.formLay.addLayout(lineLay)

    def _get_value(self):
        return self.widget.text()

    def _set_value(self, value):
        self.widget.setText(value)

    value = property(_get_value, _set_value)


class LineEdit(FormInput):

    def create_widget(self, enabled):
        widget = QLineEdit()
        widget.setEnabled(enabled)
        self.widget = widget
