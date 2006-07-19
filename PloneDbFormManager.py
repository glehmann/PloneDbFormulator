from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import View, ModifyPortalContent, ManagePortal

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import BaseFolder, BaseSchema, Schema, registerType, DisplayList
from Products.Archetypes.public import StringField, LinesField, ReferenceField
from Products.Archetypes.public import MultiSelectionWidget, BooleanWidget, SelectionWidget
from Products.Archetypes.public import ReferenceWidget

from Products.Formulator.Form import ZMIForm
from Globals import DTMLFile
from OFS.DTMLMethod import DTMLMethod
from Products.PythonScripts.PythonScript import PythonScript

import psycopg2


from permissions import *

from interfaces.PloneDbFormManager import IPloneDbFormManager
from interfaces.PloneDbFormsManager import IPloneDbFormsManager

from trucs import same_type

#from Products.PloneDbFormulator.PloneDbFormsManager import PloneDbFormsManager

def addPloneDbFormManager(self,id,REQUEST=None,**kwargs):
	""" adds a form manager in the self container """
	
	""" for the moment, can only create it in a PloneDbFormsManager """
	object = PloneDbFormManager(id,**kwargs)
	self._setObject(id, object)
	form = ZMIForm("form", "form", unicode_mode=True)
	object._setObject("form",form)

