# -*- coding: utf-8 -*-
import sys
import psycopg2

from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, ComputedField, LinesField, IntegerField
from Products.Archetypes.public import SelectionWidget, MultiSelectionWidget, ComputedWidget, StringWidget

from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, ManagePortal
from Products.PageTemplates import PageTemplateFile, PageTemplate

from Products.CMFCore.FSZSQLMethod import FSZSQLMethod
from OFS.Folder import Folder
from Products.Formulator import Form

from interfaces.PloneDbFormsManager import IPloneDbFormsManager
from permissions import *
from validators import verifyUnicityConstraint
from config import *

import PloneDbFormManager


this_module=sys.modules[__name__]

# declares the type properties in plone interface
factory_type_information = (
	{ 'id':'PloneDbFormsManager',
	 'meta_type':'PloneDbFormsManager',
	  'description':'A folder associated to a db providing tools to build interaction forms.',
	   'title':'Db Forms Manager',
	   'content_icon':'multiform.gif',
	    'product':'PloneDbFormulator',
	     'filter_content_types':True,
	      'allowed_content_types':('PloneDbFormManager','DbAddFormManager'),
	     'factory':'addPloneDbFormsManager',
	      'default_view':'folder_listing',
	      'view_methods':('folder_listing','forms_summary','forms_list'),
	      'immediate_view':'view',
	       'actions':({'id':'view',
	   		'name':'View',
	      		'action':'(selected layout)',
		 	'permissions':(ManagePortal,)},
	    
			{'id':'edit_tableFields_properties_form',
		  	'name':'Edit table fields properties',
	     		'visible':0,
	     		'action':'properties',
			'permissions':(ManagePortal,)},
			
			{'id':'setup_tableFields_properties',
			'name':'Setup table fields properties',
			'visible':0,
			'action':'edit_tableFields_properties_form_pdbf',
			'permissions':(ManagePortal,)},
	   	   
	   		{'id':'edit_tables_properties',
		  	'name':'tables properties',
	     		'action':'edit_tables_properties_form_pdbf',
			'permissions':(ManagePortal,)},
		  
			{'id':'initialize_reference_form',
			'name':'Initialize reference form',
			'visible':0,
			'action':'initialize_reference_form',
			'permissions':(ManagePortal,)},
			
			{'id':'customizations_manage',
			'name':'manage customizations',
			'action':'customizations_manage',
			'visible':0,
			'permissions':(ManagePortal,)},
					  
			),
		
	   'aliases':(
	    	{'view':'(selected layout)',
	     	'edit':'atct_edit',
	        'properties':'base_metadata',
		'sharing':'folder_localrole_form',
		 }),

	},
)

# declares archetype fields
schema = ATFolder.schema + Schema((
	ComputedField('DBMSName',
	 			title="Name of the DBMS",
		 		searchable=True,
	       			read_permission=ManagePortal,
		  		write_permission=ManagePortal,
				description="The name of the Database Managing System which you want to manage forms",
	    			expression="here._DBMSName",
	    			widget=ComputedWidget(
		     			visible={'edit':'invisible','view':'invisible'},
					label="Name of the DBMS",
	     			)
	   ),
	StringField('connection_info',
	       			read_permission=ManagePortal,
		  		write_permission=ManagePortal,
	       			required=True,
		  		description="The connection informations",
	      			mutator="majConnection",
		  		widget=StringWidget(label="The connection string"),
	   ),
	
	LinesField('tablesList',
			read_permission=View,
			write_permission=ManagePortal,
	   		accessor="getTablesList",
	   		vocabulary="_get_tablesList_vocabulary",
	      		description="List of tables managed by PloneDbFormulator",
		 	widget = MultiSelectionWidget(
 	    			description="List of tables managed by PloneDbFormulator",
		 		label="Tables List"
			)
	   ),

	 LinesField('addModifFormRole',
			default=('Manager',),
			vocabulary="_get_roles_vocabulary",
			widget = MultiSelectionWidget(
				description="User role that permits adding a form modifying Database content",
				label="add Modify Form"
			)
	   ),
	    
	LinesField('addSearchFormRole',
	 		default=('Manager','Member',),
	    		vocabulary="_get_roles_vocabulary",
	    		required=True,
	       		widget = MultiSelectionWidget(
 	    			description="User role that permits adding a form displaying Database content",
		 		label="add search form",
			)

	   ),
	    
	LinesField('useModifFormRole',
	 		default=('Manager','Member','Owner',),
	    		vocabulary="_get_roles_vocabulary",
	       		enforceVocabulary=1,
	       		widget = MultiSelectionWidget(
 	    			description="User role that permits using a form modifying Database content",
			),
	   	   ),
	    
	LinesField('useSearchFormRole',
	 		default=('Manager','Owner','Member','Authenticated',),
	    		vocabulary="_get_roles_vocabulary",
	    		required=True,
	       		widget = MultiSelectionWidget(
 	    			description="User role that permits using a form displaying Database content",
			),
	   ),	   

	))

	



