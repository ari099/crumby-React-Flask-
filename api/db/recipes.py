import os, sys, string, inspect
import ctypes
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlRecord
from PyQt5.QtCore import Qt
from db import *

# The application user interfaces....
mainWindow = uic.loadUiType("recipes_app.ui")[0]
addDialog = uic.loadUiType("add_recipe_dialog.ui")[0]

class CrummyAddRecipe(QtWidgets.QDialog, addDialog):
    """ Open AddRecipe Dialog Box """
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.recipeNameTextBox = self.findChild(QtWidgets.QTextEdit, "recipe_name_textedit")
        self.recipeDescriptionTextBox = self.findChild(QtWidgets.QTextEdit, "recipe_description_textedit")
        self.newIngredientTextBox = self.findChild(QtWidgets.QTextEdit, "new_ingredient_textedit")
        self.newIngredientFormTextBox = self.findChild(QtWidgets.QTextEdit, "new_ingredient_form_textedit")
        self.newIngredientQuantityBox = self.findChild(QtWidgets.QDoubleSpinBox, "new_ingredient_quantity_spinbox")
        self.newIngredientUnitBox = self.findChild(QtWidgets.QComboBox, "new_ingredient_unit_combobox")
        self.ingredientsTableWidget = self.findChild(QtWidgets.QTableWidget, "ingredients_tablewidget")
        self.addIngredientButton = self.findChild(QtWidgets.QPushButton, "add_ingredient_pushbutton")
        self.addIngredientButton.clicked.connect(self.addIngredientToTable)
        self.removeIngredientButton = self.findChild(QtWidgets.QPushButton, "remove_ingredient_pushbutton")
        self.removeIngredientButton.clicked.connect(self.removeSelectedIngredientFromTable)
        self.instructionsListBox = self.findChild(QtWidgets.QListWidget, "instructions_listwidget")
        self.newInstructionTextBox = self.findChild(QtWidgets.QTextEdit, "new_instruction_textedit")
        self.addInstructionButton = self.findChild(QtWidgets.QPushButton, "add_instruction_pushbutton")
        self.addInstructionButton.clicked.connect(self.addInstructionToListBox)
        self.removeInstructionButton = self.findChild(QtWidgets.QPushButton, "remove_instruction_pushbutton")
        self.removeInstructionButton.clicked.connect(self.removeSelectedInstructionsFromListBox)
        self.dlgButtonBox = self.findChild(QtWidgets.QDialogButtonBox, "addRecipeButtonBox")
        self.dlgButtonBox.accepted.connect(self.saveToDB)

    def saveToDB(self):
        name = self.recipeNameTextBox.toPlainText()
        if name == "":
            ctypes.windll.user32.MessageBoxW(0, "Please fill all fields", "ERROR", 0)
            return

        description = self.recipeDescriptionTextBox.toPlainText()
        if description == "":
            ctypes.windll.user32.MessageBoxW(0, "Please fill all fields", "ERROR", 0)
            return

        ingredients_widget = self.ingredientsTableWidget
        if ingredients_widget.rowCount() == 0:
            ctypes.windll.user32.MessageBoxW(0, "You need ingredients for a meal!", "ERROR", 0)
            return

        instructions_widget = self.instructionsListBox
        if instructions_widget.count() == 0:
            ctypes.windll.user32.MessageBoxW(0, "You need instructions to know what to do!", "ERROR", 0)
            return

        ingredients_root = ET.fromstring("<Ingredients></Ingredients>")
        instructions_root = ET.fromstring("<Instructions></Instructions>")
        for row in range(0, ingredients_widget.rowCount()):
            ingredient_name = ingredients_widget.item(row, 0).text()
            ingredient_quantity = ingredients_widget.item(row, 1).text()
            ingredient_unit = ingredients_widget.item(row, 2).text()
            ingredient_form = ingredients_widget.item(row, 3).text()
            tag = ET.SubElement(ET.Element('Ingredient'), 'Ingredient')
            name_tag = ET.SubElement(ET.Element('Name'), 'Name')
            name_tag.text = ingredient_name
            quantity_tag = ET.SubElement(ET.Element('Quantity'), 'Quantity')
            quantity_tag.text = ingredient_quantity
            unit_tag = ET.SubElement(ET.Element('Unit'), 'Unit')
            unit_tag.text = ingredient_unit
            form_tag = ET.SubElement(ET.Element('Form'), 'Form')
            form_tag.text = ingredient_form
            tag.insert(0, name_tag)
            tag.insert(0, quantity_tag)
            tag.insert(0, unit_tag)
            tag.insert(0, form_tag)
            ingredients_root.insert(1, tag)

        for row in range(0, instructions_widget.count()):
            instruction_text = instructions_widget.item(row).text()
            instruction_tag = ET.SubElement(ET.Element('Instruction'), 'Instruction')
            instruction_tag.text = instruction_text
            instructions_root.insert(1, instruction_tag)

        addRecipe(name, description, ET.tostring(instructions_root).decode('utf-8'), ET.tostring(ingredients_root).decode('utf-8'))

    def addIngredientToTable(self):
        ingredientsTable = self.ingredientsTableWidget
        newIngredientName = self.newIngredientTextBox.toPlainText()
        newIngredientQuantity = self.newIngredientQuantityBox.value()
        newIngredientUnit = self.newIngredientUnitBox.currentText()
        newIngredientForm = self.newIngredientFormTextBox.toPlainText()
        if newIngredientName != "" and newIngredientQuantity != "" and newIngredientUnit != "":
            ingredientsTable.setRowCount(ingredientsTable.rowCount() + 1)
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(newIngredientName))
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(newIngredientQuantity)))
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(newIngredientUnit))
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 3, QtWidgets.QTableWidgetItem(newIngredientForm))

    def removeSelectedIngredientFromTable(self):
        ingredientsTable = self.ingredientsTableWidget
        if ingredientsTable.currentRow() != None:
            currentRow = ingredientsTable.currentRow()
            ingredientsTable.removeRow(currentRow)
        else: ctypes.windll.user32.MessageBoxW(0, "Please select a row to remove", "ERROR", 0)

    def addInstructionToListBox(self):
        instructionList = self.instructionsListBox
        instructionText = self.newInstructionTextBox.toPlainText()
        instructionList.addItem(QtWidgets.QListWidgetItem(instructionText))

    def removeSelectedInstructionsFromListBox(self):
        instructionList = self.instructionsListBox
        if instructionList.currentItem() != None:
            instructionList.takeItem(instructionList.currentRow())

class Recipes(QtWidgets.QMainWindow, mainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        mainWindow.__init__(self)
        self.setupUi(self)
        self.model = QSqlTableModel(self)
        self.model.setTable("recipe")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "Name")
        self.model.setHeaderData(2, Qt.Horizontal, "Description")
        self.model.setHeaderData(3, Qt.Horizontal, "Instructions")
        self.model.setHeaderData(4, Qt.Horizontal, "Ingredients")
        self.model.select()

        # Setting up the view
        self.recipe_list_tableview.setModel(self.model)
        self.setCentralWidget(self.recipe_list_tableview)
        self.add_recipe = self.findChild(QtWidgets.QAction, 'actionAdd_Recipe')
        self.add_recipe.triggered.connect(self.add)
        self.remove_recipe = self.findChild(QtWidgets.QAction, 'actionRemove_Recipe')
        self.remove_recipe.triggered.connect(self.remove)

    def add(self):
        dlg = CrummyAddRecipe()
        dlg.exec_()
        self.model.submitAll()

    def remove(self):
        model = self.model
        indices = self.recipe_list_tableview.selectionModel().selectedRows()
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
window = Recipes()
window.show()
sys.exit(app.exec_())
