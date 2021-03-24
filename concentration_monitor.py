from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtChart as qtch

from designer.concentration_form import Ui_ConcentrationForm


class ConcentrationMonitor(qtw.QMainWindow):
    startSignal = qtc.pyqtSignal(int)
    stopSignal = qtc.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.classification_session_started = False

        central_wdg = qtw.QWidget()
        self.setCentralWidget(central_wdg)

        layout = qtw.QGridLayout()
        central_wdg.setLayout(layout)

        self.settings_form = Ui_ConcentrationForm()
        settings_wdg = qtw.QWidget()
        settings_wdg.setMinimumSize(200, 75)
        self.settings_form.setupUi(settings_wdg)
        layout.addWidget(settings_wdg, 0, 0)

        self.value_graph = ConcentrationValueMonitor()
        self.bandpower_graph = BandPowerMonitor()

        layout.addWidget(self.value_graph, 1, 0)
        layout.addWidget(self.bandpower_graph, 1, 1)

        self.settings_form.startToggleBtn.clicked.connect(self.start_toggle)

    def start_toggle(self):
        if self.classification_session_started:
            self.stopSignal.emit()
            self.settings_form.startToggleBtn.setText('Continue')
            self.classification_session_started = False
        else:
            interval = int(self.settings_form.intervalSpinBox.value()*1000)
            print('classification interval:', interval)
            self.startSignal.emit(interval)
            self.settings_form.startToggleBtn.setText('Stop')
            self.classification_session_started = True


class ConcentrationValueMonitor(qtch.QChartView):
    chart_title = 'Concentration Value'
    num_data_points = 25
    offset = 2

    def __init__(self):
        super().__init__()
        chart = qtch.QChart(title=self.chart_title)
        self.setChart(chart)
        self.series = qtch.QLineSeries(name="Percentage")
        chart.addSeries(self.series)

        self.last_x = 0

        self.x_axis = qtch.QValueAxis()
        self.x_axis.setLabelFormat('%i')
        self.x_axis.setRange(0, self.num_data_points+self.offset)

        y_axis = qtch.QValueAxis()
        y_axis.setRange(0, 1)

        chart.setAxisX(self.x_axis, self.series)
        chart.setAxisY(y_axis, self.series)

        self.setRenderHint(qtg.QPainter.Antialiasing)

    def update(self, nval):
        self.last_x += 1
        if self.last_x > self.num_data_points:
            self.x_axis.setRange(self.last_x-self.num_data_points, self.last_x+self.offset)
        self.series.append(self.last_x, nval)


class BandPowerMonitor(qtch.QChartView):
    chart_title = 'Average Frequencies Band Power'

    def __init__(self):
        super().__init__()

        chart = qtch.QChart(title=self.chart_title)
        self.setChart(chart)

        self.series = qtch.QBarSeries()
        chart.addSeries(self.series)
        self.bar_set = qtch.QBarSet('Average Band Power')
        self.series.append(self.bar_set)

        # theta:4-8, 8-12, 12-30
        partitions = ['Theta', 'Alpha', 'Beta']
        self.bar_set.append(0)
        self.bar_set.append(0)
        self.bar_set.append(0)

        x_axis = qtch.QBarCategoryAxis()
        x_axis.append(partitions)
        chart.setAxisX(x_axis)
        self.series.attachAxis(x_axis)

        y_axis = qtch.QValueAxis()
        y_axis.setRange(0, 120)
        chart.setAxisY(y_axis)
        self.series.attachAxis(y_axis)
        self.series.setLabelsVisible(True)

    def update(self, ntheta, nalpha, nbeta):
        self.bar_set.replace(0, ntheta)
        self.bar_set.replace(1, nalpha)
        self.bar_set.replace(2, nbeta)
