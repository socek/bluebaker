# -*- encoding: utf-8 -*-
from PySide import QtGui
from bluebaker.app import Application


class TopMenuGenerator(object):

    def __init__(self, parent):
        self.parent = parent
        self.buttonsGenerator = Application().settings['buttonsGenerator'](parent)

        self.generate()

    def createFileMenu(self):
        fileMenu = self.topMenu.addMenu(u'Plik')

        self.buttonsGenerator.close(fileMenu)

    def createBillMenu(self):
        billMenu = self.topMenu.addMenu(u'Rachunek')
        self.buttonsGenerator.bill_new(billMenu)
        self.buttonsGenerator.bill_list(billMenu)

    def createProductMenu(self):
        productMenu = self.topMenu.addMenu(u'Product')
        self.buttonsGenerator.product_new(productMenu)
        self.buttonsGenerator.product_list(productMenu)

    def generate(self):
        self.topMenu = QtGui.QMenuBar(self.parent)
        self.parent.setMenuBar(self.topMenu)

        self.createFileMenu()
        self.createBillMenu()
        self.createProductMenu()

        return self.topMenu
