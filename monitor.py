import sys
import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import pyqtgraph as qtgr


class Monitor(qtgr.GraphicsWindow):

    def __init__(self, title):
        super().__init__(title)

        qtgr.setConfigOptions(antialias=True)
        # qtgr.setConfigOption('background', 'k')
        # qtgr.setConfigOption('foreground', 'w')
        qtgr.setConfigOption('useOpenGL', True)

        self.traces = dict()
        self.psd_traces = dict()

        proxy = qtw.QGraphicsProxyWidget()
        self.resize(1200, 900)

        self.reset_plots_onclose = False
        self.is_running = False

        # Waveform plot parameters
        xrange = 1500

        self.x = list(range(0, xrange))
        self.ch1data = [0] * xrange
        self.ch2data = [0] * xrange
        self.ch3data = [0] * xrange
        self.ch4data = [0] * xrange
        self.ch5data = [0] * xrange
        self.ch6data = [0] * xrange
        self.ch7data = [0] * xrange
        self.ch8data = [0] * xrange

        self.graph_ch1 = self.addPlot(title='Channel1', row=1, col=1)
        self.graph_ch2 = self.addPlot(title='Channel2', row=2, col=1)
        self.graph_ch3 = self.addPlot(title='Channel3', row=3, col=1)
        self.graph_ch4 = self.addPlot(title='Channel4', row=4, col=1)
        self.graph_ch5 = self.addPlot(title='Channel5', row=5, col=1)
        self.graph_ch6 = self.addPlot(title='Channel6', row=1, col=2)
        self.graph_ch7 = self.addPlot(title='Channel7', row=2, col=2)
        self.graph_ch8 = self.addPlot(title='Channel8', row=3, col=2)

        # PSD parameters
        self.graph_psd = self.addPlot(title='PSD', row=4, col=2, colspan=1, rowspan=2)
        self.graph_psd.setRange(yRange=[0, 5])


    def start(self):
        self.is_running = True
        if (sys.flags.interactive != 1) or not hasattr(qtc, 'PYQT_VERSION'):
            qtg.QApplication.instance().exec_()

    def set_waveform_plot(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'Channel1':
                self.traces[name] = self.graph_ch1.plot(pen='c', width=1)
            if name == 'Channel2':
                self.traces[name] = self.graph_ch2.plot(pen='m', width=1)
            if name == 'Channel3':
                self.traces[name] = self.graph_ch3.plot(pen='g', width=1)
            if name == 'Channel4':
                self.traces[name] = self.graph_ch4.plot(pen='r', width=1)
            if name == 'Channel5':
                self.traces[name] = self.graph_ch5.plot(pen='b', width=1)
            if name == 'Channel6':
                self.traces[name] = self.graph_ch6.plot(pen='w', width=1)
            if name == 'Channel7':
                self.traces[name] = self.graph_ch7.plot(pen='y', width=1)
            if name == 'Channel8':
                self.traces[name] = self.graph_ch8.plot(pen=qtgr.mkPen(color=(135, 100, 35)), width=1)


    def update_waveform(self, stream_data):
        #TODO: update plots
        data_size = len(stream_data[0])

        # update x data
        xadd = list(range(self.x[-1], self.x[-1]+data_size))
        self.x = self.x[data_size:]
        self.x.extend(xadd)

        # update channel 1
        self.ch1data.extend(stream_data[0])
        self.ch1data = self.ch1data[data_size:]
        self.set_waveform_plot(name="Channel1", data_x=self.x, data_y=self.ch1data)

        # update channel 2
        self.ch2data.extend(stream_data[1])
        self.ch2data = self.ch2data[data_size:]
        self.set_waveform_plot(name="Channel2", data_x=self.x, data_y=self.ch2data)

        # update channel 3
        self.ch3data.extend(stream_data[2])
        self.ch3data = self.ch3data[data_size:]
        self.set_waveform_plot(name="Channel3", data_x=self.x, data_y=self.ch3data)

        # update channel 4
        self.ch4data.extend(stream_data[3])
        self.ch4data = self.ch4data[data_size:]
        self.set_waveform_plot(name="Channel4", data_x=self.x, data_y=self.ch4data)

        # update channel 5
        self.ch5data.extend(stream_data[4])
        self.ch5data = self.ch5data[data_size:]
        self.set_waveform_plot(name="Channel5", data_x=self.x, data_y=self.ch5data)

        # update channel 6
        self.ch6data.extend(stream_data[5])
        self.ch6data = self.ch6data[data_size:]
        self.set_waveform_plot(name="Channel6", data_x=self.x, data_y=self.ch6data)

        # update channel 7
        self.ch7data.extend(stream_data[6])
        self.ch7data = self.ch7data[data_size:]
        self.set_waveform_plot(name="Channel7", data_x=self.x, data_y=self.ch7data)

        # update channel 8
        self.ch8data.extend(stream_data[7])
        self.ch8data = self.ch8data[data_size:]
        self.set_waveform_plot(name="Channel8", data_x=self.x, data_y=self.ch8data)

    def set_psd_plot(self, name, data_x, data_y):
        if name in self.psd_traces:
            self.psd_traces[name].setData(data_x, data_y)
        else:
            if name == 'Channel1':
                self.psd_traces[name] = self.graph_psd.plot(pen='c', width=1)
            if name == 'Channel2':
                self.psd_traces[name] = self.graph_psd.plot(pen='m', width=1)
            if name == 'Channel3':
                self.psd_traces[name] = self.graph_psd.plot(pen='g', width=1)
            if name == 'Channel4':
                self.psd_traces[name] = self.graph_psd.plot(pen='r', width=1)
            if name == 'Channel5':
                self.psd_traces[name] = self.graph_psd.plot(pen='b', width=1)
            if name == 'Channel6':
                self.psd_traces[name] = self.graph_psd.plot(pen='w', width=1)
            if name == 'Channel7':
                self.psd_traces[name] = self.graph_psd.plot(pen='y', width=1)
            if name == 'Channel8':
                self.psd_traces[name] = self.graph_psd.plot(pen=qtgr.mkPen(color=(135, 100, 35)), width=1)

    def update_psd(self, x_data, y_data):
        self.set_psd_plot(name="Channel1", data_x=x_data, data_y=y_data[0])
        self.set_psd_plot(name="Channel2", data_x=x_data, data_y=y_data[1])
        self.set_psd_plot(name="Channel3", data_x=x_data, data_y=y_data[2])
        self.set_psd_plot(name="Channel4", data_x=x_data, data_y=y_data[3])
        self.set_psd_plot(name="Channel5", data_x=x_data, data_y=y_data[4])
        self.set_psd_plot(name="Channel6", data_x=x_data, data_y=y_data[5])
        self.set_psd_plot(name="Channel7", data_x=x_data, data_y=y_data[6])
        self.set_psd_plot(name="Channel8", data_x=x_data, data_y=y_data[7])