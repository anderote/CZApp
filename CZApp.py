import sys, os, logging
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QAction, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QSpacerItem, QSizePolicy, QPushButton, QFileDialog, QDialog, QListWidget, QGridLayout, QComboBox)

from PyQt5.QtGui import QIcon

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from CZParser import Parser
from CZMathematics import Dataset, Domain, DampedOscillator, UnstableOscillator, Pyramid, InvalidParameter


class MainWindow(QMainWindow):
    """

    Main GUI Window that handles all events and user actions.


    Consists of 6 main parts, arranged schematically in the GUI as follows :
        [Function and domain toolbar ]
        Function list     |    Domain list
        [ Generate Data toolbar ]
        Dataset list
        [ Plotting toolbar]
        Plotting window

    The bottom of the GUI window contains a status bar which is updated whenever a user successfully performs an action,
    or an action fails, and provides relevant information and commentary on likely causes of failure. All
    buttons in the GUI have tooltips which activate upon mouse-hovering. GUI also generates log files in /temp which
    records info, warnings, and errors associated with user actions.

    Important Attributes
    ----
    domain_list: list(Domain)
        List of domains available to functions to take as arguments
    function_list: list(TwoParameterFunction)
        List of functions that can be used to generate datasets
    dataset_list: list(Dataset)
        List of datasets that have been generated
    plot_list:   list(Datasets)
        List of datasets which have been addded to the plotting window
    statusbar: QStatusBar
        Display bar at bottom of GUI window for messages about nominal performance, errors, warnings
    """

    def __init__(self):

        QMainWindow.__init__(self)

        # establish size and position of GUI window upon application start
        self.title = 'CZBiohub Plotting App'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # declare domains loaded by default
        self.domain_list = [Domain(0, 10),
                            Domain(10, 20, sampling='random'),
                            Domain(0, 20, sampling='linear', numpoints=200)]
        self.current_domain_idx = 0
        self.domain_list_widget = QListWidget()

        # declare functions loaded by default
        self.function_list = [DampedOscillator(), UnstableOscillator(), Pyramid()]
        self.current_function_idx = 0
        self.function_list_widget = QListWidget()

        # declare dataset and plot lists
        self.dataset_list = []
        self.current_dataset_idx = 0
        self.dataset_list_widget = QListWidget()

        self.statusBar().showMessage('Ready')

        # populate default functions and domains into appropriate lists
        for func in self.function_list:
            self.function_list_widget.addItem(func.get_name())

        for dom in self.domain_list:
            self.domain_list_widget.addItem(dom.get_name())

        # provide logfile of errors, warnings, and information statements
        # TODO: suppress matplotlib logging output
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename= os.getcwd() + '/temp/CZApp.log',
                            filemode='w')

        self.uiSetup()

    def uiSetup(self):
        """
        Constructs the GUI layout and establishes connectivity between button-clicks and function-calls

        All buttons and function-calls must be connected to one another in the uiSetup to work in the GUI during
        run-time. Buttons not assigned to layouts will not appear, and buttons not connected to functions will not
        perform actions when clicked.
        """
        main_menu = self.menuBar()
        main_menu.setNativeMenuBar(False)
        file_menu = main_menu.addMenu('File')

        # Definitions for menu bar at top of window
        exit_button = QAction(QIcon('exit24.png'), 'Exit', self)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Exit application')
        exit_button.triggered.connect(self.close)

        # Load and save functionality are part of the extended implementation and not part of core assignment
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

        # The following lays out the UI from the "top down" and "left to right" for vertical and horizontal layouts
        # respectively. PyQt5 uses a 'signal and socket' representation such that each button generates a signal
        # which activates a socket, ie a function call. These are connected via the 'button.clicked.connect' statements
        widget = QWidget(self)
        self.setCentralWidget(widget)

        vlay = QVBoxLayout(widget)
        hlay = QHBoxLayout()
        vlay.addLayout(hlay)

        hlay.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))

        # buttons for manipulating functions and domains
        loadfunc_button = QPushButton('Load Functions')
        loadfunc_button.setToolTip('Loads previously defined functions from a user-specified JSON file')
        loadfunc_button.clicked.connect(self.load_functions)

        modfunc_button = QPushButton('Modify Function', self)
        modfunc_button.setToolTip("Opens a dialog window to modify parameters of the currently"
                                  "selected function")
        modfunc_button.clicked.connect(self.modify_function)

        new_domain_button = QPushButton('New Domain', self)
        new_domain_button.setToolTip("Opens a dialog window to create new domains with specified start, stop, number"
                                     "of points and sampling method")
        new_domain_button.clicked.connect(self.new_domain)

        clear_domain_button = QPushButton('Clear Domains', self)
        clear_domain_button.setToolTip("Clears all domains. Warning: This action cannot be undone")
        clear_domain_button.clicked.connect(self.clear_domains)

        hlay1 = QHBoxLayout()
        hlay1.addWidget(loadfunc_button)
        hlay1.addWidget(modfunc_button)
        hlay1.addWidget(new_domain_button)
        hlay1.addWidget(clear_domain_button)
        hlay1.addItem(QSpacerItem(1000, 10, QSizePolicy.Expanding))
        vlay.addLayout(hlay1)

        # create list views of functions next to domains, with datasets underneath.
        hlay2 = QHBoxLayout()
        hlay2.addWidget(self.function_list_widget)
        hlay2.addWidget(self.domain_list_widget)
        vlay.addLayout(hlay2)

        generate_button = QPushButton('Generate Dataset', self)
        generate_button.setToolTip("Applies the currently selected function to the "
                                   "currently selected domain to generate a new dataset")
        generate_button.clicked.connect(self.generate_data)
        clear_datasets_button = QPushButton('Clear Datasets', self)
        clear_datasets_button.setToolTip("Clears all datasets. Warning: This action cannot be undone")
        clear_datasets_button.clicked.connect(self.clear_datasets)
        hlay21 = QHBoxLayout()
        hlay21.addWidget(generate_button)
        hlay21.addWidget(clear_datasets_button)
        vlay.addLayout(hlay21)

        hlay3 = QHBoxLayout()
        hlay3.addWidget(self.dataset_list_widget)
        vlay.addLayout(hlay3)

        # buttons for plotting selected datasets and clearing plot window
        plotsel_button = QPushButton('Plot Selected Dataset', self)
        plotsel_button.setToolTip("Adds the selected dataset to the current plotting window")
        plotsel_button.clicked.connect(self.plot_selected_dataset)
        clear_plots_button = QPushButton('Clear Plotting Window', self)
        clear_plots_button.setToolTip("Clears all plots from the plotting window.")
        clear_plots_button.clicked.connect(self.clear_plots)

        hlay4 = QHBoxLayout()
        hlay4.addWidget(plotsel_button)
        hlay4.addWidget(clear_plots_button)
        vlay.addLayout(hlay4)

        self.plotting_window = Plotter(self)
        vlay.addWidget(self.plotting_window)

        # List interaction functionality to highlight currently selected items
        self.function_list_widget.itemClicked.connect(self.function_clicked)
        self.domain_list_widget.itemClicked.connect(self.domain_clicked)
        self.dataset_list_widget.itemClicked.connect(self.dataset_clicked)

    def function_clicked(self):
        """
        Selects the function for generating datasets and displays function information in the status bar
        """

        self.current_function_idx = self.function_list_widget.currentRow()
        function = self.function_list[self.current_function_idx]
        display_message = (function.get_name() + ", " + function.get_description("desc") + ", " +
                           function.get_description("A_desc") + " = " + str(function.get_A_value()) + ", " +
                           function.get_description("B_desc") + " = " + str(function.get_B_value())
                           )

        self.statusBar().showMessage(display_message)

    def domain_clicked(self):
        """
        Selects the domain for generating datasets and displays domain information in the status bar
        """

        self.current_domain_idx = self.domain_list_widget.currentRow()
        domain = self.domain_list[self.current_domain_idx]
        display_message = domain.get_name() + ", created at " + str(domain.timestamp)
        self.statusBar().showMessage(display_message)

    def dataset_clicked(self):
        """
        Selects dataset for plotting and displays dataset information in the status bar
        """
        self.current_dataset_idx = self.dataset_list_widget.currentRow()
        dataset = self.dataset_list[self.current_dataset_idx]
        display_message = "Dataset " + dataset.get_name() + " generated at " + str(dataset.timestamp)
        self.statusBar().showMessage(display_message)

    def generate_data(self):
        """
        Generates a new dataset from the currently selected function and currently selected domain
        """

        fun = self.function_list[self.current_function_idx]
        domain = self.domain_list[self.current_domain_idx]
        try:
            data = fun.evaluate(domain.values)
            data_name = str(fun.get_name() + '_on_' + domain.get_name())
            dataset = Dataset(data_name, domain.values, data)
            self.statusBar().showMessage("Generated dataset " + data_name + " at " + dataset.timestamp)
            self.dataset_list.append(dataset)
            self.dataset_list_widget.addItem(data_name)
        except :
            self.statusBar().showMessage("No functions or domain selected to generate data")
            logging.error("Attempted to generate data with no functions or data selected")

    def new_domain(self):
        """
        Opens a dialog box prompting user to define a new domain

        Entry fields of the dialog box are not protected to numeric values, but during run-time the dialog
        box checks values entered before assigning them to generate a domain. Users can select from a drop-down
        menu which lists the types of sampling methods currently supported, in addition to entering start, stop, and
        number of points
        """

        newdom = NewDomain(self)
        newdom.exec_()
        [start, stop, npoints, sampling] = newdom.return_info()
        try:
            float(start)
            float(stop)
            int(npoints)
            str(sampling)
        except InvalidParameter:
            self.statusBar().showMessage("Invalid domain parameters specified, start and stop may be any number" +
                                         " but numpoints must be integer")
            logging.error("Attempted to generate domain with invalid parameters")
        except :
            self.statusBar().showMessage("Failed to modify function")
            logging.error("Failed to modify function")
        else:
            new_domain = Domain(float(start), float(stop), int(npoints), sampling)
            self.domain_list.append(new_domain)
            self.domain_list_widget.addItem(new_domain.get_name())
            self.statusBar().showMessage("Created domain " + new_domain.get_name() + " at " + new_domain.timestamp)

    def modify_function(self):
        """
        Opens a dialog window which prompts the user to modify two parameters of the currently selected function

        Parameter descriptions are taken from the function objects description
        """
        modfun = ModFunction(self)
        modfun.exec_()
        new_A = modfun.get_Aparam()
        new_B = modfun.get_Bparam()

        # Ensure the user cannot enter invalid function parameters
        try:
            float(new_A)
            float(new_B)
        except :
            self.statusBar().showMessage("Invalid parameters assigned to function, defaulting to previous values")
            logging.error("Attempted to assign non-numeric values to function parameters")
        else:
            self.function_list[self.current_function_idx].set_A_value(new_A)
            self.function_list[self.current_function_idx].set_B_value(new_B)

    def plot_selected_dataset(self):
        """
        Adds the currently selected dataset to the plotting window
        """

        try:
            dataset = self.dataset_list[self.current_dataset_idx]
            self.plotting_window.canvas.plot(dataset)
        except:
            self.statusBar().showMessage("No dataset selected to plot")
            logging.error("Attempted to plot data with no dataset selected")

    def clear_plots(self):
        """
        Clears plotting window of all plots
        """
        self.plotting_window.clear_plots()

    def clear_datasets(self):
        """
        Clears datasets from GUI window and deletes them from memory.
        """
        self.dataset_list_widget.clear()
        self.dataset_list.clear()

    def clear_domains(self):
        """
        Clears domains from GUI window and deletes them from memory
        Returns:

        """
        self.domain_list_widget.clear()
        self.domain_list.clear()

    def load_functions(self):
        """
        Populates the list of functions with function objects as read from a .json file
        """

        try:
            file_name, _ = QFileDialog.getOpenFileName(self, 'Single File', os.getcwd(), '*.json')
            parser = Parser(file_name)

            for idx, _ in enumerate(parser.functions):
                function = parser.returnFunction(idx)
                self.function_list.append(function)
                self.function_list_widget.addItem(function.get_name())

            self.statusBar().showMessage("Loaded functions from " + file_name)
        except:
            self.statusBar().showMessage("Failed to load functions or invalid path specified")

    def save_functions(self):
        """
        Saves the current list of functions to the to a .json file in the cwd, with user prompt for name entry

        """
        self.statusBar().showMessage("Saving functions is not yet supported")

    def save_datasets(self):
        """
        Saves the current list of datasets to a .json file in the cwd, with user prompt for name entry

        """
        self.statusBar().showMessage("Saving datasets is not yet supported")


