""" interface de PloneDbFormsManager """

from Products.ATContentTypes.content.folder import ATFolder
from Interface import Base

class IPloneDbFormManager(Base): # 
	""" PloneDbFormManager interface 
	
	self.form : the request Formulator form, containing the request fields
	self.SQLRequest : the ZSQL request, which arguments corresponds to the request form fields
	
	"""
	
	def setRequestFields(self,requestFields):
		""" creates the request fields in form, copying the reference fields in requestFields list """
		pass
	
	pass