def verifyUnicityConstraint(self,REQUEST=None,new_userValue=""):

	def method_name():
		return "verifyUnicityConstraint"
	
	def __of__(object):
		return verifyUnicityConstraint
	
	fieldId = self.getId()
	if REQUEST:
		userValue = REQUEST["field_"+fieldId]
	else:
		# TEST
		userValue = new_userValue
	if hasattr(self,'tableName'):
		tableName = self.tableName
	else:
		tableName = self.aq_parent.getId()
	
	print "VERIFYUNICITYCONSTRAINT TABLENAME :"+str(tableName)
	
	
	#fieldId = "NUMERO"
	#userValue = 1
	print "verifyUnicityConstraint"+fieldId+str(userValue)+tableName
	sameIdEntriesList = self.idSearch(tableName=tableName,fieldId=fieldId,userValue=userValue)
	
	for entry in sameIdEntriesList:
		return False
	
	return True
