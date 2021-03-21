import sys
import os
import time

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams

import pandas as pd
import numpy as np

from serial_connection import SerialConnectionWidget

class SessionMainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Brainflow Concentration Visualization Software')

        # Brainflow Parameters
        self.board = None
        self.params = BrainFlowInputParams()
        self.board_available = False

        # Initialize Widgets and Windows
        self.serial_connection_wdg = SerialConnectionWidget()
        self.serial_connection_wdg.form.startButton.clicked.connect(self.initialize_serial_session)
        self.initial_sleep = 3

        # MenuBar Initialization
        menubar = self.menuBar()

        connection_menu = menubar.addMenu('Connect...')
        connection_menu.addAction('Serial', self.serial_connection_wdg.show)

        self.show()

    def initialize_serial_session(self):
        print('start serial session')
        self.board_id = int(self.serial_connection_wdg.form.idInput.text())
        self.params.serial_port = self.serial_connection_wdg.form.serialPortInput.text()
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board.start_stream()
        BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
        time.sleep(self.initial_sleep)
        self.board_available = True
        # Start Data Flow
        #self.data_update_timer.start(self.data_update_time)
        #self.classification_timer.start(self.classification_time)

    def closeEvent(self, event):
        if self.board_available:
            self.board.stop_stream()
            self.board.release_session()
        qtw.QApplication.closeAllWindows()

def main():
    BoardShim.enable_dev_board_logger()
    if sys.platform == 'darwin':
        os.environ['QT_EVENT_DISPATCHER_CORE_FOUNDATION'] = '1'

    app = qtw.QApplication(sys.argv)
    mw = SessionMainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()