#!/usr/bin/env python

import os
import unittest
import lsst.utils.tests as utilsTests
import lsst.pex.config as pexConfig

class Config1(pexConfig.Config):
    x = pexConfig.ListOfListField("x", int, minLength=2, maxLength=5,
                                  default=[[1],[2,3],])
    y = pexConfig.ListOfListField("y", str, default=[["a"],["bc","def"]])

class ListOfListFieldTest(unittest.TestCase):
    def testConstructor(self):
        try:
            class BadDtype(pexConfig.Config):
                l = pexConfig.ListOfListField("bad", list)
        except:
            pass
        else:
            raise SyntaxError("Unsupported dtype should not be allowed")

    def testAssignment(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "x", [[1.2],[3.4]])
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "x", [1])
        c.x = [[1,2],[3]]; c.x = [[],[],[],[],[]]; c.x = [[],[],[],[4]]

        
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "y", [[1]])
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "y", [[1.3]])
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "y", ['str'])
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "y", [['str'], [7]])
        c.y = []; c.y = [['str']]; c.y = [[],[],['']]

    def testValidation(self):
        c = Config1()
        Config1.validate(c)

        c.x = [[1],]
        self.assertRaises(pexConfig.FieldValidationError, Config1.validate, c)

        c.x = [[1],[2],[3],[4],[5],[6]]
        self.assertRaises(pexConfig.FieldValidationError, Config1.validate, c)

        c.x = [[1,],[2,]]
        Config1.validate(c)

    def testInPlaceModification(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, c.x.__setitem__, 2, 0)
        c.x[0][0] = 10
        print 'c.x:', c.x

        self.assertEqual(c.x, [[10], [2, 3]])
        self.assertEqual(((10,), (2, 3)), c.x)

        c.x[1] = [11,12,13]

        self.assertEqual(c.x, [[10], [11,12,13]])
        self.assertEqual(((10,), (11,12,13)), c.x)

        c.x.insert(1, [20,])
        self.assertEqual(c.x, [[10], [20], [11,12,13]])

        c.x.extend([[30,],[40]])
        self.assertEqual(c.x, [[10], [20], [11,12,13], [30],[40]])

    
def suite():
    utilsTests.init()
    suites = []
    suites += unittest.makeSuite(ListOfListFieldTest)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit=False):
    utilsTests.run(suite(), exit)

if __name__=='__main__':
    run(True)
