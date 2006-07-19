## Script (Python) "pre script"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
# SCRIPT S'EXECUTANT AVANT LA RECHERCHE, affiche le retour en haut de la page
# Variables contextuelles utiles :
form = context.form                     # LE FORMULAIRE
formFieldsList = context.fieldIdsList() # LISTE DES IDENTIFIANTS DES CHAMPS DU FORMULAIRE
resultFields = context.resultFields     # LISTE DES CHAMPS DE LA TABLE QUE L'ON A CHOISI DE POUVOIR AFFICHER
REQUEST = container.REQUEST             # LA REQUETE
# VERIFIER LA VALEUR D'UNE REQUETE :
# ex. pour le champ toto
# valeurToto = REQUEST['toto']
# l'operateur est 'dbForm_op', le critere de tri est 'dbForm_order'
# MODIFIER LA VALEUR D'UN PARAMETRE D'UNE REQUETE
# REQUEST.set('toto','nouvelle valeur')
#REQUEST.set('dbForm_op','OR')
return ""