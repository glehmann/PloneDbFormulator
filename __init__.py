import sys

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import utils
from setup import BDRSitePolicy

this_module = sys.modules[__name__]

product_globals=globals()

# make the skins available as DirectoryViews
registerDirectory('skins',globals())
registerDirectory('skins/PloneDBFormulator',globals())

def initialize(context):
	BDRSitePolicy.register(context,product_globals)
	pass
