""" interface de PloneDbFormsManager """

from Products.ATContentTypes.content.folder import ATFolder
from Interface import Base

class IPloneDbFormsManager(Base): # 
	""" PloneDbFormsManager interface 
	
		*************************************
		String DBMSName : name of DBMS managed by this class
		*************************************
	"""
	
	
	def getDBMSName(self):
		""" get name of DBMS managed by this class (set at __init__) 
		returns string """
		pass
	
	
	# ########## CREATING AND MANAGING THE CONNECTION ###########
	
	def addConnection(self,connection_info):
		""" adds a connection object to the relational database
		connection_info depends of DBMS
		
		"""
		pass
	
	def majConnection(self,connection_info):
		""" changes the connection_info of the connection """
		pass
	
	def setConnectionInfo(self,connection_info):
		""" sets the connection_info value of the connection 
		except if connection string is bad (returns false, no border effects) """
	
	
	# ######## DATABASE INFORMATIONS
	
	def getDBTablesList(self):
		""" get the list of database tables from which forms may be built 
		returns strings list """
		pass	
	
	def getDBTablesFieldsList(self,tableName):
		""" returns the list of fields names of the table tableName > [str] """
		pass
	
	def getDBStructure(self):
		""" returns a representation of database structure

structure :

    {<tableName_str>:
        [{<fieldName_str>:
             {'primary_key':<boolean>,'width':<integer>,'null':<boolean>,'foreign_key':(<table_str>,<field_str>),'type':<str>,'auto_num':<bool>,'unique':<bool>}
         },
     ...],
 ...}
"""
	def idSearch(self,tableName="",fieldId="",userValue=""):
		""" returns the entry of table tableName where primary key fieldId == value userValue """
		pass
	
	# ############# REFERENCE FORMS AND FIELDS PRODUCTION
	
	def getFormTypesOfDBType(self,dbFieldType=""):
		""" returns a list of formulator form types  compatible with a dbfield type [str]
		(or all the correspondance dictionnary) {str:[str]}"""
		pass
	
	def setupTableProperties(self,REQUEST=None):
		""" creates the reference form of a table """
		pass
		
	# ################### INTERACTION FORM (PloneDbFormManager) PRODUCTION
	
	def addPloneDbFormManager(self):
		""" creates an Interaction Form Based on this Forms Manager
			(using its connection and its settings - field form, table rights) """
		pass
		
	
	
	
	'''
	def initializeDbFormsManager(self,):
		""" setup tables and creates reference forms """
		pass
	
	'''	
	'''
	def editTableFieldsProperties(self,tableName,):
		""" change fields properties of table """
		pass
	'''
	