class ModFunction(QDialog):
    """
    Prompts users to modify the previously selected function by replacing parameter values A and B

    If Dialog box does not receive valid input for parameters then it will default to previously stored parameters.
    Previously stored parameters appear as default options in the entry boxes.
    """
    def __init__(self, parent=None):
        super(ModFunction, self).__init__(parent)

        function = parent.function_list[parent.current_function_idx]
        self.setWindowTitle("Modify existing function")
        layout = QGridLayout(self)
        layout.setSpacing(20)

        self.Aparam = QLabel()
        Aedit = QLineEdit()
        Aedit.textChanged.connect(self.Aparam_changed)

        self.Bparam = QLabel()
        Bedit = QLineEdit()
        Bedit.textChanged.connect(self.Bparam_changed)

        # TODO: Show previous parameter values in dialog box
        # Aedit.setText(str(function.get_A_value()))
        # Bedit.setText(str(function.get_B_value()))

        apply_button = QPushButton('Apply', self)
        apply_button.clicked.connect(self.close)

        layout.addWidget(QLabel("Function Form"), 0, 0)
        layout.addWidget(QLabel(function.get_raw()), 0, 1)
        layout.addWidget(QLabel("A: " + function.get_description("A_desc")), 1, 0)
        layout.addWidget(Aedit, 1, 1)
        layout.addWidget(QLabel("B: " + function.get_description("B_desc")), 2, 0)
        layout.addWidget(Bedit, 2, 1)
        layout.addWidget(apply_button, 3, 2)

    def Aparam_changed(self, value):
        self.Aparam.setText(value)

    def Bparam_changed(self, value):
        self.Bparam.setText(value)

    def get_Aparam(self):
        return self.Aparam.text()

    def get_Bparam(self):
        return self.Bparam.text()


