import numpy as np
from CZMathematics import TwoParameterFunction

class DampedOscillator(TwoParameterFunction):
    """
    Function representing the behavior of an exponentially decaying sinusoid., F(x) = A*e^-x/B

    'A' represents the initial amplitude and 'B' represents the exponential decay time constant
    """
    def __init__(self, A=10, B=2):
        super().__init__(A, B)
        self.name = "Damped_Oscillator"
        self.description = "Represents the behavior of an exponentially decaying sinusoid"
        self.raw = "A*e^(-x/B)"
        self.A_desc = "Initial Amplitude"
        self.B_desc = "Decay constant"

    def evaluate(self, xvals):
        return self._A * np.sin(xvals * (2*np.pi)) * np.exp((-xvals) / self._B)


class UnstableOscillator(TwoParameterFunction):
    """
    Function representing the behavior of an exponentially growing sinusoid., F(x) = A*e^x/B

    'A' represents the initial amplitude and 'B' represents the exponential growth time constant
    """
    def __init__(self, A=10, B=2):
        super().__init__(A, B)
        self.name = "Unstable_Oscillator"
        self.description = "Represents the behavior of an exponentially growing sinusoid"
        self.raw = "A*e^(x/B)"
        self.A_desc = "Initial amplitude"
        self.B_desc = "Growth constant"

    def evaluate(self, xvals):
        return self._A *np.sin(xvals * (2*np.pi))* np.exp(xvals / self._B)


class Pyramid(TwoParameterFunction):
    """
    Arbitrary routine that has no direct evaluation, i.e. not a simple function that could evaluate point by point

    Draws a pyramid of height A with B steps. If there are not enough points to draw B steps then draws a triangle.
    """

    def __init__(self, A=10, B=10):
        super().__init__()
        self.name = "Pyramid_Routine"
        self.description = "Draws a pyramid shape on the plot"
        self.raw = "Pyramid shape"
        self.A_desc = "Pyramid height"
        self.B_desc = "Number of layers"

    def evaluate(self, xvals):
        pass


