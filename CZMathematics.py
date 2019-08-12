from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np


class InvalidParameter(ValueError):
    """
    Empty execption to notify GUI when an invalid parameter is passed to a function
    """
    pass


class TwoParameterFunction(ABC):
    '''
    General abstract base class for two-parameter functions of a single variable.

    Enforces interface for getting descriptions, getting/setting parameter values, evaluating function

    Parameters A and B are private to force getter/setter methods and therefore ensure they are always numeric type.

    Derived classes should modify constructor to uniquely specify the following attributes:
        name
        description
        raw text describing function method
        A description
        B description

    Derived class must implement their own evaluate function compatible with numpy arrays as input.
    '''
    @abstractmethod
    def __init__(self, A, B):
        self._A = A
        self._B = B
        self.name = "Unnamed"
        self.description = "No description"
        self.raw = ""
        self.A_desc = ""
        self.B_desc = ""

    def get_name(self):
        '''
        :return:
            string: name of the function if available
        '''
        return self.name

    def get_raw(self):
        '''
        :return:
            string: raw text which defines function
        '''
        return self.raw

    def get_description(self, key):
        '''
        :return:
            string: description of the function or parameters if available
        '''
        if key == "desc":
            return self.description
        elif key == "A_desc":
            return self.A_desc
        elif key == "B_desc":
            return self.B_desc

    def set_A_value(self, A):
        '''
        :param
            A: value to which parameter A is set
        '''
        try:
            self._A = float(A)
        except:
            raise InvalidParameter("Invalid parameter, must be a numeric type")

    def set_B_value(self, B):
        '''
        :param B:
            B: value to which parameter B is set
        '''
        try:
            self._B = float(B)
        except:
            raise InvalidParameter("Invalid parameter, must be a numeric type")
        pass

    def get_A_value(self):
        '''
        :return:
            double: current value of parameter A
        '''
        return self._A

    def get_B_value(self):
        '''
        :return:
            double: current value of parameter B
        '''
        return self._B

    @abstractmethod
    def evaluate(self, value):
        '''
        :return:
            double or list of doubles: evaluation of function at value or list of values
        '''
        pass


class Dataset():
    """
    Container for data generated by the application of functions to domains

    This class gaurantees that all data generated can be used to produce matplotlib, which demands
    equivalency between sizes of x and y values.
    """
    def __init__(self, name, x_val, y_val):
        self.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.name = name
        self.x_data = x_val
        self.y_data = y_val
        if len(x_val) != len(y_val):
            raise Exception('Datasets must contain equal numbers of x and y values!')

    def get_name(self):
        return self.name()


class Domain():
    """
    X-values which are fed to a function as an argument. Domains support multiple samplings between start and
    stop values for a desired number of points.

    TODO: Write tests for sample and resample
    """
    def __init__(self, start, stop, numpoints=100, sampling='linear'):
        self.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.start = start
        self.stop = stop
        self.n = numpoints
        self.sampling = sampling
        self.name = sampling + "_" + str(start) + "_to_" + str(stop) + "_" + str(numpoints) + "pts"
        self.values = self.sample()

    def sample(self):
        """
        Returns a sampling between start and stop according to initialization method
        :return: set of x-vales chosen according to sampling method, start, stop, and number of points
        """
        if self.sampling == 'linear':
            step = (self.stop - self.start)/self.n
            return np.arange(self.start, self.stop, step)

        if self.sampling == 'random':
            return np.random.uniform(self.start, self.stop, self.n)

    def resample(self, sampling):
        """
        Re-samples the dataset under a different method, retaining start, stop, and numpoints
        :param sampling: string, sampling method which can be linear, random, chebyeshev, exponential
        """
        self.sampling = sampling
        self.values = self.sample()

    def get_name(self):
        return self.name


