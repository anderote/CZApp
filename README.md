# CZApp
GUI for plotting two-parameter functions 

The program has two dependencies which should be installed through pip. Note PyQt5 is a large library.

>> pip install Equation
>> pip install PyQt5

User should then run “CZApp.py” from the command line, 

>> python CZApp.py


Example of use-case:
- click "File" and "Load Functions", select "functions.json" from directory to import functions into the main window
- click a function, and a domain, and click 'generate dataset'
- click a dataset generated in the dataset window and click 'plot selected dataset'
- click the previous function used, click modify function, modify two parameters, then click on previous domain and 'generate dataset'
- click recently generated dataset then click 'plot selected dataset' to compare the two datasets. 

You can specify new functions by modifying the JSON text directly, create new domains from within the GUI, and add as many datasets
to the plot as desired. 
