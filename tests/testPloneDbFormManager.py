#!/usr/bin/python *- encoding=utf-8 -*

import os, sys

if __name__ == '__main__':
	execfile(os.path.join(sys.path[0],'framework.py'))
	
from Products.PloneTestCase import PloneTestCase
import unittest
import makerequest

from Products.PloneDbFormulator.utils import dict_cmp


from Products import PloneDbFormulator
from Products.PloneDbFormulator import PloneDbFormManager
from Products.PloneDbFormulator.PloneDbFormsManager import PloneDbFormsManager

from Products.PloneDbFormulator.interfaces.PloneDbFormManager import IPloneDbFormManager 
from Products.PloneDbFormulator.validators import verifyUnicityConstraint

from testPloneDbFormsManager import Request, QUERY_STRING_SETUPTABLE


class TestPloneDbFormManager(PloneTestCase.PloneTestCase):
	
	
	def getPdfsmTest(self,):
		""" cree et/ou recupere une instance pdfsmTest de TestPloneDbFormsManager dans le folder self.folder """
		if not(hasattr(self.folder,'pdfsmTest')):
			PloneDbFormulator.PloneDbFormsManager.addPloneDbFormsManager(self.folder,"pdfsmTest")
			
		return self.folder.pdfsmTest
			
	
	def getConnectedPdfsmTest(self,):
		
		if not(hasattr(self.getPdfsmTest(),"connection")):
			self.folder.pdfsmTest.addConnection(connection_info="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433",title="mon titre")
		elif not(self.folder.pdfsmTest.connection_info=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433"):
			self.folder.pdfsmTest.majConnection("dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		return self.folder.pdfsmTest
		
	def getSetupPdfsmTest(self,):
		folder = self.folder
		folder.REQUEST = Request()
		request = folder.REQUEST
		
		request.set('QUERY_STRING',QUERY_STRING_SETUPTABLE)
		formTest  = self.getFormTest()
		formTest.setTablesList = formTest.getTablesList() + ("subventions",)
		
		pdfsmTest = self.getConnectedPdfsmTest()
		pdfsmTest.setupTableProperties(REQUEST=request)
		
		return pdfsmTest
		
	def getFormTest(self):
		
		if hasattr(self.folder,"pdfsmTest"):
			if not(hasattr(self.folder.pdfsmTest,"formTest")):
				self.getConnectedPdfsmTest().addPloneDbFormManager("formTest")
		else:
			PloneDbFormulator.PloneDbFormsManager.addPloneDbFormsManager(self.folder,"pdfsmTest")
			self.getSetupPdfsmTest().addPloneDbFormManager("formTest")
		
		return self.folder.pdfsmTest.formTest



	def test_00_interface(self,):
		self.failUnless(IPloneDbFormManager.isImplementedByInstancesOf(PloneDbFormManager.PloneDbFormManager))
		for name in IPloneDbFormManager.names():
			#print name
			self.failUnless(hasattr(PloneDbFormManager.PloneDbFormManager,name),"Method "+name+" misses in PloneDbFormManager implementation")

				
			
	def test_02_addPloneDbFormManager(self,):
		self.failIf(PloneDbFormManager.addPloneDbFormManager.__doc__==None,"addPloneDbFormManager is not documented")

		
		'''PloneTestCase.setupPloneSite(products=('PloneDbFormulator',))'''
			
			
		folder = self.getConnectedPdfsmTest()
		
		PloneDbFormManager.addPloneDbFormManager(folder,"aNewForm")
		
		self.failUnless(hasattr(folder,'aNewForm'))
		aNewForm = folder.aNewForm
		self.failUnless(aNewForm.__class__.__name__=="PloneDbFormManager")
		
		self.failUnless(hasattr(aNewForm,'form'))
		self.failUnless(aNewForm.form.__class__.__name__=="ZMIForm")
		
		
	def test_03_get_getFormsManager(self,):
		
		self.failIf(PloneDbFormManager.PloneDbFormManager.getFormsManager.__doc__==None,"getFormsManager is not documented")

		self.failUnless(self.getFormTest().getFormsManager() == self.folder.pdfsmTest, str(self.getFormTest().getFormsManager()))
		self.failUnless(self.getFormTest().getFormsManager().__class__.__name__=="PloneDbFormsManager")
	
	def test_04__get_tableName_vocabulary(self,):
		self.failIf(PloneDbFormManager.PloneDbFormManager._get_field_list_vocabulary.__doc__==None,"_get_tableName_vocabulary is not documented")
		
		formTest = self.getFormTest()
		formTest.setTablesList = ("subventions",)
		self.failUnless(("subventions","Subventions") in formTest._get_tableName_vocabulary(),str(formTest._get_tableName_vocabulary()))
		
	def test_05__get_field_list_vocabulary(self,):
		self.failIf(PloneDbFormManager.PloneDbFormManager._get_field_list_vocabulary.__doc__==None,"get_field_list_vocabulary is not documented")
		
		pdfsmTest = self.getSetupPdfsmTest()
		formTest = self.getFormTest()
		fieldList = formTest._get_field_list_vocabulary(tableName="subventions")
		self.failUnless(('numero','Numero') in formTest._get_field_list_vocabulary() and ("date_a","Date a") in formTest._get_field_list_vocabulary(),str(formTest._get_field_list_vocabulary()))
		
		
def test_suite():
	""" permet de declarer la classe Test... comme une classe de test, et prepare pour l'ajout a la suite """
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestPloneDbFormManager))
	return suite