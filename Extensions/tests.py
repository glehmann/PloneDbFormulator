from Products.CMFCore.CMFCorePermissions import setDefaultRoles


def addPermission(name):
	#self.manage_addPermission("totoid","toto titre","totoPermission")
	setDefaultRoles(name, ('Manager', 'Owner',))
	
	