factory_type_information = (
	{ 'id':'PloneDbFormManager',
	'meta_type':'PloneDbFormManager',
	'description':'An interaction form to the database',
	'title':'Database Form',
	'content_icon':'formmanager.gif',
	'product':'PloneDbFormulator',
	'factory':'addPloneDbFormManager',
	'default_view':'view_form',
	'immediate_view':'edit',
	'filter_content_types':True,
	'allowed_content_types':(),
	'global_allow':False,
	'actions':(
		{'id':'view',
			'name':'View the form',
			'action':'view_form',
			'visible':1,
			'permissions':(UseForm,)},
		{'id':'edit',
			'name':'Edit Form Properties',
			'visible':1,
			'action':'edit',
			'permissions':(ModifyPortalContent,)},
			
			
		{'id':'customizeSQLRequest',
			'name':'customize request',
			'action':'customizeSQLRequest',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
		
		{'id':'customizePre_script',
			'name':'customize pre script',
			'action':'customizePre_script',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
			
		{'id':'customizePost_script',
			'name':'customize post script',
			'action':'customizePost_script',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
			
		{'id':'customizeForm_body',
			'name':'customize form',
			'action':'customizeForm_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
			
		{'id':'customizeResults_body',
			'name':'customize results list',
			'action':'customizeResults_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
			
		{'id':'customizeEntry_body',
			'name':'customize entry',
			'action':'customizeEntry_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
			
		{'id':'customize_form',
			'name':'customize_form',
			'action':'customize_form',
			'visible':0,
			'permissions':(ModifyPortalContent,)},
			
		{'id':'setCustomized',
			'name':'setCustomized',
			'action':'setCustomized',
			'visible':0,
			'category':'object_buttons',
			'permissions':(ModifyPortalContent,)},
		
		{'id':'setDefault',
			'name':'set default',
			'action':'setDefault',
			'visible':0,
			'permissions':(ModifyPortalContent,)},
			
		
			
		),
			
		
	'aliases':({
		'view'	: 'view_form',
		'edit'	: 'base_edit',
		'sharing' : 'sharing',
		'properties':'base_metadata'
		}),

	},
)	


PloneDbFormManagerSchema  = Schema((
	StringField('tableName',
		vocabulary="_get_tableName_vocabulary",
		description = "The Name of the related table",
		widget=SelectionWidget(label="Table managed by this form"),
		),
	LinesField('requestFields',
		vocabulary="_get_field_list_vocabulary",
		mutator="setRequestFields",
		description = "Database Fields used by SQL request",
		widget = MultiSelectionWidget(label="Field widgets of the form")
		),

	LinesField('entryFields',
		vocabulary="_get_field_list_vocabulary",
		description = "Database Fields which are displayed on unique result page",
		widget = MultiSelectionWidget(label="Fields displayed on the detailed view of an entry")
		),
	LinesField('useFormRoles',
		vocabulary="_get_useForm_roles_vocabulary",
		description="Roles that have permission to use this form",
		widget = MultiSelectionWidget(label="Roles that have permission to use this form"),
	),


))


class PloneDbFormManager(ATFolder):
	""" manages an interaction form with a database. search form by default """
	
	formTypeSchema = Schema((
	LinesField('requestFields',
		vocabulary="_get_field_list_vocabulary",
		mutator="setRequestFields",
		description = "Database Fields used by SQL request",
		widget = MultiSelectionWidget(label="Field widgets of the form")
		),
	LinesField('resultFields',
		vocabulary="_get_field_list_vocabulary",
		description = "Database Fields which are displayed on results list page",
		widget = MultiSelectionWidget(label="Fields displayed in the results list")
		),
	LinesField('allowRegexp',
		description="Allow regular expressions in fields",
		widget = BooleanWidget(label="Allow regular expressions in fields"),
		),
	
	))
	
	__implements__ = ATFolder.__implements__ + (IPloneDbFormManager,) 
	schema         = ATFolder.schema.copy()+ PloneDbFormManagerSchema + formTypeSchema
	_at_rename_after_creation = True
	
	# ZSQL type corresponding to field type (works for all connector types)
	_FormType2ZSQLType = {'CheckBoxField':'string',
		'DateTimeField':'string',
		'EmailField':'string',
		'FakeField':'string',
		'FileField':'string',
		'FloatField':'float',
		'IntegerField':'int',
		'LabelField':'string',
		'LinesField':'string',
		'LinkField':'string',
		'ListField':'string',
		'MultiCheckBoxField':'string',
		'MultiListField':'string',
		'PasswordField':'string',
		'PatternField':'string',
		'RadioField':'int',
		'RawTextAreaField':'string',
		'StringField':'string',
		'TextAreaField':'string'}
	
	
	# ###############################################################
	#      FORM TYPE (add/search/update...) RELATED INFORMATION     #
	#                        -- SEARCH FORM --                      #
	# ###############################################################
	
	_forbiddenWords = ['update','create','insert','delete','database']
	'''
	actions = (
		{'id':'view',
		'name':'View',
		'action':'view_forms_list',
		'permissions':(View,)},
		{'id':'edit',
		'name':'Edit',
		'action':'base_edit',
		'permissions':(ModifyPortalContent,)}
		)
	'''	
	
	_formType = "searchForm" # id name of type let's create subclasses for other form types
	_formRightsType = "SearchForm" # only SearchForm or ModifForm
	_formMessage = "Search" # add, update, search...

	addPermission = CreateSearchForm
	usePermission = UseSearchForm
	
	archetype_name = "Database Search Form"
	
	security = ClassSecurityInfo()
	
	
	# ################# FORM DISPLAYING AND EXECUTION ######
	

	security.declareProtected(View,'contextFieldsList')
	def contextFieldsList(self,parametre=[]):
		"""
		renvoit la liste des champs de form correspondant aux id de champs et de groupes en parametre, qui est une chaine ou une liste de chaines
		s'il n'y a pas de parametre, renvoit tous les champs de form ou tous les champs du groupe contextuel
		"""
		context=self
		# GESTION DES PARAMETRES SPECIAUX
		
		# pas de parametre : tous les champs
		if not(parametre):
			# est on dans une sequence... 
			if hasattr(context,'sequence-item'):
				# et l'iteration correspond-elle a un nom de groupe ?
				group = getattr(context,'sequence-item')
				if group in [group.getId() for group in context.form.get_groups()]:
					# si oui on recupere l'id du groupe et on en fait le parametre
					parametre = [group.getId()]
		
				else:
					# sinon, alors on renvoit tous les champs
					return context.form.get_fields() 
			else:
				return context.form.get_fields()
		
		
		# si le parametre contient une chaine, alors on la considere comme une liste contenant uniquement cette chaine
		elif same_type(parametre,""):
			parametre = [parametre]
		
		
		# CONSTRUCTION DE LA LISTE
		
		FieldList = []
		
		# si le parametre contient une liste, on renvoit la liste tous les champs dont l'id est dans cette liste
		
		if same_type(parametre,[]):
			for idGroupOrField in parametre:
			# si l'element de la liste est un nom de champ, on ajoute le champ
				if idGroupOrField in context.form.get_field_ids():
					FieldList.append(context.form.get_field(idGroupOrField))
				# si l'element de la liste est un nom de groupe, on ajoute les champs du groupe
				elif idGroupOrField in [group for group in context.form.get_groups()]:
					for group \
					  in [group for group in context.form.get_groups() if group == idGroupOrField]:
						FieldList = FieldList + context.form.get_fields_in_group(group)
						break
			
		return [field.getId() for field in FieldList]
	
	security.declareProtected(View,'fieldNamesStrList')
	def fieldNamesStrList(self):
		""" returns a string of the request field names separated by commas (for sql request) """
		NamesStrList = ""
		for field in self.form.get_fields()[:-1]:
			NamesStrList += field.getId()+","
			
		NamesStrList += self.form.get_fields()[-1].getId()
		return NamesStrList

				
	def getPkeys(self):
		""" gets the pkeys related to the form """
		return getattr(self.references,self.tableName).primary_keys
		
	security.declareProtected(View,'entryRequest')
	def entryRequest(self,currentResult):
		""" builds a link towards an entry from the current results row """
		
		pkeys = self.getPkeys() # list of primary keys of the current table
		
		httpRequest = self.absolute_url()+'?'
		
		
		for pkey in pkeys:
			httpRequest += pkey+"="
			httpRequest += str(currentResult[pkey])+"&"
		
		httpRequest+="entry_submission=1"
		
		return httpRequest
				
				
	def getFormType(self):
		""" gets form type (add form, search form, etc)"""
		return self._formType
	
	
	def getFormMessage(self):
		""" gets form message, for buttons, titles... """
		return self._formMessage
	
	
	def emptyForm(self):
		""" returns true if the form hasn't yet been completed at all, or false """
		REQUEST = self.REQUEST
		for field in self.form.get_fields():
  			 if REQUEST[field.getId()]:
				 return False

		return True
	
		
	# #######################################################
	# 		FUNCTIONAL CUSTOMIZATION		#
	# #######################################################
	

	# ############# SET DEFAULT
	
	security.declareProtected(addPermission,"setDefault")
	def setDefault(self,REQUEST=None):
		""" delete customization of 'customize' (in request) by deleting the object """
				
		if  REQUEST.form.has_key('customize'):
			customize = REQUEST.form['customize']
			self.manage_delObjects([customize])
			message = customize+" has been deleted"
		else:
			message = customize+" was not customized"
		REQUEST.response.redirect(self.absolute_url()+"?portal_status_message="+message)
	
	# ########## Edit customized method
	
	security.declareProtected(addPermission,"setCustomized")
	def setCustomized(self,REQUEST=None):
		""" edits the body of customized method """
		customize = REQUEST.form['customize']
		customizedBody = REQUEST.form['customizedBody']
		
		set_method = getattr(self,"setCustomized_"+customize)
		message = set_method(customizedBody) # executes the set method for this customized method
		
		REQUEST.response.redirect(
			self.absolute_url()+"/customize_form?customize="+customize+"&portal_status_message="+message)
			
			
	# ############ create customized method :
	# related to method
	
	
	# ############### SQL REQUEST MANAGEMENT #############################

	_SQLRequestName = "searchFormZSQL" # name of the request
	
	
	def getSQLText(self,**kwargs):
		if not(self._formType=="searchForm"):
			return self.getSQLModifRequest()(src__=1,**kwargs)
		else:
			return self.getSQLSearchRequest()(src__=1,**kwargs)
			

	def getSQLResults(self,**kwargs):
		#REQUEST.form['numero']
		return self.getSQLSearchRequest()(**kwargs)
	

	security.declareProtected(usePermission,'getSQLRequest')
	def getSQLSearchRequest(self,**kwargs):
		""" gets the SQL Search Request associated to this form : 
			the main SQL Request for search request
			or the entry request for modification requests """
		
		# if we are in a modification form, returns the request searching for the entry
		if not(self._formType=="searchForm"):
			return self.entrySearchSQL
		
		# if search request has been customized
		if "SQLRequest" in self.objectIds():
			request = self.SQLRequest
		else:
			request = getattr(self,self._SQLRequestName)
		if self.isSQLSecure(request.document_src()):
			return request
		
	def executeModifRequest(self,**kwargs):
		""" executes the modification request """
		return self.getSQLModifRequest()(**kwargs)
			
	def getSQLModifRequest(self,**kwargs):
		""" gets the SQL Modif Request associated to this form (works for each form type) """
		if "SQLRequest" in self.objectIds():
			request = self.SQLRequest
		else:
			request = getattr(self,self._SQLRequestName)
		if self.isSQLSecure(request.document_src()):
			return request
		

	security.declarePublic('isSQLSecure')
	def isSQLSecure(self,requestText):
		""" returns true if SQL is 'secure'
		 BUT ITS ONLY ERGONOMY : ONLY SECURING WITH CONNECTION STRING IS SECURE """
		template = requestText.lower()
		for badword in self._forbiddenWords:
			if badword.lower() in template:
				return False
		return True
	
	security.declareProtected(addPermission,'getSQLRequest')
	def customizeSQLRequest(self,REQUEST=None):
		""" action : copy the sql request into the forms manager and make it editable by user """
		if not("SQLRequest" in self.objectIds()):
			defaultSQL = getattr(self,self._SQLRequestName)
			template = defaultSQL.document_src().replace("<params></params>","")
			self.manage_addProduct['ZSQLMethods'].manage_addZSQLMethod("SQLRequest",self._formType+" Request",connection_id="connection",arguments="",template=template)
			
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=SQLRequest&portal_status_message=custom SQL Request has been added")

		
	security.declareProtected(addPermission,'setSQLRequest')
	def setCustomized_SQLRequest(self,SQLRequestText):
		""" sets the sqlrequest from form """
		SQLRequestText = SQLRequestText.replace("<params></params>","")
		if self.isSQLSecure(SQLRequestText):
			self.SQLRequest.manage_edit(template=SQLRequestText,title=self.SQLRequest.title,arguments='',connection_id="connection", dtpref_cols='', dtpref_rows='')
			return "SQL Request has been saved"
			pass
		else:
			raise "Forbidden Request"

	security.declareProtected(View,"getZSQLTypeOfField")
	def getZSQLTypeOfField(self,field):
		""" gets the ZSQL type working with field """
		if type(field) == type(""):
			field = getattr(self.references,self.tableName).get_field(field) # if string, gets the reference field of that name
		return self._FormType2ZSQLType[field.meta_type]
		
	# ##################### scripts management ###################
	
	# customize
	security.declareProtected(addPermission,"customizePost_script")
	def customizePost_script(self,REQUEST=None):
		""" action : copy the post_script into the forms manager and make it editable by user """
		message = self._customizeScript("post_script",params="request,results")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=post_script&"+message)
	
	security.declareProtected(addPermission,"customizePre_script")
	def customizePre_script(self,REQUEST=None):
		""" action : copy the pre_script into the forms manager and make it editable by user """
		message = self._customizeScript("pre_script",params="")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=pre_script&"+message)
	
	security.declareProtected(addPermission,"_customizeScript")
	def _customizeScript(self,scriptName,params=""):
		message=""
		if not(scriptName in self.objectIds()): # if no scriptname script in current form manager
			defaultscript = getattr(self,scriptName) # gets the first script acquired
			scriptBody = defaultscript.body()
			script = PythonScript(scriptName)
			script.ZPythonScript_edit(params=params,body=scriptBody)
			script.write(scriptBody)
			self._setObject(scriptName,script)
			message+="portal_status_message=custom "+scriptName+" has been added"+scriptBody
			
		return message
		
	# edit custom
	security.declareProtected(addPermission,"setCustomized_pre_script")
	def setCustomized_pre_script(self,customizedBody):
		return self._setCustomizedScript(name="pre_script",params="",body=customizedBody)
		
	security.declareProtected(addPermission,"setCustomized_post_script")
	def setCustomized_post_script(self,customizedBody):
		return self._setCustomizedScript(name="post_script",params="request,results",body=customizedBody)
		
	def _setCustomizedScript(self,name=None,params=None,body=None):
		script = getattr(self,name) # gets the first script acquired
		body=str(body).replace("\r","")
		script.write(body)
		
		return "custom "+name+" has been saved"
		
	# ####################### Templates management
	
	def customizeForm_body(self,REQUEST=None):
		""" action : copy the post_script into the forms manager and make it editable by user """
		message = self._customizeTemplate("form_body")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=form_body&"+message)
		
	def customizeEntry_body(self,REQUEST=None):
		""" action : copy the post_script into the forms manager and make it editable by user """
		message = self._customizeTemplate("entry_body")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=entry_body&"+message)
		
	def customizeResults_body(self,REQUEST=None):
		""" action : copy the post_script into the forms manager and make it editable by user """
		message = self._customizeTemplate("results_body")
		REQUEST.response.redirect(self.absolute_url()+"/customize_form?customize=results_body&"+message)
	
	security.declareProtected(addPermission,"_customizeScript")
	def _customizeTemplate(self,name):
		message=""
		if not(name in self.objectIds()): # if no scriptname script in current form manager
			defaultTemplate = getattr(self,name) # gets the first script acquired
			defaultBody = defaultTemplate.document_src()
			template = DTMLMethod(name)
			template.manage_edit(data=defaultBody,title=name)
			self._setObject(name,template)
			message+="portal_status_message=custom "+name+" has been added"
			
		return message
		
	def setCustomized_entry_body(self,customizedBody):
		return self._setCustomizedTemplate(name="entry_body",params="",body=customizedBody)
		
	def setCustomize_results_body(self,customizedBody):
		return self._setCustomizedTemplate(name="results_body",params="",body=customizedBody)
	 
	def setCustomized_form_body(self,customizedBody):
		return self._setCustomizedTemplate(name="form_body",params="",body=customizedBody)

	def _setCustomizedTemplate(self,name=None,params=None,body=None):
		template = getattr(self,name) # gets the first script acquired
		body=str(body).replace("\r","")
		template.manage_edit(data=body,title=name)
		return "custom "+self.labelFromId(name)+" has been saved"		
		
		
	# #######################################################################	
	# ############### REQUEST FIELDS AND FORM CREATION ######################
	
	security.declareProtected(addPermission,'setRequestFields')
	def setRequestFields(self,requestFields):
		""" sets the request fields : copy the new fields from reference, 
		 and delete the unselected ones """
		
		
		
		# deleting unselected fields
		form = self.form
		for field in form.get_fields():
			if not(field.id in requestFields):
				form.manage_delObjects([field.id])
		
		# evite un bug incomprehensible : un tuple vide se met dans requestFields
		self.requestFields = tuple([requestField for requestField in requestFields if requestField])
			
		if requestFields:
			self._copyReferenceFields()
		
	
		
	security.declareProtected(addPermission,'_copyReferenceFields')
	def _copyReferenceFields(self):
		""" copy reference fields into the form. old ones are not replaced """
		referenceForm = getattr(self.references,self.getTableName()) # CHANGER CA !!! utiliser les ATreferences
		
		form = self.form
		
		for fieldName in self.requestFields:
			
			if not(same_type(fieldName,"")):
				fieldName = fieldName.getId() # pas tres clean
			
			if not(hasattr(form,fieldName)):
				# adds lacking fields in form
				referenceField = getattr(referenceForm,fieldName)
				form.manage_clone(referenceField,fieldName)
				self._initializeRequestField(getattr(form,fieldName),referenceField)

	
	security.declareProtected(addPermission,'_initializeRequestField')
	def _initializeRequestField(self,field,referenceField):
		""" DEPENDS ON FORM TYPE. initialize field properties with help of referenceField 
		SEARCH FORM VERSION
		"""
		valuesDict = referenceField.values
		
		# differences between reference version and search form version
		valuesDict['required']=False
		if valuesDict['external_validator'] == "verifyUnicityConstraint":
			valuesDict['external_validator']=None
			
		field.initialize_values(valuesDict)
		
		pass
	
	def fieldIdsList(self,form=None):
		""" returns list of this form's fields """
		if not form: form=self.form
		return [field.getId() for field in form.get_fields()]
	
	def getReferenceTable(self):
		return getattr(self.references,self.tableName)
	
	def getReferenceFieldsList(self):
		if not(self.tableName):
			return []
		if not(getattr(self.references,self.tableName)):
			return []
		else:
			return getattr(self.references,self.tableName).objectIds()
			
				
	# ######################## VOCABULARIES ##########################

	security.declareProtected(addPermission,'setRequestFields')
	def _get_tableName_vocabulary(self):
		""" get the display list of names of tables managed by the forms manager 
		and which form managing is possible """
		manager = self.getFormsManager()
		
		tables = tuple()
		
		if not(manager):
			return DisplayList(tables)
		
		for table in manager.getReferenceTablesList():
			
			try:
				manager.getDBTablesFieldsList(table)
				# get tables which read is authorized by connection string
				tables += ((table,self.labelFromId(table)),)
				
			except psycopg2.ProgrammingError:
				print self.connection_info+" doesn't give access to "+table+" table"
				pass
					
		return DisplayList(tables)
	
		
	security.declareProtected(addPermission,'_get_field_list_vocabulary')
	def _get_field_list_vocabulary(self,tableName=""):
		""" gets the display list of the fields of the related table """
		if not tableName:
			tableName = self.getTableName()
			
				
		fieldsList = tuple()
		
		if not(tableName):
			return DisplayList(fieldsList)
		
		table = getattr(self.references,tableName)
		
		for field in getattr(self.references,tableName).objectItems():
			
			idField = field[0]
			titleField = getattr(table, idField).title()
			if not(titleField):
				titleField = idField
				
			# get tables which read is authorized by connection string
			fieldsList += ((idField,str(titleField)),)
			
			pass
					
		return DisplayList(fieldsList)
	
		
	security.declareProtected(addPermission,'_get_useForm_roles_vocabulary')
	def _get_useForm_roles_vocabulary(self,tableName=""):
		""" gets the possible roles for using (submitting) this form """
		if not tableName:
			tableName = self.getTableName()
		
		rolesList = tuple()
		
		if not(tableName):
			return DisplayList(rolesList)
		
		for role in getattr(getattr(self.references,tableName),"use"+self._formRightsType):

			# get tables which read is authorized by connection string
			rolesList += ((role,role),)
			
			pass

		return DisplayList(rolesList)
	
	security.declareProtected(addPermission,'getFormsManager')
	def getFormsManager(self):
		""" gets the form manager A AMELIORER !!! """
		return self.aq_parent
	
registerType(PloneDbFormManager)
