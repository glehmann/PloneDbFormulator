## Script (Python) "submitButton"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=message=""

# <!-- a faire : le bouton de soumission ne s'affiche que si le formulaire est activé -->
if not(message):
	message = context.getFormMessage()
	
return '<input type="submit" value="'+message+'" />'
