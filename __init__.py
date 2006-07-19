import sys

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, ManagePortal
from Products.CMFCore import utils
from Products.Archetypes.public import process_types, listTypes

from config import *
from permissions import *

from interfaces.PloneDbFormsManager import IPloneDbFormsManager
import PloneDbFormsManager
import PloneDbFormManager
import DbAddFormManager


#from Products.CMFCore import utils

this_module = sys.modules[__name__]

product_globals=globals()

# make the skins available as DirectoryViews
registerDirectory('skins',globals())
registerDirectory('skins/PloneDbFormulator',globals())
registerDirectory('SQLRequests',globals())


contentConstructors = (PloneDbFormsManager.addPloneDbFormsManager,)
contentClasses = (PloneDbFormsManager.PloneDbFormsManager,)

def initialize(context):


	'''
	utils.ContentInit("PloneDbFormsManager",
			content_types = contentClasses,
			permission = ManagePortal,
			extra_constructors = contentConstructors,
			fti = PloneDbFormsManager.factory_type_information).initialize(context)
	'''
	## archetypes initialization
	
	content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),PROJECTNAME)

	utils.ContentInit(
		"PloneDbFormulator Content",
		content_types = content_types,
		permission = ManagePortal,
		extra_constructors = constructors,
		fti = ftis,).initialize(context)	

	
        context.registerClass(
            meta_type = PloneDbFormManager.PloneDbFormManager.archetype_name,
            constructors = (PloneDbFormManager.addPloneDbFormManager,),
            permission = PloneDbFormManager.PloneDbFormManager.addPermission,
            )
	    
        context.registerClass(
            meta_type = DbAddFormManager.DbAddFormManager.archetype_name,
            constructors = (DbAddFormManager.addDbAddFormManager,),
            permission = DbAddFormManager.DbAddFormManager.addPermission,
            )
		
	pass