def addPloneDbFormsManager(container,id,**kwargs):
	""" add to self a PloneDbFormsManager of DBMS """
	object = PloneDbFormsManager(id,**kwargs)
	container._setObject(id, object)
	
	
	
	references = Folder("Forms References of this Forms manager")
	object._setObject("references",references)




class PloneDbFormsManager(ATFolder):
	"""A folder associated to a db providing tools to build interaction forms.
	Psycopg Version by default """
	
	__implements__ = ATFolder.__implements__ + (IPloneDbFormsManager,) 
	schema         = ATFolder.schema.copy()+ schema
	archetype_name = "Db Forms Manager"
	security = ClassSecurityInfo()
	_at_rename_after_creation = True
	formRoles = ["useSearchForm","useModifForm","addSearchForm","addModifForm"]
	
	_DBMSName = "Psycopg"
	_connectionProduct = "ZPsycopgDA"
	_connection_info_name = "Connection String"
	
	# ################################################################################ #
	#       requests and type correspondances : DATABASE MANAGEMENT SYSTEM SPECIFIC    #
	# ##################################################################################
	
	_DBTablesListZSQLFile = 'PloneDbFormulator/SQLRequests/DBTablesList.zsql' # list of all db tables
	_DBTableEntriesZSQLFile = 'PloneDbFormulator/SQLRequests/DBTableEntries.zsql' # all entries of a table (arg tableName:string)
	_DBTablePkeyZSQLFile = 'PloneDbFormulator/SQLRequests/DBTablePkey.zsql' # list of all primary keys of a table (arg tableName)
	_DBTableFieldsZSQLFile = 'PloneDbFormulator/SQLRequests/DBTableFields.zsql' # list of fields of a table, with Type and Not null information TODO : UNIQUE, width
	_IDSearchZSQLFile = 'PloneDbFormulator/SQLRequests/IDSearch.zsql' # entry of a table corresponding to a couple (field,value)
	
	# form types lists corresponding to db field types
	_DBType2FormTypes = {
		'int4':["IntegerField"],
		'int2':["IntegerField"],
		'bool':["CheckBoxField"],
		'oid':["IntegerField","StringField","PatternField","ListField","RadioField"],
		'char':["StringField","PatternField","RadioField","ListField"],
		'text':["StringField","TextAreaField","LinkField",
           "PasswordField","PatternField","RadioField","ListField","RawTextAreaField",
	   "EmailField","FileField"],
	   	'varchar':["StringField","PasswordField","PatternField","RadioField","ListField",
	   "EmailField","FileField"],
	   	'date':["DateTimeField"],
		'float4':["FloatField"],
		'float8':["FloatField"],
	}
	
	# dimensions (in octets) corresponding to db type
	_DBType2len = {
		'bool':1,
		'char':1,
		'name':64,
		'int8':8,
		'int2':2,
		'int2vector':64,
		'int4':4,
		'line':32,
		'float4':4,
		'float8':8,
		'money':4,
		'time':8,
		'text':None,
		'varchar':None,
		'date':None,
		'oid':8}
	
	_DBStructure = {} # the structure of the database. for caching and modifying
	
	def getLenOfDBType(self,DBtype):
		if not type(DBtype) == type(""):
			raise TypeError
		
		if self._DBType2len.has_key(DBtype):
			return self._DBType2len[DBtype]
		else:
			raise str(DBtype)+" type is not managed by _DBType2len. patch it if necessary"
	
	def getFormTypesOfDBType(self,DBtype=""):
		if not(DBtype):
			return self._DBTypes2FormTypes
		if not type(DBtype) == type(""):
			raise TypeError
		if self._DBType2FormTypes.has_key(DBtype):
			return self._DBType2FormTypes[DBtype]
		else:
			raise str(DBtype)+" type is not managed by _DBType2FormTypes. patch it if necessary"
		
	# ################## CONNECTION RELATED METHODS #################################
	
	security.declarePublic('getDBMSName')
	def getDBMSName(self):
		""" returns the name of the sgbd """
		return self._DBMSName

	
	security.declareProtected(ManagePortal,'addConnection')
	def addConnection(self,connection_info,**kwargs):
		""" (psycopg) creates the connection, if not exists """
		try:
			self.manage_addProduct['ZPsycopgDA'].manage_addZPsycopgConnection("connection","connection",connection_info,check=True)
			self.connection_info = connection_info
			return True
		except psycopg2.OperationalError:
			return False
	
			
	security.declareProtected(ManagePortal,'majConnection')
	def majConnection(self,connection_info,**kwargs):
		""" (all) changes connection informations 
		 creates a db connector if not exists """
		if not(hasattr(self,'connection')):
			self.addConnection(connection_info,**kwargs)
		else:
			self.setConnectionInfo(connection_info)
		pass
	
	security.declareProtected(ManagePortal,'setConnectionInfo')
	def setConnectionInfo(self,connection_string):
		""" sets connection_string value (psycopg), returns False if connection string is bad """
		self.connection.manage_close_connection()
		old_connection_info = self.connection.connection_info
		
		self._DBStructure = {} # initialize db structure in 'cache'
		
		try:
			self.connection.connection_string = connection_string
			
			self.connection.manage_open_connection()
			self.connection_info = connection_string
			self.connection.manage_close_connection()
			return True
		
		except psycopg2.OperationalError:
			self.connection.connection_string = old_connection_info
			self.connection_info = old_connection_info
			return False
		
		
		
	security.declareProtected(View,'userCanViewDbForm')
	def userCanViewDbForm(self,form):
		""" returns True if authenticated user can view object form, else False  """
		if isinstance(form, PloneDbFormManager.PloneDbFormManager):
			return True
		elif 0: # if user has rights
			return True
		else:
			return False

	# ############################### DATABASE INFORMATIONS ################################

	security.declareProtected(View,'getDBTablesList')
	def getDBTablesList(self):
		""" returns the tables of the database (psycopg) - only ones that may be interesting for making forms string list """
		if not hasattr(self,"connection"):
			return []
		
		else:
			request = FSZSQLMethod(self,self._DBTablesListZSQLFile)
			request.connection = self.connection
			request.connection.manage_open_connection()
			tablesList = [result['tablename'] for result in request() \
				if not(result['tablename'].startswith("pg_") or result['tablename'].startswith("sql_"))]
			request.connection.manage_close_connection()
			return tablesList

	def _get_tablesList_vocabulary(self):
		""" returns a DisplayList object for List widgets, containing the tables that can be managed """
		tablesList = self.getDBTablesList()
		
		tablesItems = tuple()
		
		for table in tablesList:
			
			try:
				self.getDBTablesFieldsList(table)
				# get tables which read is authorized by connection string
				tablesItems += ((table,table),)
				
			except psycopg2.ProgrammingError:
				
				pass

		return DisplayList(tablesItems)
	
			
	security.declareProtected(View,'getDBTablesFieldsList')	
	def getDBTablesFieldsList(self,tableName):
		""" returns list of tableName table fields """
		request = FSZSQLMethod(self,self._DBTableEntriesZSQLFile)
		request.connection = self.connection
		request.connection.manage_open_connection()
		result = request(tableName=tableName)
		request.connection.manage_close_connection()
		return result.names()
	
	
	security.declareProtected(View,'getDBStructure')	
	def getDBStructure(self,):
		""" psycopg version
		
		structure :

    {<tableName_str>:
        {<fieldName_str>:
             {'primary_key':<boolean>,'width':<integer>,'null':<boolean>,'foreign_key':(<table_str>,<field_str>),'type':<str>,'auto_num':<bool>}
         },
 ...}
"""
		structure = {}

		fieldslistRequest = FSZSQLMethod(self,self._DBTableFieldsZSQLFile)
		fieldslistRequest.connection = self.connection
		fieldslistRequest.connection.manage_open_connection()
		
		for table in self.getDBTablesList():
			
			if self._DBStructure:
				if self._DBStructure.has_key(table):
					if self._DBStructure[table]: # use saved config if exists
						structure[table] = self._DBStructure[table]
						break
			
			structure[table] = {}
			fieldslistResult = fieldslistRequest(tableName=table)
			
			tablePkey = self._getTablePkeys(table)
			
			for field in fieldslistResult:
				
				fieldDefs = {}
				fieldDefs['primary_key'] = (field['field'] in tablePkey)
				fieldDefs['foreign_key'] = False # TODO
				fieldDefs['auto_num'] = False # TODO
				fieldDefs['width'] = self._DBType2len[field['type']]
				fieldDefs['null'] = field['not_null'] or fieldDefs['primary_key']
				fieldDefs['type'] = field['type']
				fieldDefs['unique'] = False # TODO
				fieldDefs['label'] = self.labelFromId(field['field'])
	
				structure[table][field['field']]=fieldDefs
		
		fieldslistRequest.connection.manage_close_connection()
		
		self._DBStructure = structure
		return structure
	
	
	security.declareProtected(View,'_getTablePkeys')		
	def _getTablePkeys(self,tableName):
		""" returns the name of table primary keys """
		pkeylistRequest = FSZSQLMethod(self,self._DBTablePkeyZSQLFile)
		pkeylistRequest.connection = self.connection
		pkeylistRequest.connection.manage_open_connection()
		pkeylistResults = pkeylistRequest(tableName=tableName)
		tableKeys = tuple()
		for pkeylistResult in pkeylistResults:
			tableKeys += (pkeylistResult['field'],)
		pkeylistRequest.connection.manage_close_connection()
		return tableKeys

	def idSearch(self,fieldId="",userValue="",tableName=""):
		if not(tableName) and hasattr(self,'tableName'):
			tableName = self.tableName
		
		idSearchRequest = FSZSQLMethod(self,self._IDSearchZSQLFile)
		idSearchRequest.connection = self.connection
		idSearchRequest.connection.manage_open_connection()
		idSearchResults = idSearchRequest(fieldId=fieldId,userValue=str(userValue),tableName=tableName)
		idSearchRequest.connection.manage_close_connection()
		
		if len(idSearchResults) > 1:
			raise "the couple "+fieldId+"/"+userValue+" doesn't make a primary key"
			
		elif len(idSearchResults) < 1:
			return None
		else:
			return idSearchResults[0]
		
		
		
	# #################### TABLES AND FIELDS FORMS RELATED METHODS
	
	security.declareProtected(View,'getTablesDict')
	def getTablesDict(self):
		""" returns the dictionnary of form tables chosen by user, with their title, if defined """
		
		tablesList = {}
		
		for table in self.getTablesList():
			if hasattr(self.references,table) and getattr(self.references,table).title:
				tablesList[table] = getattr(self.references,table).title
			else:
				tablesList[table]=table
		
		return tablesList
	
	
	security.declareProtected(ManagePortal,'setupTableProperties')
	def setupTableProperties(self,REQUEST=None):
		""" creates the reference form of the table (in request), with formulator 
		properties are fields (name, type, label, width and constraints)
		and rights
		"""
		
		
		
		parameters = REQUEST.form
		tableName = parameters['tableName'] # name of the table
		tableProperties = self._getTablePropertiesFromRequest(REQUEST)
		
		# creation of the reference table, a formulator form representing the table structure
		self.addReferenceForm(tableName)
		tableForm = getattr(self.references, tableName)
		
			
		
		# set table rights
		self._setTableRights(tableForm,tableProperties['rights'])
		
		
		tableFields = tableProperties['fields']
		self._DBStructure[tableName] = tableFields
		
		# the reference form contains a formulatorField by field
		
		for fieldName in tableFields:
			
			fieldProperties = tableFields[fieldName]
			
			if not(fieldProperties.has_key('primary_key')): fieldProperties['primary_key']=False
			if not(fieldProperties.has_key('null')): fieldProperties['null']=False
			if not(fieldProperties.has_key('width')): fieldProperties['width']=0
			if not(fieldProperties.has_key('auto_num')): fieldProperties['auto_num']=False
			
			
			self.addReferenceField(tableForm,fieldName,
					fieldType=fieldProperties['type'],
					title=fieldProperties['label'],
					primary_key=fieldProperties['primary_key'],
					auto_num=fieldProperties['auto_num'],
					width=fieldProperties['width'],
					null=fieldProperties['null'])
			
			#print tableForm,field,fieldProperties['type'],fieldProperties['label']
		#return self._DBStructure
		REQUEST.response.redirect("./edit_table_properties_form_pdbf?tableName="+tableName)
		
	security.declareProtected(ManagePortal,'editTableProperties')
	def editTableProperties(self,REQUEST=None):
		""" edits the reference table properties with form values
		"""
		
		
		# ############### DUPLICATION DE CODE !!!
		parameters = REQUEST.form
		tableName = parameters['tableName'] # name of the table
		
		tableProperties = self._getTablePropertiesFromRequest(REQUEST)

		tableForm = getattr(self.references, tableName)
		
		# set table rights
		self._setTableRights(tableForm,tableProperties['rights'])
		
		tableForm.manage_changeProperties({"primary_keys":tuple()})
		
		tableFields = tableProperties['fields']
		self._DBStructure[tableName] = tableFields
		
		# the reference form contains a formulatorField by field
		
		for fieldName in tableFields:
			
			fieldProperties = tableFields[fieldName]
			
			if not(fieldProperties.has_key('primary_key')): fieldProperties['primary_key']=False
			if not(fieldProperties.has_key('null')): fieldProperties['null']=False
			if not(fieldProperties.has_key('width')): fieldProperties['width']=0
			if not(fieldProperties.has_key('auto_num')): fieldProperties['auto_num']=False
			
			
			self.editReferenceField(tableForm,fieldName,
					title=fieldProperties['label'],
					primary_key=fieldProperties['primary_key'],
					auto_num=fieldProperties['auto_num'],
					width=fieldProperties['width'],
					null=fieldProperties['null'])
			
			#print tableForm,field,fieldProperties['type'],fieldProperties['label']
		
		#return self._DBStructure
		REQUEST.response.redirect("./edit_table_properties_form_pdbf?tableName="+tableName)
		
			
	def _getTablePropertiesFromRequest(self,REQUEST=None):
		# creates two dictionnaries about the table : {'fields':{},'rights':{}}
		# rights dictionnary, about rights and roles {right str: [role str]}
		# fields dictionnary, containing a dictionnary of fields and parameters {fieldName str:{fieldParameter str: parameterValue div}}
		
		form = REQUEST.form
				
		tablePropertiesDicts = {'fields':{},'rights':{}}

		# parses the request datas

		for finput in form:
			# field parameters
			if finput.find('.')>-1:
				parameter = finput.split('.')
				fieldParam = parameter[0]
				paramParam = parameter[1]
				# parameter[0] : field name, parameter[1] : property, form[input] : param value
				
				
				if not(tablePropertiesDicts['fields'].has_key(fieldParam)):
					tablePropertiesDicts['fields'][fieldParam]={'label':self.labelFromId(fieldParam)}
				
				# property value from parameter value :
				if paramParam in ["primary_key","null","auto_num"]:
					valueParam = True
				elif paramParam in ["width"]:
					if not form[finput]:
						valueParam=None
					else:
						valueParam = int(form[finput])
				else:
					valueParam = form[finput]
				
				tablePropertiesDicts['fields'][fieldParam][paramParam]=valueParam
		
			elif finput.find('_roles')>-1:
			# rights parameters
				right = finput.split('_')[0]
				#if not right in tablePropertiesDicts['rights']:
				#	tablePropertiesDicts['rights'][right] = []
				if type(form[finput]) == type(["",""]):
					tablePropertiesDicts['rights'][right] = form[finput]
				elif not(form[finput]):
					tablePropertiesDicts['rights'][right] = []
				elif type(form[finput]) == type(""):
					tablePropertiesDicts['rights'][right] = [form[finput]]

		# dans le cas d'une liste a choix multiple, quand on ne choisit rien,
		# le champ n'est pas envoye dans la requete
		
		# when no right is given :
		for role in self.formRoles:
			if not(tablePropertiesDicts['rights'].has_key(role)):
				tablePropertiesDicts['rights'][role] = []

		return tablePropertiesDicts



	# ############## MANAGEMENT OF REFERENCES FOLDER ###########
	# IN THE FUTURE : I SHOULD CREATE A REFERENCE TABLE OBJECT #


			
	# PB DE CONCEPTION : IL DEVRAIT Y AVOIR UN OBJECT REFERENCEFORM

	# ######## TABLES / REFERENCE FORMS
	
	def addReferenceForm(self,tableName):
		""" adds a reference form of this table """
		Form.manage_add(
			self.references, id=tableName, title=self.labelFromId(tableName), unicode_mode=True
			)
		referenceForm = getattr(self.references,tableName)
		referenceForm.manage_addProperty('primary_keys',[],'lines')
		setattr(referenceForm,'stored_encoding',"UTF-8")
	
	def initialize_reference_form(self,tableName,REQUEST=None):
		""" deletes the reference form """
		self._DBStructure[tableName] = {}
		references = self.references
		if hasattr(references,tableName):
			references.manage_delObjects(ids=[tableName])
		if REQUEST:
			REQUEST.response.redirect(self.absolute_url()+"/edit_table_properties_form_pdbf?tableName=subventions&portal_status_message="+tableName+" has been initialized")
		else:
			return references
		
	def _setTableRights(self,tableObject,tableRights):
		""" set ups the table rights (dict tableRights) of tableObject """

		for permission in self.formRoles:
			""" creates the permission as property """
			if not(tableObject.hasProperty(permission)):
				tableObject.manage_addProperty(permission,tuple(),"lines")
			
			""" setups the property value """
			tableObject.manage_changeProperties({permission:tableRights[permission]})
		pass
			
	security.declareProtected(View,'getReferenceTablesList')
	def getReferenceTablesList(self):
		references = self.references
		return [table for table in self.references.objectIds() if getattr(references,table).__class__.__name__=="ZMIForm"]
	
	
	# ######## FIELDS / REFERENCE FIELDS	
	def addReferenceField(self,referenceFormObject,fieldName,
					fieldType="StringField",
					title="",
					primary_key=False,
					auto_num=False,
					null=True,
					width=8,
					unique=False):
		""" adds a reference field with those properties """
		
		if not(title):
			title = self.labelFromId(fieldName)
		
		referenceFormObject.manage_addField(fieldName,Form.convert_unicode(title),fieldType)
		field = getattr(referenceFormObject,fieldName)

		field.db_width = width
		initialSettingsDictionnary = {'required':null,'title':title,'unicode':True}
		

		# VALIDATION CONSTRAINTS : a ameliorer
		if width:
			if field.has_value('end'): # pour les entiers qui peuvent avoir un maximum
				initialSettingsDictionnary['start']= 0 - (2 ** (2**width)) / 2 -1
				initialSettingsDictionnary['end']= (2 ** (2**width)) / 2 +1
				initialSettingsDictionnary['display_maxwidth'] = (2 ** (2**width))/10+1
	
			elif field.has_value('max_length'):
				initialSettingsDictionnary['max_length'] = width
				if fieldType in ["TextAreaField","RawTextAreaField"]:
					initialSettingsDictionnary['width']=40
					initialSettingsDictionnary['height']=width/40+1
				else:
					initialSettingsDictionnary['display_maxwidth'] = 2**width
				
		if primary_key:
			# primary keys are stored as a reference form property
			referenceFormObject.manage_changeProperties(
				{"primary_keys":referenceFormObject.primary_keys + (fieldName,)})
		
		if unique: # TODO
			initialSettingsDictionnary['external_validator']="verifyUnicityConstraint"
			
		if auto_num:
			initialSettingsDictionnary['override_default']="sequelAutoNum"
			
		field.initialize_values(initialSettingsDictionnary)
	
	def editReferenceField(self,referenceFormObject,fieldName,
					title="",
					primary_key=False,
					auto_num=False,
					null=True,
					width=8,
					unique=False):
		""" adds a reference field with those properties """
		
		if not(title):
			title = self.labelFromId(fieldName)
		
		tableName = referenceFormObject.getId()
		# save settings
		self._DBStructure[tableName][fieldName]={}
		self._DBStructure[tableName][fieldName]['primary_key'] = title
		self._DBStructure[tableName][fieldName]['primary_key'] = primary_key
		self._DBStructure[tableName][fieldName]['null'] = null
		self._DBStructure[tableName][fieldName]['auto_num'] = auto_num
		self._DBStructure[tableName][fieldName]['null'] = null
		self._DBStructure[tableName][fieldName]['width'] = width
		self._DBStructure[tableName][fieldName]['unique'] = unique	
		self._DBStructure[tableName][fieldName]['label'] = title
		
		# build field properties from settings
		field = getattr(referenceFormObject,fieldName)

		
		settingsDictionnary = {}
		


		# VALIDATION CONSTRAINTS : a ameliorer !!! DUPLICATION DE CODE
		if width:
			if field.has_value('end'): # pour les entiers qui peuvent avoir un maximum
				settingsDictionnary['start']= 0 - (2 ** (2**width)) / 2 -1
				settingsDictionnary['end']= (2 ** (2**width)) / 2 +1
				settingsDictionnary['display_maxwidth'] = (2 ** (2**width))/10+1
	
			elif field.has_value('max_length'):
				settingsDictionnary['max_length'] = width
				if field.meta_type in ["TextAreaField","RawTextAreaField"]:
					settingsDictionnary['width']=40
					settingsDictionnary['height']=width/40+1
				else:
					settingsDictionnary['display_maxwidth'] = width
				
		if primary_key:
			# primary keys are stored as a reference form property
			referenceFormObject.manage_changeProperties(
				{"primary_keys":referenceFormObject.primary_keys + (fieldName,)})
		
		if unique: # TODO
			settingsDictionnary['external_validator']="verifyUnicityConstraint"
			
		if auto_num:
			settingsDictionnary['override_default']="sequelAutoNum"
			
		for setting in settingsDictionnary:
			field.values[setting] = settingsDictionnary[setting]
	
				
	
	security.declareProtected(View,'getReferenceField')
	def getReferenceField(self,tableName,fieldName):
		""" returns the reference field 'fieldName' of table 'tableName' """
		table = getattr(self.references, tableName)
		return getattr(table, fieldName)
	
	security.declareProtected(View,'getFieldWidth')
	def getFieldWidth(self,tableName,fieldName):
		""" returns the field with, if set """
		fieldWidth = getattr(getattr(self.references, tableName), fieldName).db_width
		if fieldWidth:
			 return fieldWidth
		else:
			 return None
	
	# #################### SECURITY RELATED METHODS
	
	security.declareProtected(View,'roleHasDbFormPermissionOnTable')
	def roleHasDbFormPermissionOnTable(self,role,permission,tableName):
		""" returns true if 'role' has 'permission' set (by archetype field) on 'tableName' """
		if not(hasattr(self.references,tableName)):
			return None
		
		table = getattr(self.references,tableName)
		permission = getattr(table,permission)
		if role in permission:
			return "selected"
		else:
			return None

	def _get_roles_vocabulary(self):
		""" returns a DisplayList object for List widgets, containing the roles list in the object context """
		rolesList = self.validRoles()
		
		rolesItems = tuple()
		
		for role in rolesList:
			rolesItems += ((role,role),)

		return DisplayList(rolesItems)


	# ############################### ADDING A FORM

	def addPloneDbFormManager(self,id):
		""" adds a form manager in the current forms manager """
		PloneDbFormManager.addPloneDbFormManager(self,id)


	# #################### TOOLS #####################
	# qui auraient davantage leur place dans un tool #	
	# je ne les interface pas #

	def labelFromId(self,id):
		""" cree un label a partir de l'id majuscule premiere lettre + minuscules et espaces a la place des _"""
		id = id[0].upper() + id[1:].lower()
		id = id.replace("_"," ")
		id = id.replace("ee","ée")
		return id

	def normalizeSQL(self,fieldValue):
		""" returns a value adaptated to sql input
		returns none if null """
		if not(fieldValue):
			return None
		else:
			return fieldValue


