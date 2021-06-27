import sys, random
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRecord
from PyQt5.QtCore import Qt
from db import *

# The application user interfaces....
mainWindow = uic.loadUiType("ingredients_app.ui")[0]
addDialog = uic.loadUiType("add_ingredient_dialog.ui")[0]

class CrummyAddIngredient(QtWidgets.QDialog, addDialog):
    """ Open AddIngredient Dialog Box"""
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.ingredientName = self.findChild(QtWidgets.QTextEdit, 'ingredient_name_textedit')
        self.quantity = self.findChild(QtWidgets.QSpinBox, 'quantity_spinbox')
        self.unitOfMeasure = self.findChild(QtWidgets.QComboBox, 'unit_combobox')
        self.buttonBox = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox')
        self.buttonBox.accepted.connect(self.addIngredient)

    def addIngredient(self):
        ingredientName = self.ingredientName.toPlainText()
        quantity = self.quantity.value()
        unit = self.unitOfMeasure.currentText()
        addIngredient(ingredientName, int(quantity), unit)

class MainWindow(QtWidgets.QMainWindow, mainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        mainWindow.__init__(self)
        self.setupUi(self)
        self.model = QSqlTableModel(self)
        self.model.setTable("ingredient")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "Name")
        self.model.setHeaderData(2, Qt.Horizontal, "Quantity")
        self.model.setHeaderData(3, Qt.Horizontal, "Unit")
        self.model.select()

        # Setting up the view
        self.ingredients_list.setModel(self.model)
        self.setCentralWidget(self.ingredients_list)
        self.add_ingredient = self.findChild(QtWidgets.QAction, 'actionAdd_Ingredient')
        self.add_ingredient.triggered.connect(self.add)
        self.remove_ingredient = self.findChild(QtWidgets.QAction, 'actionRemove_Ingredient')
        self.remove_ingredient.triggered.connect(self.remove)

    def add(self):
        dlg = CrummyAddIngredient()
        dlg.exec_()
        self.model.submitAll()

    def remove(self):
        """ Remove selected row from Ingredients QTableWidget """
        # Check if any are selected
        # query(f"DELETE FROM Ingredient WHERE Name = '{self.model.ingredients[index.row()][1]}'")
        model = self.model
        indices = self.ingredients_list.selectionModel().selectedRows()
        for index in sorted(indices): model.removeRow(index.row())
        self.model.submitAll()

def createConnection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("crummy.db")
    if not con.open():
        QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True

app = QtWidgets.QApplication(sys.argv)
if not createConnection(): sys.exit(1)
window = MainWindow()
window.show()
sys.exit(app.exec_())
