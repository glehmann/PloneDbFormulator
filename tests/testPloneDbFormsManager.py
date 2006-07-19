#!/usr/bin/python *- encoding=utf-8 -*

import os, sys

if __name__ == '__main__':
	execfile(os.path.join(sys.path[0],'framework.py'))
	
from Products.PloneTestCase import PloneTestCase
import unittest
import makerequest

from Products.PloneDbFormulator.utils import dict_cmp


from Products import PloneDbFormulator
from Products.PloneDbFormulator import PloneDbFormsManager
from Products.PloneDbFormulator.interfaces.PloneDbFormsManager import IPloneDbFormsManager 
from Products.PloneDbFormulator.validators import verifyUnicityConstraint

from zope.component.tests.request import Request
global QUERY_STRING_SETUPTABLE
QUERY_STRING_SETUPTABLE = "tableName=subventions&somme_accordee.label=Somme accordee&somme_accordee.type=IntegerField&somme_accordee.width=3&nom.label=Nom&nom.type=StringField&nom.width=25&remarques.label=Remarques&remarques.type=StringField&remarques.width=72&date_d.label=Date d&date_d.type=DateTimeField&date_d.width=10&date_a.label=Date a&date_a.type=DateTimeField&date_a.width=10&pays.label=Pays&pays.type=StringField&pays.width=10&adresse.label=Adresse&adresse.type=StringField&adresse.width=&numero.label=Numero&numero.type=IntegerField&numero.primary_key=1&numero.null=1&numero.width=2&transmis_tresor.label=Transmis tresor&transmis_tresor.type=DateTimeField&transmis_tresor.width=10&reception_rapport.label=Reception rapport&reception_rapport.type=DateTimeField&reception_rapport.width=10&communication.label=Communication&communication.type=StringField&communication.width=2&congres.label=Congres&congres.type=StringField&congres.width=151&somme_demandee.label=Somme demandee&somme_demandee.type=IntegerField&somme_demandee.width=4&estimation.label=Estimation&estimation.type=IntegerField&estimation.width=3&fonction.label=Fonction&fonction.type=StringField&fonction.width=33&notification.label=Notification&notification.type=DateTimeField&notification.width=10&useSearchForm_roles=Owner&useSearchForm_roles=Manager&useSearchForm_roles=Member&useSearchForm_roles=Authenticated&addModifForm_roles=&addSearchForm_roles=Owner&addSearchForm_roles=Manager&useModifForm_roles=Manager"

class Request(object):
	form = {}
	environ = {}
	
	class Response:
		def redirect(self,URL):
			message = "Allons gaiement vers "+str(URL)
			print "\n"+message
			return message
			
	
	
	def set(self,item,value):
		
		if item=="QUERY_STRING":
			self.environ['QUERY_STRING'] = value
			self.form={}
			for parameterSet in value.split('&'):
				parameterKey = parameterSet.split('=')[0]
				parameterValue = parameterSet.split('=')[1]
				if self.form.has_key(parameterKey):
					if type(self.form[parameterKey]) == type([]):
						self.form[parameterKey].append(parameterValue)
					else:
						self.form[parameterKey] = [self.form[parameterKey],parameterValue]
				else:
					self.form[parameterSet.split('=')[0]]=parameterSet.split('=')[1]
		
		elif item=="HTTP_STRING":
			self.set('QUERY_STRING',value.split('?')[1])
			self.set('URL',value.split('?')[0])

		else:
			self.item = value
	
	RESPONSE = Response()

	

