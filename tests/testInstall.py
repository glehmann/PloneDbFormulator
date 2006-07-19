import os, sys

if __name__ == '__main__':
	execfile(os.path.join(sys.path[0],'framework.py'))
	
from Products.PloneTestCase import PloneTestCase

import unittest
from Products import PloneDbFormulator
from Products.PloneDbFormulator.Extensions.Install import install


class TestInstall(PloneTestCase.PloneTestCase):
	
	def test_00_install(self,):
		install(self.app.plone)
		


def test_suite():
	""" permet de declarer la classe Test... comme une classe de test, et prepare pour l'ajout a la suite """
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestInstall))
	return suite