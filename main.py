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
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams

import pandas as pd
import numpy as np

from serial_connection import SerialConnectionWidget
from monitor import Monitor
from concentration_monitor import ConcentrationMonitor
from denoising_config import DenoisingConfigWidget
from dmc_mod import DMCMod

class SessionMainWindow(qtw.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Brainflow Concentration Visualization Software')

        # Brainflow Parameters
        self.board = None
        self.board_id = 0
        self.params = BrainFlowInputParams()
        self.board_available = False

        self.initial_sleep = 7
        # Initialize Widgets and Windows
        self.serial_connection_wdg = SerialConnectionWidget()
        self.serial_connection_wdg.form.startButton.clicked.connect(self.initialize_serial_session)

        self.denoising_wdg = DenoisingConfigWidget()
        self.denoising_wdg.submitted.connect(self.apply_denoising_config)

        self.dmc_mod_window = DMCMod()
        # Initialize Monitors
        self.raw_monitor = Monitor('Session Raw Monitor')
        self.processed_monitor = Monitor('Session Processed Monitor')
        self.concentration_monitor = ConcentrationMonitor()

        # MenuBar Initialization
        menubar = self.menuBar()

        options_menu = menubar.addMenu('Options')
        options_menu.addAction('Serial', self.serial_connection_wdg.show)
        options_menu.addAction('Synthetic', self.initialize_synthetic_session)
        options_menu.addAction('Denoising Configuration', self.denoising_wdg.show)

        # TODO: Add Monitor menu
        # TODO: Add concentration menu
        concentration_menu = menubar.addMenu('Concentration')
        concentration_menu.addAction('Monitor', self.concentration_monitor.show)

        games_menu = menubar.addMenu('Game Mods')
        games_menu.addAction('DMC5', self.dmc_mod_window.show)

        self.session_timer = qtc.QTimer()
        self.session_timer.timeout.connect(self.session_update)

        self.is_buffers_initialized = False
        self.data_buffer = None
        self.processed_buffer = None

        # Denoising params
        self.denoising_method = ''
        self.denoising_decompose_level = 0

        # Classification params
        self.power_2_of = 0
        self.classification_timer = qtc.QTimer()
        self.classification_timer.timeout.connect(self.concentration_classification)

        self.concentration_monitor.startSignal.connect(self.classification_timer.start)
        self.concentration_monitor.stopSignal.connect(self.classification_timer.stop)

        self.show()

    def concentration_classification(self):
        master_board_id = int(self.board_id)
        sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        eeg_channels = BoardShim.get_eeg_channels(master_board_id)
        nfft = DataFilter.get_nearest_power_of_two(sampling_rate)

        # Get band powers
        tmp_buffer = self.processed_buffer.copy()
        bp_buffer = tmp_buffer[:, -self.power_2_of:]
        theta_sum = 0
        alpha_sum = 0
        beta_sum = 0

        for i in range(8):
            current_channel = eeg_channels[i]
            # optional detrend
            DataFilter.detrend(bp_buffer[current_channel], DetrendOperations.LINEAR.value)
            psd = DataFilter.get_psd_welch(bp_buffer[current_channel], nfft, nfft // 2, sampling_rate,
                                           WindowFunctions.BLACKMAN_HARRIS.value)

            theta_sum += DataFilter.get_band_power(psd, 3.0, 7.0)
            alpha_sum += DataFilter.get_band_power(psd, 8.0, 13.0)
            beta_sum += DataFilter.get_band_power(psd, 14.0, 30.0)

        # Update band power monitor
        self.concentration_monitor.bandpower_graph.update(theta_sum/8, alpha_sum/8, beta_sum/8)

        # Concentration Classification
        bands = DataFilter.get_avg_band_powers(self.processed_buffer, eeg_channels, sampling_rate, True)
        feature_vector = np.concatenate((bands[0], bands[1]))
        print(feature_vector)
        # KNN, SWM, REGRESSION
        concentration_params = BrainFlowModelParams(BrainFlowMetrics.CONCENTRATION.value, BrainFlowClassifiers.KNN.value)
        concentration = MLModel(concentration_params)
        concentration.prepare()
        print(self.processed_buffer.shape)
        concentration_result = concentration.predict(feature_vector)
        print('Concentration: %f' % concentration_result)
        concentration.release()

        # Update Value monitor
        self.concentration_monitor.value_graph.update(concentration_result)
        self.dmc_mod_window.current_eeg_concentration = concentration_result
        #self.classification_buffer_initialized = False
        # self.classification_buffer = None


    def apply_denoising_config(self, wavelet, decompose):
        self.denoising_method = wavelet
        self.denoising_decompose_level = decompose

    def session_update(self):
        # print('session update')

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

        # board params
        sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        eeg_channels = BoardShim.get_eeg_channels(self.board_id)
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
        self.power_2_of = firstPowerOf2

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
        if self.denoising_method == '':
            for count, channel in enumerate(eeg_channels):
                DataFilter.perform_rolling_filter(self.processed_buffer[channel], 3, AggOperations.MEAN.value)
        else:
            for count, channel in enumerate(eeg_channels):
                DataFilter.perform_wavelet_denoising(self.processed_buffer[channel], self.denoising_method, self.denoising_decompose_level)

        # Update processed monitor
        # Update waveform monitors
        processed_data = []
        for count, channel in enumerate(eeg_channels):
            processed_data.append(self.processed_buffer[channel, -current_data.shape[1]:])
        self.processed_monitor.update_waveform(processed_data)

        # Update PSD monitor
        tmp_buffer = self.processed_buffer.copy()
        psd_buffer = tmp_buffer[:, -firstPowerOf2:]

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
        time.sleep(7)
        self.board_available = True
        self.session_timer.start(40)
        self.serial_connection_wdg.close()

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