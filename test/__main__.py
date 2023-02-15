#!/usr/bin/python3




#------------------------------------------------------------------------------
# Import Python libraries
import os
import sys
import unittest

from pathlib import Path

# Add the current execution directory name to SYSPATH to import easily the custom libraries
full_path = os.path.dirname(Path(__file__))
sys.path.append(str(full_path))
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
import test_ljdc
import test_slack
import test_tools
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_ljdc))
    suite.addTests(loader.loadTestsFromModule(test_slack))
    suite.addTests(loader.loadTestsFromModule(test_tools))

    unittest.TextTestRunner(buffer=True, verbosity=2).run(suite)
#------------------------------------------------------------------------------
