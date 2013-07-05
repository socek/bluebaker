from PySide.QtGui import QLineEdit, QLabel, QHBoxLayout, QPushButton
from formskit import Form, Field
from mock import patch

from bluebaker.base.view import FormViewBase
from bluebaker.tests.base import TestCase
from bluebaker.tests.internal.base.view.mocks import MockBinder, ClickedMockup


class ExampleForm(Form):

    def createForm(self):
        self.addField(Field('name1', label=u'Numer'))


class ExampleFormWithList(Form):

    def createForm(self):
        self.addFieldList(Field('name1', label=u'Numer'))


class ExampleFormView(FormViewBase):

    def __init__(self, *args, **kwargs):
        super(ExampleFormView, self).__init__(*args, **kwargs)
        self._success = False
        self._fail = False

    def generate_form(self):
        self.add_line_edit('name1', True)

    def success(self):
        self._success = True

    def fail(self):
        self._fail = True


class SecondExampleFormView(FormViewBase):

    def generate_form(self):
        self.add_line_edit('name1', False)


class FormViewTest(TestCase):

    def setUp(self):
        super(FormViewTest, self).setUp()
        self.binder = MockBinder()
        self.view = ExampleFormView(self.binder)

    def test_init(self):
        self.assertEqual({}, self.view._inputs)
        self.assertFalse(self.view._is_form_generated)

    def test_add_line_edit_enabled(self):
        self.view.set_form(ExampleForm())

        self.assertTrue('name1' in self.view._inputs)
        edit = self.view._inputs['name1'][0]
        label = self.view._labels['name1']
        self.assertTrue(edit.isEnabled())
        self.assertEqual(QLineEdit, type(edit))
        self.assertEqual(QLabel, type(label))
        self.assertEqual(QHBoxLayout, type(self.view.formLay.itemAt(0)))
        lay = self.view.formLay.itemAt(0)
        self.assertEqual(label, lay.itemAt(0).widget())
        self.assertEqual(edit, lay.itemAt(1).widget())

    def test_add_line_edit_disabled(self):
        self.view = SecondExampleFormView(self.binder)
        self.view.set_form(ExampleForm())

        self.assertTrue('name1' in self.view._inputs)
        edit = self.view._inputs['name1'][0]
        label = self.view._labels['name1']
        self.assertFalse(edit.isEnabled())
        self.assertEqual(QLineEdit, type(edit))
        self.assertEqual(QLabel, type(label))
        self.assertEqual(QHBoxLayout, type(self.view.formLay.itemAt(0)))
        lay = self.view.formLay.itemAt(0)
        self.assertEqual(label, lay.itemAt(0).widget())
        self.assertEqual(edit, lay.itemAt(1).widget())

    def test_add_button(self):
        def method():
            pass  # pragma: no cover

        mock = ClickedMockup()
        with patch.object(QPushButton, 'clicked', mock):
            self.view.add_button('label', method)
            self.assertEqual(method, mock.method)
            widget = self.view.formLay.itemAt(0).widget()
            self.assertEqual('label', widget.text())
            self.assertEqual(QPushButton, type(widget))

    def test_add_submit_button(self):
        mock = ClickedMockup()
        with patch.object(QPushButton, 'clicked', mock):
            self.view.add_submit_button('label2')
            self.assertEqual(self.view.on_submit, mock.method)
            widget = self.view.formLay.itemAt(0).widget()
            self.assertEqual('label2', widget.text())
            self.assertEqual(QPushButton, type(widget))

    def test_form_data(self):
        self.view.set_form(ExampleForm())
        self.view._inputs['name1'][0].setText('value1')
        data = self.view.form_data()
        self.assertEqual('ExampleForm', data['form_name'])
        self.assertEqual('value1', data['name1'])

    def test_form_data_multiply(self):
        self.view.set_form(ExampleFormWithList())
        self.view.create_line_edit('name1')

        self.view._inputs['name1'][0].setText('value1')
        self.view._inputs['name1'][1].setText('value2')
        data = self.view.form_data()
        self.assertEqual('ExampleFormWithList', data['form_name'])
        self.assertEqual(['value1', 'value2'], data['name1'])

    def test_update_form(self):
        form = ExampleForm()
        self.view.set_form(form)
        form['name1'].value = 'value3'
        form['name1'].error = True
        form['name1'].message = 'message1'
        self.view.update_form()

        self.assertEqual(['value3',], self.view._get_field_values('name1'))

    def test_create_line_edit(self):
        self.view.create_line_edit('name1', True)
        self.view.create_line_edit('name1', False)

        self.assertEqual(2, len(self.view._inputs['name1']))
        self.assertTrue(self.view._inputs['name1'][0].isEnabled())
        self.assertFalse(self.view._inputs['name1'][1].isEnabled())

    def test_get_field_values(self):
        self.view.create_line_edit('name1', True).setText('1')

        self.assertEqual(['1',], self.view._get_field_values('name1'))

    def test_get_field_value_many(self):
        self.view.create_line_edit('name1', True).setText('1')
        self.view.create_line_edit('name1', False).setText('2')

        self.assertEqual(['1', '2'], self.view._get_field_values('name1'))


class FieldValueTest(TestCase):

    def setUp(self):
        super(FieldValueTest, self).setUp()
        self.binder = MockBinder()
        self.view = ExampleFormView(self.binder)

    def test_qlineedit_set(self):
        self.view.set_form(ExampleForm())
        self.view._set_field_value('name1', 'value2')
        inputs = self.view._inputs['name1']
        self.assertEqual(1, len(inputs))
        self.assertEqual('value2', inputs[0].text())

    def test_else_set(self):
        self.view._inputs['name_else'] = [None, ]

        self.assertRaises(
            RuntimeError, self.view._set_field_value, 'name_else', 'value')

    def test_qlineedit_get(self):
        self.view.set_form(ExampleForm())
        self.view._set_field_value('name1', 'value3')

        self.assertEqual(['value3',], self.view._get_field_values('name1'))

    def test_else_get(self):
        self.view._inputs['name_else'] = [None, ]

        self.assertRaises(
            RuntimeError, self.view._get_field_values, 'name_else')

    def test_on_submit(self):
        self.view.form = None
        with patch.object(self.view, 'form', return_value=True):
            self.view.on_submit()
            self.assertTrue(self.view._success)
            self.assertFalse(self.view._fail)

    def test_on_submit_fail(self):
        self.view.form = None
        with patch.object(self.view, 'form', return_value=False):
            self.view.on_submit()
            self.assertFalse(self.view._success)
            self.assertTrue(self.view._fail)
