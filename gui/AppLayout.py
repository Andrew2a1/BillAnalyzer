from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

from gui.ProductListWidget import ProductListWidget
from gui.ActionButtonsWidget import ActionButtonsWidget
from gui.ResultsPopup import ResultsPopup
from gui.OptionsPopup import OptionsPopup
from gui.LoadDialog import LoadDialog
from gui.MessageBox import MessageBox

from ShoppingListGenerator import ShoppingListGenerator
from Options import Options

import TextFormatter
import os

class AppLayout(FloatLayout):
    realSumInput = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._popup = None
        self.options = Options()

        self.__bindActionButtons()
        self.realSumInput.bind(focus = self.validateExpectedCosts)

    def __bindActionButtons(self):
        buttons = self.ids.actionButtons.ids
        buttons.button_generate.bind(on_release = self.parseFileCallback)
        buttons.button_clear.bind(on_release = self.clearCallback)
        buttons.button_options.bind(on_release = self.optionsCallback)
        buttons.button_results.bind(on_release = self.resultsCallback)

    def validateExpectedCosts(self, instance, value):
        if value:
            return

        costs = instance.text

        try:
            costs = float(costs.replace(",", "."))
        except ValueError:
            costs = 0

        self.ids.productList.expectedSum = costs
        self.updateTotalCosts()

    def update(self, instance, value):
        self.updateTotalCosts()

    def updateTotalCosts(self):
        self.ids.totalSumLabel.text = "Total sum: {0:.2f}".format(self.ids.productList.getTotalSum())
        self.realSumInput.text = "{0:.2f}".format(self.ids.productList.getRealSum())

    def parseFileCallback(self, event):
        filename = self.ids.file_input.text.strip()

        if not filename:
            return

        person_names = self.options.getPersons()
        generator = ShoppingListGenerator(person_names)

        try:
            shoppingList = generator.generateFromImage(filename)
        except Exception as e:
            self.notifyParserError(str(e))
            return

        if not shoppingList.realSum:
            self.notifyBadExpectedSum()
    
        self.ids.productList.addShoppingList(shoppingList)
        self.ids.productList.attachObserver(self)
        self.updateTotalCosts()

    def clearCallback(self, event):
        self.ids.productList.clear()
        self.updateTotalCosts()

    def optionsCallback(self, event):
        content = OptionsPopup(self.options, cancel = self.dismiss_popup)
        self._popup = Popup(title = "Options", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()
        
    def resultsCallback(self, event):
        content = ResultsPopup(cancel = self.dismiss_popup)
        content.text = "\n".join("{0} = {1:.2f}".format(person, sum) for person,sum
                                     in self.ids.productList.getBill().items())

        if not content.text:
            content.text = "No Results"

        self._popup = Popup(title = "Results", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()

    def notifyParserError(self, detailed_desc = ""):
        desc = "Cannot parse image file, " \
               "please make sure that " \
               "your bill scan is readable - {0}".format(detailed_desc)
                             
        content = MessageBox(text = TextFormatter.breakByWords(desc, 24),
                             ok = self.dismiss_popup) 

        self._popup = Popup(title = "Error", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()
   
    def notifyBadExpectedSum(self):
        content = MessageBox(text = "Cannot get real sum from image,\n"
                                    " you may want to change it manually",
                             ok = self.dismiss_popup)

        self._popup = Popup(title = "Warning", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()

    def loadFilePopup(self):
        content = LoadDialog(load = self.__getFilename, cancel = self.dismiss_popup)
        self._popup = Popup(title = "Load file", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()

    def __getFilename(self, path, filename):
        if filename:
            self.ids.file_input.text = os.path.join(path, filename[0])
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()

    