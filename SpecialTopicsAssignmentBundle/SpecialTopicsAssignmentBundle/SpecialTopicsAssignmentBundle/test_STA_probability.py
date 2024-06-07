https://powcoder.com
代写代考加微信 powcoder
Assignment Project Exam Help
Add WeChat powcoder
import sys
from random import randint, seed, uniform, choice, choices
import math
import ast
import os
import unittest
import specialtopics as ST
from inspect import getsource

randomSeed = 0     # <--------------------- change the seed here
scriptDirectory = os.path.dirname(__file__)
allowed_modules = [ 'probability', 'numpy', 'csv', 're' ]

repeats = 5000
yearsPerRepeat = 20
startingBalance = 0
cropFailures = ( 'drought', 'hail', 'grasshoppers', 'no failure' )

fields = { 
        'Home quarter': { 'drought': 4, 'hail': 1, 'grasshoppers': 1, 'no failure': 14}, 
        'Breaking':     { 'drought': 3, 'hail': 3, 'grasshoppers': 3, 'no failure': 11},
        'Lyon quarter': { 'drought': 0, 'hail': 4, 'grasshoppers': 0, 'no failure': 16},
        'Down south':   { 'drought': 1, 'hail': 1, 'grasshoppers': 3, 'no failure': 15},
        'Up north':     { 'drought': 2, 'hail': 2, 'grasshoppers': 2, 'no failure': 14},
        'The farm':     { 'drought': 1, 'hail': 1, 'grasshoppers': 1, 'no failure': 17}
    }

insurancePayoutRates = {
    'comprehensive': { 'drought': 0.8, 'hail': 0.8,  'grasshoppers': 0.8, 'no failure': 1 },
    'hail':          { 'drought': 0,   'hail': 0.8,  'grasshoppers': 0  , 'no failure': 1 },
    'grasshopper':   { 'drought': 0  , 'hail': 0,    'grasshoppers': 0.8, 'no failure': 1 },
    'basic':         { 'drought': 0.5, 'hail': 0,    'grasshoppers': 0.5, 'no failure': 1 }
}

premiumRanges = {
    'comprehensive': (5000, 6000),
    'hail':          (1900, 2100),
    'grasshopper':   (1600, 1720),
    'basic':         (2080, 2320),
}

inputCostRange =     (10000, 20000)
contractPriceRange = (20000, 30000)


def doSomeFarming(chooseCropInsurance):
    seed(randomSeed)
    totalProfit = 0
    for i in range(repeats):
        field = choice(list(fields.values()))
        failureWeights = [ field[failure] for failure in cropFailures ]
        
        state = None            # state variable for the farming function
        lastYearOutcome = None  # we need to remember what last years' outcome was to pass to the farming function
        balance = startingBalance

        for h in range(yearsPerRepeat):
            # Randomly choose various parameters
            premiums = { name: uniform(*range) for name, range in premiumRanges.items() }
            inputCost = uniform(*inputCostRange)
            contractPrice = uniform(*contractPriceRange)
            
            # Call the student's function to find out what insurance to buy
            insurance, state = chooseCropInsurance(premiums, inputCost, contractPrice, lastYearOutcome, state)
            
            # choose a failure at random, weighted according to how often each has occurred on this field
            lastYearOutcome = choices(cropFailures, weights=failureWeights, k=1)[0]
            
            # Calculate the profit
            balance += insurancePayoutRates[insurance][lastYearOutcome] * contractPrice - inputCost - premiums[insurance]

        totalProfit += balance - startingBalance
         
    return totalProfit / repeats


def assert_no_loops(s, f):
    f_ast = ast.parse(getsource(f))
    for node in ast.walk(f_ast):
        if isinstance(node, ast.For):
            s.fail(f'function {f.__name__} uses a for loop.')
        if isinstance(node, ast.While):
            s.fail(f'function {f.__name__} uses a while loop.')


class TestProbabilitySolution(unittest.TestCase):
    def test_no_loops(self):
        '''No loops.  This is worth 1 mark.'''
        assert_no_loops(self, ST.chooseCropInsurance)
    
    
    def test_score(self, set_score=None):
        '''Marks for average net profit, out of 9.'''
        averageProfit = doSomeFarming(ST.chooseCropInsurance)
        score = math.ceil((averageProfit - 61000) / 1830 )
        print(f'Estimated marks for net profit: {score} out of 9')


# This test does not count for any marks.  It just helps to ensure
# that your code will run on the test system.
class TestImportedModules(unittest.TestCase):
    def test_modules(self):
        '''Check that only allowed modules have been imported.'''
        with open('specialtopics.py', "r") as f:
            file_raw = f.read()
            player_ast = ast.parse(file_raw)

        def imported_modules():
            for node in ast.walk(player_ast):
                if isinstance(node, ast.Import):
                    yield from (x.name.split('.')[0] for x in node.names)
                if isinstance(node, ast.ImportFrom) and node.level is None:
                    yield node.module.split('.')[0]

        for module in imported_modules():
            if module not in allowed_modules:
                self.fail(f'module {module} imported by submission but not allowed.')


if __name__ == '__main__':
    print(f'Please note that the marks is an estimate only, as the tester will use a different seed.  It is recommended that you run with multiple seeds for testing.  The seed is chosen by modifying the randomSeed = 0 statement on line 10.')
    print(f'Python version {sys.version}')
    unittest.main(argv=['-b'])