class TestPloneDbFormsManager(PloneTestCase.PloneTestCase):

	'''class Request(object):
		
		def set(self,item,value):
			if item = '''
		
		
	
	def getPdfsmTest(self):
		""" cree et/ou recupere une instance pdfsmTest de TestPloneDbFormsManager dans le folder self.folder """
		if not(hasattr(self.folder,'pdfsmTest')):
			PloneDbFormsManager.addPloneDbFormsManager(self.folder,"pdfsmTest")
			
		return self.folder.pdfsmTest
		
	def getPgfsmTest(self):
		if not(hasattr(self.folder,'pgfsmTest')):
			PloneDbFormsManager.addPloneGadflyFormsManager(self.folder,"pgfsmTest")
		return self.folder.pgfsmTest
		
	def getConnectedPdfsmTest(self):
		
		if not(hasattr(self.getPdfsmTest(),"connection")):
			self.folder.pdfsmTest.addConnection(connection_info="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433",title="mon titre")
		elif not(self.folder.pdfsmTest.connection_info=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433"):
			self.folder.pdfsmTest.majConnection("dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		return self.folder.pdfsmTest
		
	def getInsufficientConnectionPdfsm(self,):
		if not(hasattr(self.getPdfsmTest(),"connection")):
			self.folder.pdfsmTest.addConnection(connection_info="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433",title="mon titre")
		elif not(self.folder.pdfsmTest.connection_info=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433"):
			self.folder.pdfsmTest.majConnection("dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		return self.folder.pdfsmTest
		
		
		
	def test_00_interface(self,):
		self.failUnless(IPloneDbFormsManager.isImplementedByInstancesOf(PloneDbFormsManager.PloneDbFormsManager))
		for name in IPloneDbFormsManager.names():
			#print name
			self.failUnless(hasattr(PloneDbFormsManager.PloneDbFormsManager,name),"Method "+name+" misses in PloneDbFormsManager implementation")
		
	'''
	def test_01_managedDBMSList(self,):
		
		dicoSGBD = PloneDbFormsManager.managedDBMSDict()
		for SGBD in dicoSGBD:
			self.failUnless(type(SGBD[0]) == type(""))
			self.failUnless(IPloneDbFormsManager in dicoSGBD[SGBD].__implements__) # chaque element doit implementer IPloneDbFormsManager
			self.failUnless(IPloneDbFormsManager.isImplementedByInstancesOf(dicoSGBD[SGBD]),str(dicoSGBD[SGBD])+" doesnt implements IPloneDbFormsManager")
		self.failUnless("Gadfly" in dicoSGBD and "Psycopg" in dicoSGBD) # Gadfly et Psycopg doivent etre dans la liste
		print "liste des SGBD gerees par PloneDbFormulator ",dicoSGBD
	'''
	'''
	def test_01_1_managedDBMSNames(self,):
		listeNomsSGBD = PloneDbFormsManager.managed_DBMSNames()
		self.failUnless(type(listeNomsSGBD)==type(()))
		self.failUnless("Gadfly" in listeNomsSGBD and "Psycopg" in listeNomsSGBD)
	'''
		
	def test_02_addPloneDbFormsManager(self,):

		
		'''PloneTestCase.setupPloneSite(products=('PloneDbFormulator',))'''
		
		self.failIf(PloneDbFormsManager.addPloneDbFormsManager.__doc__==None,"addPloneDbFormsManager is not documented")
		
		folder = self.folder
		
		pdfsmTest = self.getPdfsmTest()
		self.failUnless(hasattr(folder,'pdfsmTest'))
		self.failUnless(hasattr(pdfsmTest,'references'))
		print "FOLDER CLASS NAME"+pdfsmTest.references.__class__.__name__
		self.failUnless(pdfsmTest.references.__class__.__name__=="Folder")
		self.getPgfsmTest()
		self.failUnless(hasattr(folder,'pgfsmTest'))
		
	def test_03_getDBMSName(self,):
		
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.getDBMSName.__doc__==None,"getDBMSName is not documented")
		
		folder = self.folder
		
		self.failUnless(self.getPdfsmTest().getDBMSName()=="Psycopg")
		#print "gadfly DBMS NAME",self.getPgfsmTest().getDBMSName()
		self.failUnless(self.getPgfsmTest().getDBMSName()=="Gadfly")
		
	
	def test_04_addConnection(self,):
						
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.addConnection.__doc__==None,"addConnection is not documented")

		
		
		
		PloneTestCase.installProduct('ZPsycopgDA')
		folder = self.folder
		pdfsmtest = self.getPdfsmTest()
		
		# doesn't add connection is connection_string is bad
	
		pdfsmtest.addConnection(connection_info="n'importe quoi",title="mon titre")
		self.failIf(hasattr(pdfsmtest,"connection"))
		
		# adds if connection_string is good
		
		pdfsmtest.addConnection(connection_info="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433",title="mon titre")
		
		self.failUnless(hasattr(pdfsmtest,"connection"))
		self.failUnless(pdfsmtest.connection.connection_string=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		
				
		pgfsmtest = self.getPgfsmTest()
		pgfsmtest.addConnection(connection_info="subventions",title="mon titre")

		
	def test_04b_majConnection(self,):
		
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.majConnection.__doc__==None,"majConnection is not documented")
		
		folder = self.folder
		pdfsmtest = self.getPdfsmTest()
		
		# en principe il y a rien au debut
		self.failIf(hasattr(pdfsmtest,"connection"))

		pdfsmtest.addConnection(connection_info="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433",title="mon titre")
		
		
		
		# on teste si la connection se cree quand il n'y en avait pas
		pdfsmtest.majConnection("dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		self.failUnless(hasattr(pdfsmtest,"connection"))
		self.failUnless(pdfsmtest.connection.connection_string=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		
		
		
		# on teste si la connection se met a jour s'il y en avait deja une
		pdfsmtest.majConnection("dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		self.failUnless(hasattr(pdfsmtest,"connection"))
		self.failUnless(pdfsmtest.connection.connection_string=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		
		
		# on teste si la connection ne bouge pas si on a mis une mauvaise connection_string
		pdfsmtest.majConnection("n'importe quoi")
		self.failUnless(hasattr(pdfsmtest,"connection"))
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection.connection_string=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")		
	
	def test_04c_setConnectionInfo(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.setConnectionInfo.__doc__==None,"setConnectionInfo is not documented")
		
		pdfsmtest = self.getConnectedPdfsmTest()
		
		# retourne Faux si la valeur est mauvaise
		self.failIf(pdfsmtest.setConnectionInfo("n'importe quoi"))
		# la valeur ne doit pas avoir change
		self.failUnless(pdfsmtest.connection.connection_string=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron password=car,678 host=138.102.22.9 port=5433")
		
		# change si c'est bon
		self.failUnless(pdfsmtest.setConnectionInfo("dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433"))
		self.failUnless(pdfsmtest.connection_info=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		self.failUnless(pdfsmtest.connection.connection_info=="dbname=cnb2 user=caron_test password=shsd54 host=138.102.22.9 port=5433")
		
	def test_05_factoryTypeInformation(self,):
		self.failUnless(PloneDbFormsManager.factory_type_information[0]['id']=='PloneDbFormsManager')
	
	def test_06_registerType(self,):
		PloneDbFormsManager.registerType(PloneDbFormsManager.PloneDbFormsManager)
	
	def test_07_edit_connection_form_pdbf(self,):
		self.getPdfsmTest().edit_connection_form_pdbf("requete")
	
	def test_08_get_roles_vocabulary(self,):
		
		self.failIf(PloneDbFormsManager.PloneDbFormsManager._get_roles_vocabulary.__doc__==None,"_get_roleslist_vocabulary is not documented")

		rolesList = self.getPdfsmTest()._get_roles_vocabulary()
		self.failUnless("Manager" in rolesList and "Member" in rolesList and "Owner" in rolesList and "Reviewer" in rolesList)
		
		

	def test_09_getDBTablesList(self,):
		
		
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.getDBTablesList.__doc__==None,"getDBTablesList is not documented")

		dbtableslistUnconnected = self.getPdfsmTest().getDBTablesList()
		self.failIf(dbtableslistUnconnected)
		
		dbtableslist = self.getConnectedPdfsmTest().getDBTablesList()
		#print dbtableslist
		self.failUnless("subventions" in dbtableslist)
		self.failIf("pg_tables" in dbtableslist)
		
		

	def test_10_getDBTablesFieldsList(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.getDBTablesFieldsList.__doc__==None,"getDBTablesFieldsList is not documented")

		dbtablefieldslist = self.getConnectedPdfsmTest().getDBTablesFieldsList(tableName='subventions')
		#print "dbtablefieldslist"+str(dbtablefieldslist)
		self.failUnless(dbtablefieldslist==['numero',
						'nom',
						'adresse',
						'fonction',
						'congres',
						'pays',
						'date_a',
						'date_d',
						'communication',
						'somme_demandee',
						'estimation',
						'somme_accordee',
						'remarques',
						'notification',
						'reception_rapport',
						'transmis_tresor']
				)

	def test_11__getTablePkeys(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager._getTablePkeys.__doc__==None,"_getTablePkey is not documented")

		pkeytable = self.getConnectedPdfsmTest()._getTablePkeys(tableName="subventions")
		self.failUnless(pkeytable == ("numero",),str(pkeytable))

	def test_12_getDBStructure(self):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.getDBStructure.__doc__==None,"getDBStructure is not documented")

		dbstructure = self.getConnectedPdfsmTest().getDBStructure()

		self.failUnless("subventions" in dbstructure)

		self.failUnless('remarques' in dbstructure['subventions'])

		print "DBSTRUCTURE"
		print dbstructure
		
		self.failIf(dbstructure['subventions']['remarques']['null'])
		self.failUnless(dbstructure['subventions']['remarques']['type']  == 'text',dbstructure['subventions']['remarques']['type'])
		self.failUnless(dbstructure['subventions']['remarques']['primary_key']  == False)
		self.failUnless(dbstructure['subventions']['numero']['primary_key'] == True)
		self.failUnless(dbstructure['subventions']['remarques']['foreign_key'] == False)
		self.failUnless(dbstructure['subventions']['remarques']['auto_num'] == False)
		# TODO #self.failUnless(dbstructure['subventions']['numero']['unique'] == True)
		self.failUnless(dbstructure['subventions']['remarques']['unique'] == False)
		print "WIDTH"+str(dbstructure['subventions']['remarques']['width'])
		self.failUnless(dbstructure['subventions']['remarques']['width'] == None)

		pass
		
	def test_13__get_tablesList_vocabulary(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager._get_tablesList_vocabulary.__doc__==None,"_get_tablesList_vocabulary is not documented")
		
		tablesList = self.getPdfsmTest()._get_tablesList_vocabulary()
		self.failIf(tablesList)
		
		tablesList = self.getConnectedPdfsmTest()._get_tablesList_vocabulary()
		self.failUnless("subventions" in tablesList)
		
		
		vocabularyWithInsufficientConnection = self.getInsufficientConnectionPdfsm()._get_tablesList_vocabulary()
		print "DBTABLES LIST"+str(vocabularyWithInsufficientConnection)
		self.failIf("subventions" in vocabularyWithInsufficientConnection,"connection to subventions table should'nt be permitted to caron_test user")
		
		
		
	def test_14_getTablesDict(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager._get_tablesList_vocabulary.__doc__==None,"_getTablesDict is not documented")
		
		tablesList = self.getPdfsmTest().getTablesDict()
		
		self.failUnless(tablesList=={})
		
		self.getPdfsmTest().setTablesList(('subventions',))
		print "TABLESLIST",str(self.folder.pdfsmTest.getTablesList())
		tablesDict = self.getPdfsmTest().getTablesDict()
		print "TABLESDICT",str(tablesDict)
		self.failUnless(tablesDict=={'subventions':'subventions'})
		
	def test_15_labelFromId(self,):
		self.failIf(PloneDbFormsManager.PloneDbFormsManager.labelFromId.__doc__==None,"labelFromId is not documented")
		
		self.failUnless(self.getPdfsmTest().labelFromId("titi_TOTO")=="Titi toto")
		
	def test_16_DBType2FormTypes(self,):
		pdfsmtest = self.getPdfsmTest()
		self.failUnless(pdfsmtest.getFormTypesOfDBType('int4')==["IntegerField"])
		
	def test_16_getLenOfDBType(self,):
		pdfsmtest = self.getPdfsmTest()
		self.failUnless(pdfsmtest.getLenOfDBType('int4')==4)
		
	def test_17__getTablePropertiesFromRequest(self,):
		# TOUT DOUX !
		
		folder = self.folder
		
		#folder = makerequest.makerequest(self.folder)
		folder.REQUEST = Request()
		
		
		
		folder.REQUEST.set('QUERY_STRING',QUERY_STRING_SETUPTABLE)
		
		goodProperties = \
		{'fields':
			{'somme_accordee': {'width': 3, 'type': 'IntegerField', 'label': 'Somme accordee'}, 'nom': {'width': 25, 'type': 'StringField', 'label': 'Nom'},
			 'remarques': {'width': 72, 'type': 'StringField', 'label': 'Remarques'}, 
			 'date_d': {'width': 10, 'type': 'DateTimeField', 'label': 'Date d'}, 
			 'pays': {'width': 10, 'type': 'StringField', 'label': 'Pays'}, 
			 'date_a': {'width': 10, 'type': 'DateTimeField', 'label': 'Date a'}, 
			 'notification': {'width': 10, 'type': 'DateTimeField', 'label': 'Notification'}, 
			 'adresse': {'width': None, 'type': 'StringField', 'label': 'Adresse'}, 
			 'numero': {'width': 2, 'null': True, 'type': 'IntegerField', 'primary_key': True, 'label': 'Numero'},
			  'transmis_tresor': {'width': 10, 'type': 'DateTimeField', 'label': 'Transmis tresor'},
			   'reception_rapport': {'width': 10, 'type': 'DateTimeField', 'label': 'Reception rapport'},
			    'communication': {'width': 2, 'type': 'StringField', 'label': 'Communication'},
			     'congres': {'width': 151, 'type': 'StringField', 'label': 'Congres'},
			     'somme_demandee': {'width': 4, 'type': 'IntegerField', 'label': 'Somme demandee'}, 'estimation': {'width': 3, 'type': 'IntegerField', 'label': 'Estimation'},
			      'fonction': {'width': 33, 'type': 'StringField', 'label': 'Fonction'}},
			       
			'rights': {'useModifForm': ['Manager'], 'addModifForm': [], 'useSearchForm': ['Owner', 'Manager', 'Member', 'Authenticated'], 'addSearchForm': ['Owner', 'Manager']}}

		
		
		
		print folder.REQUEST
		
		print "REQUEST FORM "+str(folder.REQUEST.form)
		print 
		tableProperties = self.getPdfsmTest()._getTablePropertiesFromRequest(REQUEST=folder.REQUEST)
		print "TEST TABLE PROPERTIES", str(tableProperties)
		self.failUnless(tableProperties['rights'] and tableProperties['fields'])
		self.failUnless(tableProperties['rights'] == goodProperties['rights'],dict_cmp(tableProperties['rights'],goodProperties['rights']))
		self.failUnless(tableProperties['fields'] == goodProperties['fields'],dict_cmp(tableProperties['fields'],goodProperties['fields']))
		
		
	def test_18a__setTableRights(self,):
		
		tableRights = {'useModifForm': ['Manager'], 'addModifForm': [], 'useSearchForm': ['Owner', 'Manager', 'Member', 'Authenticated'], 'addSearchForm': ['Owner', 'Manager']}
		self.getPdfsmTest().addReferenceForm("subventions")
		tableObject = self.getPdfsmTest().references.subventions
		
		self.getPdfsmTest()._setTableRights(tableObject,tableRights)
		
		self.failUnless(tableObject.addSearchForm==('Owner','Manager',),tableObject.addSearchForm)
		self.failUnless(tableObject.addModifForm==(),tableObject.addModifForm)
		print "settablerights CA PASSE !!!!!!!"
		
	def test_18_setupTableProperties(self,):
				
		#folder = makerequest.makerequest(self.folder)
		folder = self.folder
		
		folder.REQUEST = Request()
		
		request = folder.REQUEST
		
		request.set('QUERY_STRING',QUERY_STRING_SETUPTABLE)
		pdfsmtest = self.getConnectedPdfsmTest()
		pdfsmtest.setupTableProperties(REQUEST=request)
		references = pdfsmtest.references
		
		self.failUnless(hasattr(references,"subventions"))
		
		
		
		# RIGHTS
		subventions = references.subventions
		self.failUnless(subventions.hasProperty("useSearchForm"))
		self.failUnless(subventions.useSearchForm==('Owner', 'Manager', 'Member', 'Authenticated',),subventions.useSearchForm)
		
		
		
		# FIELDS
		self.failUnless(hasattr(subventions,"primary_key"))
		self.failUnless("numero" in subventions.primary_key)
		
		self.failUnless(hasattr(subventions,"numero"))
		self.failUnless(subventions.numero.__class__.__name__ == "IntegerField",
				"numero class should'nt be "+str(references.subventions.numero.__class__.__name__))
		numero = references.subventions.numero
		self.failUnless(numero.get_value('title') == "Numero")
		self.failUnless(numero.get_value('required') == True)
		self.failUnless(numero.get_value('display_width') == 20)
		self.failUnless(references.subventions.pays.get_value('display_maxwidth') == 10)
		self.failUnless(references.subventions.pays.get_value('max_length') == 10)
		#print verifyUnicityConstraint(numero,new_userValue=2)
		#self.failUnless(numero.get_value('external_validator')=='verifyUnicityConstraint',numero.get_value('external_validator'))
		pass
	
	def test_20_addReferenceForm(self,):
		
		self.getPdfsmTest().addReferenceForm("subventions")
		self.failUnless(hasattr(self.folder.pdfsmTest.references,"subventions"))
		print "SUBVENTIONS"+str(self.folder.pdfsmTest.references.subventions)
	
	def test_21_addReferenceField(self,):
		
		self.test_20_addReferenceForm()
		
		referenceFormObject = self.folder.pdfsmTest.references.subventions
		self.folder.pdfsmTest.references.addReferenceField(
				referenceFormObject,"adresse","TextAreaField",
				primary_key=True,auto_num=False,null=True,width=256,unique=True)
		
		self.failUnless(hasattr(referenceFormObject,'adresse'))
		adresse = referenceFormObject.adresse
		self.failUnless(adresse.get_value('title') == "Adresse","adresse title should'nt be"+adresse.get_value('title'))
		self.failUnless(adresse.get_value('required') == True)
		self.failUnless(adresse.get_value('width') == 40,adresse.get_value('width'))
		self.failUnless(adresse.get_value('height') == 7,adresse.get_value('height'))
		
		self.failUnless(adresse.get_value('external_validator')=='verifyUnicityConstraint',adresse.get_value('external_validator'))
		
		self.failUnless("adresse" in referenceFormObject.primary_keys,str(referenceFormObject.primary_keys))
		
	def test_22_addPloneDbFormManager(self,):
		
		pdfsm = self.getPdfsmTest()
		pdfsm.addPloneDbFormManager("aFormManager")
		self.failUnless(hasattr(pdfsm,"aFormManager"))
		newform = pdfsm.aFormManager
		self.failUnless(hasattr(pdfsm.aFormManager,"form"))
	
	def test_23_idSearch(self,):
		
		pdfsm = self.getConnectedPdfsmTest()
		numero2 = pdfsm.idSearch(tableName="subventions",fieldId="numero",userValue=2)
		numero59 = pdfsm.idSearch(tableName="subventions",fieldId="numero",userValue=59)
		self.failUnless(numero2.__class__.__name__ == "r",numero2.__class__.__name__)
		self.failUnless(hasattr(numero2,'pays'),dir(numero2))
		self.failUnless(str(numero2['PAYS'])=="'USA'",str(numero2['pays'])+str(numero2['pays'].__class__)+str(dir(numero2['pays'])))
		self.failIf(numero59)
		
def test_suite():
	""" permet de declarer la classe Test... comme une classe de test, et prepare pour l'ajout a la suite """
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestPloneDbFormsManager))
	return suite