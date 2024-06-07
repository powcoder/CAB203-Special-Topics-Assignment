https://powcoder.com
代写代考加微信 powcoder
Assignment Project Exam Help
Add WeChat powcoder
import os
import ast
import unittest
from inspect import getsource
import sys

import specialtopics as ST

scriptDirectory = os.path.dirname(__file__)
allowed_modules = ["csv", "probability", "numpy", "re"]

tolerance = 0.01


def assert_no_loops(s, f):
    f_ast = ast.parse(getsource(f))
    for node in ast.walk(f_ast):
        if isinstance(node, ast.For):
            s.fail(f"function {f.__name__} uses a for loop.")
        if isinstance(node, ast.While):
            s.fail(f"function {f.__name__} uses a while loop.")


def closeEnough(s, a, b):
    if abs(a - b) > tolerance:
        s.fail(f"Amounts differ.  Expected: {a} Got {b}")


def closeEnoughDict(s, a, b):
    if set(a.keys()) != set(b.keys()):
        s.fail(f"Dictionaries don't have the same keys.\nExpected: {a}\nGot: {b}")

    r = all(abs(a[k] - b[k]) <= tolerance for k in a.keys())
    if not r:
        s.fail(f"Dictionaries have different values.\nExpected: {a}\nGot: {b}")


class TestLinearAlgebra(unittest.TestCase):
    def test_no_loops(self):
        """No loops"""
        assert_no_loops(self, ST.blendWheat)

    def run_for_csvfile(self, csvfilename, correctDict, correctAmount):
        rDict, rAmount = ST.blendWheat(csvfilename)

        closeEnoughDict(self, correctDict, rDict)
        closeEnough(self, correctAmount, rAmount)

    def test_bins1(self):
        self.run_for_csvfile("bins1.csv", {"A": 12.0, "B": 10.29, "C": 3.43}, 25.71)

    def test_bins2(self):
        self.run_for_csvfile("bins2.csv", {'Big one': 7.0, 'One beside the big one': 8.17, 'Old one': 2.33}, 17.5)
    
    def test_bins3(self):
        self.run_for_csvfile("bins3.csv", {'A': 17.5, 'B': 15.0, 'C': 5.0}, 37.5)

    def test_bins4(self):
        self.run_for_csvfile("bins4.csv", {'A': 14.0, 'B': 12.0, 'C': 4.0}, 30.0)

    def test_bins5(self):
        self.run_for_csvfile("bins5.csv", {'A': 7.5, 'B': 15.0, 'C': 0.0}, 22.5)

    def test_bins6(self):
        self.run_for_csvfile("bins6.csv", {'A': 3.5, 'B': 3.5, 'C': 7.0}, 14.0)

    def test_bins7(self):
        self.run_for_csvfile("bins7.csv", {'A': 22.0, 'B': 8.25, 'C': 2.75}, 33.0)

    def test_bins8(self):
        self.run_for_csvfile("bins8.csv", {'Bravo': 5.5, 'Charlie': 0.0, 'Alpha': 22.0}, 27.5)

    def test_bins9(self):
        self.run_for_csvfile("bins9.csv",  {'Top': 9.33, 'Middle': 2.67, 'Bottom': 4.0}, 16.0)


# This test does not count for any marks.  It just helps to ensure
# that your code will run on the test system.
class TestImportedModules(unittest.TestCase):
    def test_modules(self):
        with open("specialtopics.py", "r") as f:
            file_raw = f.read()
            player_ast = ast.parse(file_raw)

        def imported_modules():
            for node in ast.walk(player_ast):
                if isinstance(node, ast.Import):
                    yield from (x.name.split(".")[0] for x in node.names)
                if isinstance(node, ast.ImportFrom) and node.level is None:
                    yield node.module.split(".")[0]

        for module in imported_modules():
            if module not in allowed_modules:
                self.fail(f"module {module} imported by submission but not allowed.")


if __name__ == "__main__":
    print(f"Python version {sys.version}")
    unittest.main(argv=["-b"])
