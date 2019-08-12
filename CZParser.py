import Equation as eq
import json
import os
from unittest import TestCase
from CZMathematics import TwoParameterFunction
import logging


class Parser:
    """
    Parses a JSON file containing two-parameter functions and stores a list of valid functions

    Stores a list of valid functions which can be used to generate instances of function objects
    which extend TwoParameterFunction abstract base class. All valid functions will contain valid
    mathematical expression as a function of x and two parameters A and B. Functions may be returned
    with incomplete or missing descriptions with an appended field saying so.

    A valid function has:
        raw text which can be evaluated as a mathematical expression as functions of x, A, and/or B
        two parameters A and B, even if they are not used in the function text.
    """

    def __init__(self, dir):
        """
        :param dir: text location of the JSON file containing function descriptions
        """
        self._parameter_keys = ["A", "B"]
        self._desc_keys = ["name", "desc", "A_desc", "B_desc"]
        self.functions = self.readFunctions(dir)
        # self.logger = logging.getLogger("Parser")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename= os.getcwd() + '/temp/ParserTesting.log',
                            filemode='w')


    def readFunctions(self, dir):
        """
        Sanitizes a JSON file containing two-parameter functions and returns a list of valid
        functions
        :param dir: location of JSON file
        :return: list of valid functions
        """
        with open(dir, encoding='utf-8') as data_file:
            function_data = json.loads(data_file.read())

        cleaned_functions = []
        remove_flag = False

        # Only accept functions if they explicitly pass validity checks on math
        # add warnings if it appears a function is missing parameters or descriptions
        for idx, element in enumerate(function_data):
            remove_flag = False
            if "raw" in element:
                if not self.checkFunction_math(element["raw"]):
                    remove_flag = True

            if "raw" not in element:
                remove_flag = True

            if "name" not in element:
                element.update({"name": "Unnamed Function"})

            # If A and B are missing, i.e. zero parameter function, add placeholders
            if not self.checkFunction_params(element):
                element.update({"A": "0.0", "B": "0.0"})

            # TODO: This overwrites descriptions if some are missing, it should be more lenient to preseve partial descriptions
            if not self.checkFunction_desc(element):
                element.update({"A_desc": "", "B_desc" : "", "desc" : ""})

            if not remove_flag:
                cleaned_functions.append(element)

        return cleaned_functions


    def checkFunction_math(self, raw):
        """
        Returns whether a string contains a valid mathematical expression
        :param raw: string which contains mathematical expression
        :return:    boolean
        """
        try:
            f = eq.Expression(raw, ['x', 'A', 'B'])

            # TODO: need a better method for checking if functions are valid than a simple point evaluation
            #  although this works in most cases most of the time it seems.
            f(x=0, A=0, B=0)
        # Value and Type errors are thrown when the string can't be converted to a function via Equation library

        except TypeError:
            logging.error("Attempted to parse text that is not a function, or with improperly labelled parameters")
            return False

        # TODO: It would be nice to automatically detect any parameters, regardless of if they are labelled A or B, and

        # Zero division errors are still functions, i.e. 1/x
        except ZeroDivisionError:
            logging.warning("Function defined which is unbounded at the origin")
            return True
        else:
            return True

    def checkFunction_desc(self, element):
        """
        Returns True if a function has all description fields filled out
        :param name:
        :return:
        """
        for key in self._desc_keys:
            if key not in element.keys():
                logging.info("Function defined with incomplete or missing descriptors")
                return False

        return True

    def checkFunction_params(self, element):
        """
        Checks to see if a function is a two-parameter function
        :param element: JSON object containing function fields
        :return:
        """
        for p in self._parameter_keys:
            if p not in element.keys():
                logging.warning("One or Zero-parameter function found, assigning zero-value placeholder parameters")
                return False
        return True

    def returnFunction(self, index):
        """
        Returns a class object which extends TwoParameterFunction functionality

        :param index: position of function in Parser.functions
        :return: class object which extends TwoParameterFunction
        """
        selected_function = self.functions[index]

        class Function(TwoParameterFunction):
            """
            Function which extends TwoParameterFunction functionality

            Parameters A, B, and the raw text are exposed directly in the class and
            accessed only through getter/setter methods.

            An 'original' template is stored in function_template to allow exporting modified functions
            at a later date, i.e. with updated parameter values.
            """
            def __init__(self, fun_template):
                try:
                    self.A = float(fun_template["A"])
                except ValueError:
                    logging.error("Invalid parameter value, re-setting to zero")
                    self.A = 0.0

                try:
                    self.B = float(fun_template["B"])
                except ValueError:
                    logging.error("Invalid parameter value, re-setting to zero")
                    self.B = 0.0

                self.raw = fun_template["raw"]

                # storing the template adds more memory overhead but lets us be more flexible
                # in what is considered a valid function, i.e. allowing missing descriptors
                # also makes it easier to save functions.
                self.function_template = fun_template

            def get_name(self):
                try:
                    return self.function_template["name"]
                except KeyError:
                    return "Unnamed_Function"

            def get_raw(self):
                return self.raw

            def get_description(self, key):
                try:
                    return self.function_template[key]
                except KeyError:
                    return ""

            def set_A_value(self, A):
                try:
                    float(A)
                except ValueError:
                    logging.warning("Attempted to assign a non-number to parameter A")
                else:
                    self.A = A
                    self.function_template.update({"A": A})

            def set_B_value(self, B):
                try:
                    float(B)
                except ValueError:
                    logging.warning("Attempted to assign a non-number to parameter B")
                else:
                    self.B = B
                    self.function_template.update({"B": B})

            def get_A_value(self):
                return self.A

            def get_B_value(self):
                return self.B

            def evaluate(self, value):
                # f could be defined as a class attribute but would require storing the Expression object in memory.
                # by declaring it locally it is thrown away and we only need store the text it is derived from.
                # This saves memory overhead at the cost of run-time performance in evaluating functions

                try:
                    f = eq.Expression(self.raw, ["x", "A", "B"])
                    result = f(x=value, A=self.A, B=self.B)
                except ValueError:
                    logging.error("Failed to evaluate function call")
                    return None
                else:
                    return result

        function_object = Function(selected_function)
        return function_object


