import os, sys, json, ctypes
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
import urllib

mainWindow = uic.loadUiType("crumby.ui")[0]
instructionsDlg = uic.loadUiType("instructions_dlg.ui")[0]
ingredientsDlg = uic.loadUiType("ingredients_dlg.ui")[0]

class CrumbsModel(QtCore.QAbstractListModel):
    def __init__(self, data):
        super(CrumbsModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

class InstructionsDialog(QtWidgets.QDialog, instructionsDlg):
    """ Open InstructionsDialog Dialog Box """
    def __init__(self, recipe_id, recipe_instructions, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.recipe_id = recipe_id
        self.instructions_list = self.findChild(QtWidgets.QListWidget, "instructions_list")
        instructions = ET.fromstring(recipe_instructions)
        for instruction in instructions:
            widgetItem = QtWidgets.QListWidgetItem(instruction.text)
            self.instructions_list.addItem(widgetItem)

        self.instruction_text = self.findChild(QtWidgets.QTextEdit, "instruction_text")
        self.add_instruction = self.findChild(QtWidgets.QPushButton, "add_instruction")
        self.add_instruction.clicked.connect(lambda: self.instructions_list.addItem(self.instruction_text.toPlainText()))
        self.remove_selected_instruction = self.findChild(QtWidgets.QPushButton, "remove_selected_instruction")
        self.remove_selected_instruction.clicked.connect(self.remove)
        self.dlgButtonBox = self.findChild(QtWidgets.QDialogButtonBox, "buttonBox")
        self.dlgButtonBox.accepted.connect(self.saveInstructions)

    def saveInstructions(self):
        instructions_widget = self.instructions_list
        if instructions_widget.count() == 0:
            ctypes.windll.user32.MessageBoxW(0, "You need instructions to know what to do!", "ERROR", 0)
            return

        instructions_root = ET.fromstring("<Instructions></Instructions>")
        for row in range(0, instructions_widget.count()):
            instruction_text = instructions_widget.item(row).text()
            instruction_tag = ET.SubElement(ET.Element('Instruction'), 'Instruction')
            instruction_tag.text = instruction_text
            instructions_root.insert(1, instruction_tag)

        new_data = {
            "field": "Instructions",
            "value": ET.tostring(instructions_root).decode('utf-8')
        }
        req = Request('http://127.0.0.1:5000/update_recipe/{0}'.format(self.recipe_id))
        req.add_header('Content-Type', 'application/json')
        response = urlopen(req, json.dumps(new_data).encode('utf8'))

    def remove(self):
        instructions = self.instructions_list.selectedItems()
        if self.instructions_list.count() == 0:
            ctypes.windll.user32.MessageBoxW(0, "No instructions to delete", "ERROR", 0)
            return

        for instruction in instructions:
           self.instructions_list.takeItem(self.instructions_list.row(instruction))

class IngredientsDialog(QtWidgets.QDialog, ingredientsDlg):
    """ Open IngredientsDialog Dialog Box """
    def __init__(self, recipe_id, recipe_ingredients, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.recipe_id = recipe_id
        self.ingredients_table = self.findChild(QtWidgets.QTableWidget, "ingredients_table")
        self.ingredient_name = self.findChild(QtWidgets.QTextEdit, "ingredient_name")
        self.ingredient_quantity = self.findChild(QtWidgets.QSpinBox, "ingredient_quantity")
        self.ingredient_unit = self.findChild(QtWidgets.QComboBox, "ingredient_unit")
        self.add_ingredient = self.findChild(QtWidgets.QPushButton, "add_ingredient")
        self.add_ingredient.clicked.connect(self.addIngredientToTable)
        self.remove_selected_ingredient = self.findChild(QtWidgets.QPushButton, "remove_selected_ingredient")
        self.remove_selected_ingredient.clicked.connect(self.removeSelectedIngredientFromTable)
        ingredients = ET.fromstring(recipe_ingredients)
        for ingredient in ingredients:
            # widgetItem = QtWidgets.QListWidgetItem(ingredient.text)
            fields = {field.tag:field.text for field in list(ingredient)}
            self.ingredients_table.setRowCount(self.ingredients_table.rowCount() + 1)
            self.ingredients_table.setItem(self.ingredients_table.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(fields['Name']))
            self.ingredients_table.setItem(self.ingredients_table.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(fields['Quantity']))
            self.ingredients_table.setItem(self.ingredients_table.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(fields['Unit']))

        self.dlgButtonBox = self.findChild(QtWidgets.QDialogButtonBox, "buttonBox")
        self.dlgButtonBox.accepted.connect(self.saveIngredients)

    def addIngredientToTable(self):
        ingredientsTable = self.ingredients_table
        newIngredientName = self.ingredient_name.toPlainText()
        newIngredientQuantity = self.ingredient_quantity.value()
        newIngredientUnit = self.ingredient_unit.currentText()
        if newIngredientName != "" and newIngredientQuantity != "" and newIngredientUnit != "":
            ingredientsTable.setRowCount(ingredientsTable.rowCount() + 1)
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(newIngredientName))
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(str(newIngredientQuantity)))
            ingredientsTable.setItem(ingredientsTable.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(newIngredientUnit))

    def removeSelectedIngredientFromTable(self):
        ingredientsTable = self.ingredients_table
        if ingredientsTable.currentRow() != None:
            currentRow = ingredientsTable.currentRow()
            ingredientsTable.removeRow(currentRow)
        else: ctypes.windll.user32.MessageBoxW(0, "Please select a row to remove", "ERROR", 0)

    def saveIngredients(self):
        ingredients_widget = self.ingredients_table
        if ingredients_widget.rowCount() == 0:
            ctypes.windll.user32.MessageBoxW(0, "You need ingredients for a meal!", "ERROR", 0)
            return

        ingredients_root = ET.fromstring("<Ingredients></Ingredients>")
        for row in range(0, ingredients_widget.rowCount()):
            ingredient_name = ingredients_widget.item(row, 0).text()
            ingredient_quantity = ingredients_widget.item(row, 1).text()
            ingredient_unit = ingredients_widget.item(row, 2).text()
            ingredient_form = 'na'
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

        new_data = {
            "field": "Ingredients",
            "value": ET.tostring(ingredients_root).decode('utf-8')
        }
        req = Request('http://127.0.0.1:5000/update_recipe/{0}'.format(self.recipe_id))
        req.add_header('Content-Type', 'application/json')
        response = urlopen(req, json.dumps(new_data).encode('utf8'))

class Crumby(QtWidgets.QMainWindow, mainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        mainWindow.__init__(self)
        self.setupUi(self)

        # Sending HTTP request to Crumby API
        req = Request('http://127.0.0.1:5000/crumbs/')
        apidata = json.loads(urlopen(req).read().decode('utf-8'))
        data = [list(v.values()) for v in list(apidata.values())]
        self.ids = [id for id in list(apidata.keys())]
        self.names = [row[3] for row in data]
        self.descriptions = [row[0] for row in data]
        self.ingredient_lists = [row[1] for row in data]
        self.instruction_lists = [row[2] for row in data]
        self.model = CrumbsModel(self.names)
        self.crumby_recipe_name = self.findChild(QtWidgets.QLabel, 'crumby_recipe_name')
        self.reload_button = self.findChild(QtWidgets.QPushButton, 'reload_button')
        self.reload_button.clicked.connect(self.reloadData)
        self.ingredients_button = self.findChild(QtWidgets.QPushButton, 'ingredients_button')
        self.ingredients_button.clicked.connect(self.showIngredients)
        self.instructions_button = self.findChild(QtWidgets.QPushButton, 'instructions_button')
        self.instructions_button.clicked.connect(self.showInstructions)
        self.crumbs_list_view.setModel(self.model)
        self.crumbs_list_view.selectionModel().selectionChanged.connect(self.showRecipe)
        self.show()

    def showRecipe(self):
        indices = self.crumbs_list_view.selectionModel().currentIndex()
        self.crumby_recipe_name.setText(indices.data())
        self.crumby_recipe_description.setText(self.descriptions[indices.row()])

    def reloadData(self):
        req = Request('http://127.0.0.1:5000/crumbs/')
        apidata = json.loads(urlopen(req).read().decode('utf-8'))
        data = [list(v.values()) for v in list(apidata.values())]
        self.ids = [id for id in list(apidata.keys())]
        self.names = [row[3] for row in data]
        self.descriptions = [row[0] for row in data]
        self.ingredient_lists = [row[1] for row in data]
        self.instruction_lists = [row[2] for row in data]

    def showIngredients(self):
        indices = self.crumbs_list_view.selectionModel().currentIndex()
        dlg = IngredientsDialog(self.ids[indices.row()], self.ingredient_lists[indices.row()])
        dlg.exec_()
        self.reloadData()

    def showInstructions(self):
        indices = self.crumbs_list_view.selectionModel().currentIndex()
        dlg = InstructionsDialog(self.ids[indices.row()], self.instruction_lists[indices.row()])
        dlg.exec_()
        self.reloadData()

app = QtWidgets.QApplication(sys.argv)
window = Crumby()
window.show()
sys.exit(app.exec_())
