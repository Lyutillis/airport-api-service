import unittest

def suite():   
    return unittest.TestLoader().discover("airport.tests", pattern="*.py")