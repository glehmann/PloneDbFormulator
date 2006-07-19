from StringIO import StringIO
import string

from Products.Formulator import Form, Field, StandardFields
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent,ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.CMFCore.TypesTool import ContentFactoryMetadata
from Products.CMFCore.Expression import Expression

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.PloneDbFormulator import product_globals, PloneDbFormsManager 
from Products.PloneDbFormulator.PloneDbFormsManager import factory_type_information
from Products.PloneDbFormulator.config import *

def install(self):
	"""Register skin layer with skin tool, and other setup in the future """
	
	out = StringIO() # setup stream for status messages
	
	out.write(install_archetypes_types(self))
	
	out.write(install_archetypes_skins(self))
	
	cssreg = getToolByName(self, 'portal_css', None)
	
        if cssreg is not None:
            stylesheet_ids = cssreg.getResourceIds()
            # Failsafe: first make sure the two stylesheets exist in the list
            if 'plonedbformulator.css' not in stylesheet_ids:
                cssreg.registerStylesheet('plonedbformulator.css')
	
	return out.getvalue()

def install_archetypes_skins(self):
	out = StringIO()
	install_subskin(self,out,GLOBALS)
	return out.getvalue()

def install_archetypes_types(self):
	# Install Archetypes types
	out = StringIO()
	installTypes(self,out,listTypes(PROJECTNAME),PROJECTNAME)
	return out.getvalue()	

def uninstall(self):
	out = StringIO()
	
	return out.getvalue()