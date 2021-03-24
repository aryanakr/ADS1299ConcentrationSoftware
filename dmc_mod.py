from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtChart as qtch

from ReadWriteMem import ReadWriteMemory

from designer.dmc_mod_from import Ui_DmcEegModForm


class DMCMod(qtw.QMainWindow):

    def __init__(self):
        super().__init__()

        # Window Initialization
        self.setWindowTitle('DMC5 EEG Concentration Mod')
        central_wdg = qtw.QWidget()
        self.setCentralWidget(central_wdg)
        self.mod_form = Ui_DmcEegModForm()
        self.mod_form.setupUi(central_wdg)
        self.status = qtw.QStatusBar()
        self.setStatusBar(self.status)

        self.is_connected = False
        self.is_injecting = False
        self.current_eeg_concentration = 0.6

        # Read Write Memory params
        self.rwm = ReadWriteMemory()
        self.process = None
        self.concentration_ptr = None

        # Buttons Trigger
        self.mod_form.connectBtn.clicked.connect(self.connect)
        self.mod_form.setValBtn.clicked.connect(self.form_set_value)
        self.mod_form.startBtn.clicked.connect(self.execute_injection)

        self.concentration_update_value = 0

        # Timers
        self.value_update_timer = qtc.QTimer()
        self.value_update_timer.timeout.connect(self.update_value)
        self.injection_timer = qtc.QTimer()
        self.injection_timer.timeout.connect(self.inject_value)

    def inject_value(self):
        # TODO: check if in combat
        self.write_dmc_concentration(self.concentration_update_value)

    def update_value(self):
        print('update dmc5')
        # calculate update value
        dmc_concentration = self.read_dmc_concentration()
        update_value = self.current_eeg_concentration - self.mod_form.thrSpinBox.value()
        if update_value > 0:
            update_value *= self.mod_form.addSpinBox.value()
        else:
            update_value *= self.mod_form.subSpinBox.value()

        next_concentration_value = dmc_concentration + update_value
        if next_concentration_value > 300:
            next_concentration_value = 300
        elif next_concentration_value < 0:
            next_concentration_value = 0

        # update status values
        self.mod_form.concentrationLabel.setText(str(self.current_eeg_concentration))
        self.mod_form.updateLabel.setText(str(update_value))
        self.mod_form.gameLabel.setText(str(dmc_concentration))
        self.mod_form.nextGameLabel.setText(str(next_concentration_value))

        # update game value
        self.concentration_update_value = next_concentration_value


    def execute_injection(self):
        if not self.is_connected:
            print('not connected to game')
            return
        if not self.is_injecting:
            print('start inject')
            update_interval = self.mod_form.valUpdateIntervalSpinBox.value()
            inject_interval = self.mod_form.injectIntervalSpinBox.value()
            self.value_update_timer.start(update_interval)
            self.injection_timer.start(inject_interval)
            self.mod_form.startBtn.setText('Stop Injection')
            self.mod_form.connectBtn.setDisabled(True)
            self.is_injecting = True
        else:
            self.value_update_timer.stop()
            self.injection_timer.stop()
            self.mod_form.connectBtn.setDisabled(False)
            self.mod_form.startBtn.setText('Start Injection')
            self.is_injecting = False

    def form_set_value(self):
        val = self.mod_form.valSpinBox.value()
        self.concentration_update_value = val
        if self.is_connected:
            self.write_dmc_concentration(val)
            # update status values
            self.mod_form.concentrationLabel.setText(str(self.current_eeg_concentration))
            self.mod_form.updateLabel.setText(str(0))
            self.mod_form.gameLabel.setText(str(val))
            self.mod_form.nextGameLabel.setText(str(val))

    # Base Methods
    def connect(self):
        if not self.is_connected:
            self.process = self.rwm.get_process_by_name('DevilMayCry5.exe')
            self.process.open()

            # Get concentration pointer
            base_offset = 0X7E61B90
            module_addr = int(str(self.process.base_addr), 0) + int(str(base_offset), 0)
            self.concentration_ptr = self.process.get_pointer(lp_base_address=module_addr, offsets=[0x78, 0x1B50])

            # TODO: Get in combat ptr
            self.is_connected = True
            self.mod_form.connectBtn.setText('Disconnect')
            print('connection to dmc5')
        else:
            self.process.close()
            self.is_connected = False
            self.mod_form.connectBtn.setText('Connect')
            print('disconnect from dmc5')

    def read_dmc_concentration(self):
        con_val = self.process.read_float(self.concentration_ptr)
        print('Read concentration:', con_val)
        return con_val

    def write_dmc_concentration(self, val):
        state = self.process.write(self.concentration_ptr, val)
        print('write concentration state:', state)

    def closeEvent(self, event):
        if self.is_connected:
            self.process.close()
            self.is_connected = False
