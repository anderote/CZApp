import sys, os, logging
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QSpacerItem, QSizePolicy, QPushButton, QFileDialog, QSlider, QListWidget)

from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pylab import cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from CZParser import Parser
from CZMathematics import Dataset

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.title = 'CZBiohub Plotting App'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.function_list = []
        self.current_function_idx = 0
        self.function_list_widget = QListWidget()
        self.dataset_list = []
        self.current_dataset_idx = 0
        self.dataset_list_widget = QListWidget()

        self.statusBar().showMessage('Ready')

        # questionable about putting domain here but it is workable for now
        # potential improvement in making a list of domains for true generality
        self.domain = np.arange(100)

        #TODO: suppress matplotlib logging output
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename= os.getcwd() + '/temp/CZApp.log',
                            filemode='w')

        self.uiSetup()

    def uiSetup(self):
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(False)
        file_menu = main_menu.addMenu('File')

        # Definitions for menu bar at top of window
        exit_button = QAction(QIcon('exit24.png'), 'Exit', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Exit application')
        exit_button.triggered.connect(self.close)

        load_button = QAction('Load Functions', self)
        load_button.setShortcut('Ctrl+L')
        load_button.setStatusTip('Load functions from a file')
        load_button.triggered.connect(self.load_functions)

        save_func_button = QAction('Save Functions', self)
        save_func_button.setShortcut('Ctrl+F')
        save_func_button.setStatusTip('Save functions to a file')
        save_func_button.triggered.connect(self.save_functions)

        save_data_button = QAction('Save Datasets', self)
        save_data_button.setShortcut('Ctrl+D')
        save_data_button.setStatusTip('Save datasets to a file')
        save_data_button.triggered.connect(self.save_datasets)

        file_menu.addAction(exit_button)
        file_menu.addAction(load_button)
        file_menu.addAction(save_func_button)
        file_menu.addAction(save_data_button)

        # Layout definitions for widgets
        widget = QWidget(self)
        self.setCentralWidget(widget)

        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout()
        vlay.addLayout(hlay)

        hlay.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))

        # buttons for manipulating the function plotting settings

        plotsel_button = QPushButton('Plot Selected', self)
        plotsel_button.clicked.connect(self.plot_selected_dataset)

        generate_button = QPushButton('Generate', self)
        generate_button.clicked.connect(self.generate_data)

        hlay2 = QHBoxLayout()
        hlay2.addWidget(generate_button)
        hlay2.addWidget(plotsel_button)
        hlay2.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))
        vlay.addLayout(hlay2)

        self.plotting_window = Plotter(self)
        vlay.addWidget(self.function_list_widget)
        vlay.addWidget(self.dataset_list_widget)
        vlay.addWidget(self.plotting_window)

        # Connect list widget functionality, where clicking once shows name of the function in status bar
        # and clicking twice plots the function over a range specified by input domain

        self.function_list_widget.itemClicked.connect(self.function_clicked)
        #self.function_list_widget.itemDoubleClicked.connect(self.listItemDoubleClicked)

    def load_functions(self):
        """
        Populates the list of functions with function objects as read from a .json file
        """
        file_name, _ = QFileDialog.getOpenFileName(self, 'Single File', os.getcwd(), '*.json')
        parser = Parser(file_name)

        for idx, _ in enumerate(parser.functions):
            function = parser.returnFunction(idx)
            self.function_list.append(function)
            # TODO: implement a table instead of a list that also shows function names / parameters / desc
            self.function_list_widget.addItem(function.get_raw())

        self.statusBar().showMessage("Loaded functions from " + file_name)

    def function_clicked(self):
        """
        Selects the function for generating datasets and displays function information in the status bar
        """

        self.current_function_idx = self.function_list_widget.currentRow()

        current_fun = self.function_list[self.current_function_idx]
        display_message = current_fun.get_name()
        self.statusBar().showMessage(display_message)
        #
        # if "A_desc" in current_fun.keys():
        #     display_message = display_message + ", A =" + current_fun.get_description("A")
        # if "B_desc" in current_fun.keys():
        #     display_message = display_message + ", B =" + current_fun.get_description("B")
        #
        # self.statusBar().showMessage(display_message)

    def generate_data(self):
        """
        Applies the current function to the current domain and adds a dataset object to the list of datasets
        """
        fun = self.function_list[self.current_function_idx]
        data = fun.evaluate(self.domain)
        data_name = (fun.get_name() + '_' + str(np.min(self.domain)) +
                     '_to_' + str(np.max(self.domain)))
        dataset = Dataset(data_name, self.domain, data)
        self.statusBar().showMessage("Generated dataset " + data_name)

        self.dataset_list.append(dataset)
        self.dataset_list_widget.addItem(data_name)

    def dataset_clicked(self):
        self.current_dataset_idx = self.dataset_list_widget.currentRow()
        dataset = self.dataset_list[self.current_dataset_idx]
        self.statusBar().showMessage("Dataset " + dataset.name + " generated at " + dataset.timestamp)

    def plot_selected_dataset(self):
        dataset = self.dataset_list[self.current_dataset_idx]
        self.plotting_window.canvas.plot(dataset)


    def listItemDoubleClicked(self):
        """
        Evaluates the current function at the current domain and displays results in the plotting window
        :param item: function definition which was just double-clicked
        """
        '''
        self.current_function_idx = self.function_list_widget.currentRow()
        current_fun = self.function_list(self.current_function_idx)

        try:
            y_vals = current_fun(np.arange(100))
        except:
            logging.error("Failed to evaluate function")
        self.plotting_window.canvas.plot(np.sin(y_vals), "Blank")

        # self.plotting_window.canvas.plot(y_vals, "Blank")  # self.parser.functions[self.current_function_idx]["name"])
        '''

    def clear_plots(self):
        """
        Resets the Plotter
        :return:
        """
        self.plotting_window = Plotter()

    def save_functions(self):
        """
        Saves the current list of functions to the to a .json file in the cwd, with user prompt for name entry

        """

    def save_datasets(self):
        """
        Saves the current list of datasets to a .json file in the cwd, with user prompt for name entry
        :return:
        """


class Plotter(QWidget):
    """
    Also provides matplotlib built-in toolbar for panning, viewing, saving views, etc.

    #TODO: Implement clearing, saving, loading plots.
    """
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self, width=10, height=8)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)


class PlotCanvas(FigureCanvas):
    """
    Provides basic plotting functionality
    # TODO: Implement an optional legend that can be turned on or off
    """
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.add_gridspec(5, 5)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.dataset_list = []
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    # TODO: Implement handling multiple plots on the same window
    def plot(self, dataset):
        """
        Plots data with label for legend
        """
        self.dataset_list.append(dataset)
        n = len(self.dataset_list)
        axes_list =[]
        color = cm.rainbow(np.linspace(0,1,n))

        for idx, dataset in enumerate(self.dataset_list):
            axes_list.append(self.figure.add_subplot(1, 1, 1))

        for idx, ax in enumerate(axes_list):
            ax.plot(self.dataset_list[idx].x_data, self.dataset_list[idx].y_data, c=color[idx],
                    label=self.dataset_list[idx].name)

        # ax = self.figure.add_subplot(111)
        # ax.plot(dataset.x_data, dataset.y_data, 'r-', linewidth=1, label=dataset.name)
        self.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_())