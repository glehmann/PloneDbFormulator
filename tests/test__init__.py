import os, sys

if __name__ == '__main__':
	execfile(os.path.join(sys.path[0],'framework.py'))
	
from Products.PloneTestCase import PloneTestCase

import unittest

from Products import PloneDbFormulator 


class Test__init__(PloneTestCase.PloneTestCase):
	
	def test_01_initialize(self,):
		#PloneDbFormulator.initialize(self)
		#assert(hasattr(self.manage_addProduct['PloneDbFormulator'],"addPloneDbFormsManager"))
		pass
		
def test_suite():
	""" permet de declarer la classe Test... comme une classe de test, et prepare pour l'ajout a la suite """
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(Test__init__))
	return suite
