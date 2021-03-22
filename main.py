import sys
import os
import time
from random import randrange

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams

import pandas as pd
import numpy as np

from serial_connection import SerialConnectionWidget
from monitor import Monitor
from denoising_config import DenoisingConfigWidget

class SessionMainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Brainflow Concentration Visualization Software')

        # Brainflow Parameters
        self.board = None
        self.params = BrainFlowInputParams()
        self.board_available = False

        self.initial_sleep = 4
        # Initialize Widgets and Windows
        self.serial_connection_wdg = SerialConnectionWidget()
        self.serial_connection_wdg.form.startButton.clicked.connect(self.initialize_serial_session)

        self.denoising_wdg = DenoisingConfigWidget()
        self.denoising_wdg.submitted.connect(self.apply_denoising_config)

        # Initialize Monitors
        self.raw_monitor = Monitor('Session Raw Monitor')
        self.processed_monitor = Monitor('Session Processed Monitor')

        # MenuBar Initialization
        menubar = self.menuBar()

        options_menu = menubar.addMenu('Options')
        options_menu.addAction('Serial', self.serial_connection_wdg.show)
        options_menu.addAction('Synthetic', self.initialize_synthetic_session)
        options_menu.addAction('Denoising Configuration', self.denoising_wdg.show)


        self.session_timer = qtc.QTimer()
        self.session_timer.timeout.connect(self.session_update)

        self.is_buffers_initialized = False
        self.data_buffer = None
        self.processed_buffer = None

        # Denoising params
        self.denoising_method = ''
        self.denoising_decompose_level = 0

        self.show()

    def apply_denoising_config(self, wavelet, decompose):
        self.denoising_method = wavelet
        self.denoising_decompose_level = decompose

    def session_update(self):
        # print('session update')
        # board params
        sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        # Get current data
        current_data = self.board.get_board_data()

        # Initialize/update buffer
        if not self.is_buffers_initialized:
            self.is_buffers_initialized = True
            self.data_buffer = current_data
            return
        else:
            self.data_buffer = self.data_buffer[:, current_data.shape[1]:]
            self.data_buffer = np.hstack([self.data_buffer, current_data])

        # Raw data monitor update
        raw_eeg = []
        for count, channel in enumerate(eeg_channels):
            raw_eeg.append(current_data[channel])
            # TODO: Add downsampling

        self.raw_monitor.update_waveform(raw_eeg)

        # Create psd buffer
        # Selectable psd range size
        psd_buffer = self.data_buffer.copy()
        firstPowerOf2 = 1
        nextPowerOf2 = 2
        while nextPowerOf2 < psd_buffer.shape[1]:
            firstPowerOf2 = nextPowerOf2
            nextPowerOf2 = nextPowerOf2 * 2
        psd_buffer = psd_buffer[:, -firstPowerOf2:]

        # Create PSD data
        psd_data = []
        psd_x = []
        for count, channel in enumerate(eeg_channels):
            channel_psd_data = DataFilter.get_psd(psd_buffer[channel], 250, WindowFunctions.BLACKMAN_HARRIS.value)
            if count == 0:
                psd_x = channel_psd_data[1].tolist()
            psd_data.append(channel_psd_data[0].tolist())

        # Update monitor PSD
        self.raw_monitor.update_psd(psd_x, psd_data)

        # Data processing
        self.processed_buffer = self.data_buffer.copy()
        if not self.denoising_method == '':
            for count, channel in enumerate(eeg_channels):
                DataFilter.perform_wavelet_denoising(self.processed_buffer[channel], self.denoising_method, self.denoising_decompose_level)

        # Update processed monitor
        # Update waveform monitors
        processed_data = []
        for count, channel in enumerate(eeg_channels):
            processed_data.append(self.processed_buffer[channel, -current_data.shape[1]:])
        self.processed_monitor.update_waveform(processed_data)

        # Update PSD monitor
        psd_buffer = self.processed_buffer[:, -firstPowerOf2:]

        # Create PSD data
        psd_data = []
        psd_x = []
        for count, channel in enumerate(eeg_channels):
            channel_psd_data = DataFilter.get_psd(psd_buffer[channel], 250, WindowFunctions.BLACKMAN_HARRIS.value)
            if count == 0:
                psd_x = channel_psd_data[1].tolist()
            psd_data.append(channel_psd_data[0].tolist())

        # Update monitor PSD
        self.processed_monitor.update_psd(psd_x, psd_data)


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
        self.session_timer.start(40)

    def initialize_synthetic_session(self):
        print('start synthetic session')
        self.board_id = BoardIds.SYNTHETIC_BOARD.value
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board.start_stream()
        BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
        time.sleep(self.initial_sleep)
        self.board_available = True
        self.session_timer.start(40)

    def closeEvent(self, event):

        if self.board_available:
            self.session_timer.stop()
            time.sleep(1)
            self.board.stop_stream()
            self.board.release_session()
        qtw.QApplication.closeAllWindows()

def main():
    BoardShim.enable_dev_board_logger()
    if sys.platform == 'darwin':
        os.environ['QT_EVENT_DISPATCHER_CORE_FOUNDATION'] = '1'

    app = qtw.QApplication(sys.argv)
    app.setStyle('Fusion') #'Breeze', 'Oxygen', 'QtCurve', 'Windows', 'Fusion'
    mw = SessionMainWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()