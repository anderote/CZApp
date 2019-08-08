from abc import ABC, abstractmethod


class TwoParameterFunction(ABC):
    '''
    General abstract base class for two-parameter functions of a single variable.

    Enforces interface for getting descriptions, getting/setting parameter values, evaluating function
    '''

    @abstractmethod
    def get_name(self):
        '''
        :return:
            string: name of the function if available
        '''
        pass

    @abstractmethod
    def get_raw(self):
        '''
        :return:
            string: raw text which defines function
        '''
        pass

    @abstractmethod
    def get_description(self, key):
        '''
        :return:
            string: description of the function or parameters if available
        '''
        pass


    @abstractmethod
    def set_A_value(self, A):
        '''
        :param
            A: value to which parameter A is set
        '''
        pass

    @abstractmethod
    def set_B_value(self, B):
        '''
        :param B:
            B: value to which parameter B is set
        '''
        pass

    @abstractmethod
    def get_A_value(self):
        '''
        :return:
            double: current value of parameter A
        '''
        pass

    @abstractmethod
    def get_B_value(self):
        '''
        :return:
            double: current value of parameter B
        '''
        pass

    @abstractmethod
    def evaluate(self, value):
        '''
        :return:
            double or list of doubles: evaluation of function at value or list of values
        '''
        pass