registerType(PloneDbFormsManager)



def managedDBMSDict(): # inutilise
	""" returns dict of DBMS managed by this version of PloneDbFormulator, even if patched, associated to the class 
	{_DBMSName:str: PloneDbFormsManager:class,} """
	PloneDbFormsManagerObjects = [this_module.__dict__[objectName] for objectName in this_module.__dict__]
	PloneDbFormsManagerList = interfacedList(PloneDbFormsManagerObjects, IPloneDbFormsManager)
	""" each PloneDbFormsManager implementing IPloneDbFormsManager manages a DBMS """
	dict = {}
	for PloneDbFormsManagerClass in PloneDbFormsManagerList:
		dict[PloneDbFormsManagerClass._DBMSName] = PloneDbFormsManagerClass
	return dict

def managed_DBMSNames(): # inutilise
	_DBMSNames = managedDBMSDict()
	return tuple(_DBMSName for _DBMSName in _DBMSNames)

def interfacedList(objectList,interface): # inutilise
	""" returns the objects in objectList (classes, instances...) that implements interface (class) """
	interfaced = []
	for object in objectList:
		if hasattr(object,"__implements__"):
			if not(type(object.__implements__) in [tuple]):
				pass
			elif interface in object.__implements__:
				interfaced.append(object)
			else: 
				pass
	return interfaced