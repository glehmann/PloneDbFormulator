PloneDbFormulator README
* author : "Thomas Desvenain":mailto:thomas.desvenain@gmail.com
* product page : http://thomas.desvenain.fr/PloneDbFormulator

Notes

* Needs Formulator and Plone, and the Relational Database Connector product related to your DBMS (Z Gadfly Connector for example)

* Provides a PloneDbFormsManager object that is linked to a relational database,

* PloneDbFormsManager assists portal users to build (in itself) interaction forms to that database, and result processing, containing PloneFormManager objects
	* forms are managed as Plone Document, with a specific workflow

* PloneDbFormManager objects are frameworks for interaction between a plone user and that database, managing :
	* semi-automated form creation
	* form validation (type, unicity, width) and security, using formulator, under MVC model
	* automated creation of requests from form (monotable only) : for the moment, search forms and add forms 
		(future : option for deleting and editing an entry, linked to a search form)
	* simple organization for easy processing of request results and user form entries, with python scripts
	* dtml instructions system providing a very simple template language to display the form and the request results into Plone
	* security : form use and creation permissions are managed by administrator, activation and publishing are reviewed

* (future PloneDbResultPage object : manages as a Plone Document the statical or dynamical result of a request, fully customizable)
	
* Default page templates are provided, so that no knowledge is needed

* Forms, scripts and templates are fully customizable (using python and dtml), for advanced users