class ParserTest(TestCase):
    """
    Unit testing class for the Parser.

    An example of functions stored in a JSON file with known values is given in /functions.json
    empty.json is a blank file we use so we can inspect the log warnings and errors
    """
    def setUp(self):

        self.Parser = Parser("empty.json")
        # self.logger = logging.getLogger("ParserTest")

    def test_checkFunction_math(self):

        self.assertEqual(False, self.Parser.checkFunction_math("bananas"))
        self.assertEqual(False, self.Parser.checkFunction_math("C*x + D*x^2"))
        self.assertEqual(True, self.Parser.checkFunction_math("A*x + B*x^2"))
        self.assertEqual(True, self.Parser.checkFunction_math("1/x"))

    def test_checkFunction_desc(self):

        described_function = {
        "name": "Exp",
        "desc": "Exponential Function",
        "raw": "A*e^(x*B)",
        "A": "1.0",
        "B": "2.0",
        "A_desc": "Initial Value",
        "B_desc": "Growth Rate"
        }

        undescribed_function = {
        "name": "Exp",
        "raw": "A*e^(x*B)",
        "A": "1.0",
        "B": "2.0",
        }

        self.assertEqual(False, self.Parser.checkFunction_desc(undescribed_function))
        self.assertEqual(True, self.Parser.checkFunction_desc(described_function))

    def test_checkFunction_params(self):
         unparam_fun = {
             "name": "Exp",
             "raw": "A*e^(x*B)",
         }

         param_fun = {
             "name": "Exp",
             "raw": "A*e^(x*B)",
             "A": "1.0",
             "B": "2.0",
         }

         self.assertEqual(False, self.Parser.checkFunction_params(unparam_fun))
         self.assertEqual(True, self.Parser.checkFunction_params(param_fun))


    def test_returnFunction(self):
        pass