class NewDomain(QDialog):
    """
    Prompts users with a dialog box to generate new domains by specifying a start, stop, number of points and
    sampling method.

    This class does not sanitize its inputs or perform type-checking of inputs at run-time
    """
    def __init__(self, parent=None):
        super(NewDomain, self).__init__(parent)

        self.setWindowTitle("Create a new domain")
        layout = QGridLayout(self)
        layout.setSpacing(10)

        self.start = QLabel()
        start_edit = QLineEdit()
        start_edit.textChanged.connect(self.start_changed)

        self.stop = QLabel()
        stop_edit = QLineEdit()
        stop_edit.textChanged.connect(self.stop_changed)

        self.npoints = QLabel()
        npoints_edit = QLineEdit()
        npoints_edit.textChanged.connect(self.npoints_changed)

        self.sampling = QComboBox()
        self.sampling.addItems(["Evenly Spaced", "Uniform Random"])

        apply_button = QPushButton('Apply', self)
        apply_button.clicked.connect(self.close)

        layout.addWidget(QLabel("Start value"), 1, 0)
        layout.addWidget(start_edit, 1, 1)
        layout.addWidget(QLabel("Stop value"), 2, 0)
        layout.addWidget(stop_edit, 2, 1)
        layout.addWidget(QLabel("Number of points"), 3, 0)
        layout.addWidget(npoints_edit, 3, 1)
        layout.addWidget(QLabel("Sampling method"), 4, 0)
        layout.addWidget(self.sampling, 4, 1)
        layout.addWidget(apply_button, 5, 2)

    def start_changed(self, value):
        self.start.setText(value)

    def stop_changed(self, value):
        self.stop.setText(value)

    def npoints_changed(self, value):
        self.npoints.setText(value)

    def return_info(self):
        if self.sampling.currentIndex() == 0:
            sampling = "linear"
        else:
            sampling = "random"
        return [self.start.text(), self.stop.text(), self.npoints.text(), sampling]


class Plotter(QWidget):
    """
    Provides matplotlib built-in toolbar for panning, viewing, saving views, functionality.

    """
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.canvas = PlotCanvas(self, width=10, height=8)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.toolbar)
        self.layout().addWidget(self.canvas)

    def clear_plots(self):
        self.canvas.ax.cla()
        self.canvas.draw()


class PlotCanvas(FigureCanvas):
    """
    Provides basic plotting functionality
    """
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.add_gridspec(5, 5)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.dataset_plotting_list = []
        self.ax = self.fig.add_subplot(111)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, dataset):
        """
        Plots data with label for future implementation of legend
        """
        self.dataset_plotting_list.append(dataset)
        self.ax.plot(dataset.get_xvals(), dataset.get_yvals(), label=dataset.get_name())
        if len(self.dataset_plotting_list) >= 2:
            self.ax.legend(loc ='lower right')
        self.ax.grid()
        self.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_())