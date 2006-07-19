from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.public import Schema, registerType
from Products.Archetypes.public import StringField, LinesField, ReferenceField
from Products.Archetypes.public import MultiSelectionWidget, BooleanWidget, SelectionWidget
from Products.Archetypes.public import ReferenceWidget

from Products.Formulator.Form import ZMIForm

from permissions import *
from PloneDbFormManager import PloneDbFormManager, PloneDbFormManagerSchema


factory_type_information = (
	{ 'id':'DbAddFormManager',
	'meta_type':'DbAddFormManager',
	'description':'An interaction form to the database',
	'title':'Database Add Form',
	'content_icon':'formmanager.gif',
	'product':'PloneDbFormulator',
	'factory':'addDbAddFormManager',
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
			'permissions':(UseModifForm,)},
		{'id':'edit',
			'name':'Edit Form Properties',
			'visible':1,
			'action':'edit',
			'permissions':(CreateModifForm,)},
			
			
		{'id':'customizeSQLRequest',
			'name':'customize request',
			'action':'customizeSQLRequest',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
		
		{'id':'customizePre_script',
			'name':'customize pre script',
			'action':'customizePre_script',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
			
		{'id':'customizePost_script',
			'name':'customize post script',
			'action':'customizePost_script',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
			
		{'id':'customizeForm_body',
			'name':'customize form',
			'action':'customizeForm_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
			
		{'id':'customizeResults_body',
			'name':'customize results list',
			'action':'customizeResults_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
			
		{'id':'customizeEntry_body',
			'name':'customize entry',
			'action':'customizeEntry_body',
			'visible':1,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
			
		{'id':'customize_form',
			'name':'customize_form',
			'action':'customize_form',
			'visible':0,
			'permissions':(CreateModifForm,)},
			
		{'id':'setCustomized',
			'name':'setCustomized',
			'action':'setCustomized',
			'visible':0,
			'category':'object_buttons',
			'permissions':(CreateModifForm,)},
		
		{'id':'setDefault',
			'name':'set default',
			'action':'setDefault',
			'visible':0,
			'permissions':(CreateModifForm,)},
			
		
			
		),
			
		
	'aliases':({
		'view'	: 'view_form',
		'edit'	: 'base_edit',
		'sharing' : 'sharing',
		'properties':'base_metadata'
		}),

	},
)	


	
def addDbAddFormManager(self,id,REQUEST=None,**kwargs):
	""" adds an add form manager """
	""" for the moment, can only create it in a PloneDbFormsManager """
	
	object = DbAddFormManager(id,**kwargs)
	self._setObject(id, object)
	form = ZMIForm("form", "form", unicode_mode=True)
	object._setObject("form",form)
	

class DbAddFormManager(PloneDbFormManager):


			
	# ###############################################################
	#      FORM TYPE (add/search/update...) RELATED INFORMATION     #
	#                        -- SEARCH FORM --                      #
	# ###############################################################
	
	_forbiddenWords = ['update','create','database','delete']
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
	
	_formType = "addForm" # id name of type let's create subclasses for other form types
	_formRightsType = "ModifForm" # only SearchForm or ModifForm
	_formMessage = "Add" # add, update, search...
	_SQLRequestName = "addFormZSQL" # name of the request

	addPermission = CreateModifForm
	usePermission = UseModifForm
	
	archetype_name = "Database Add Form"
	
	security = ClassSecurityInfo()
	

	formTypeSchema = Schema((
	LinesField('requestFields',
		vocabulary="_get_field_list_vocabulary",
		mode="",
		description = "Database Fields used by SQL request",
		widget = MultiSelectionWidget(visible={'edit':'invisible','view':'invisible'})
		),
	LinesField('resultFields',
		vocabulary="_get_field_list_vocabulary",
		mode="",
		widget = MultiSelectionWidget(visible={'edit':'invisible','view':'invisible'})
		),
	))	

	
	schema = ATFolder.schema.copy()+ PloneDbFormManagerSchema + formTypeSchema
	security = ClassSecurityInfo()
	_at_rename_after_creation = True
	
	# #################### ADD FORM CREATION
	
	# add form is created at table name choice
	
	def setTableName(self,tableName):
		self.tableName=tableName
		self.resultFields = self.requestFields = self.getReferenceFieldsList() # add form needs all fields
		self._copyReferenceFields() 
		
	security.declareProtected(addPermission,'_initializeRequestField')
	def _initializeRequestField(self,field,referenceField):
		""" DEPENDS ON FORM TYPE. initialize a field properties from referenceField properties
		ADD FORM VERSION : no modification
		"""
		valuesDict = referenceField.values
		field.initialize_values(valuesDict)
		
		pass
			
	#def setRequestFields(self,requestFields):
	#	self.requestFields = self.references.objectIds()
		
registerType(DbAddFormManager)
