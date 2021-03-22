from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from designer.data_processing_configuration_form import Ui_dataProcessingConfigurationForm

class DenoisingConfigWidget(qtw.QWidget):
    submitted = qtc.pyqtSignal(str, int)
    def __init__(self):
        super().__init__()
        self.form = Ui_dataProcessingConfigurationForm()
        self.form.setupUi(self)
        self.form.pushButton.clicked.connect(self.apply_denoise)

    def apply_denoise(self):
        self.submitted.emit(self.form.waveletStrLineEd.text(), self.form.decomposeLvlSpinBox.value())
