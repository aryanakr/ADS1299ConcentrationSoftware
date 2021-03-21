from PyQt5 import QtWidgets as qtw
from designer.serial_connection_form import Ui_serialConnectionForm

class SerialConnectionWidget(qtw.QWidget):

    def __init__(self):
        super().__init__()
        self.form = Ui_serialConnectionForm()
        self.form.setupUi(self)

    def getPort(self):
        return self.form.serialPortInput.text()

    def getId(self):
        return self.form.idInput.text()