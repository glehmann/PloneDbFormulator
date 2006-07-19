## Script (Python) "pre script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=results,request

# ce script est lance apres l'execution de la requete
# object results : les resultats de la requete
# str request : le texte de la requete lancee
form = context.form # le formulaire
formValues = container.REQUEST.form # les valeurs entrees par l'utilisateur
# exemple : envoit un mail a tdesvena@jouy.inra.fr
corps = "Champs : "+str(formValues)+"\n\n"
corps += "Request : "+str(request[0])+"\n\n"
for result in results:
   corps = corps + str(result) + "\n"
   for r in result:
      corps += str(r)
message = """
From: thomas.desvenain@gmail.com
To: tdesvena@jouy.inra.fr
Bcc: 
Subject: [PloneDbFormulator] Un formulaire a été complété

"""+corps+"""

URL: """+context.absolute_url()+"""

"""
context.MailHost.send(message)

return ""