
				


Summary: 

This project uses a html, Flask, sqlalchemy and SQLlite to run  a "data driven web application".






Folder Contents:

* Static = HTML style sheet and images used to add  style to the application
* templates= web pages used to carry out the crud operations
* client_secrets.JSON = Oauth file for basic user authentication.
* Database_setup.py = Using SQLAlchemy to setup and configure th DB
* Lotsofmenus.py = Adding data to the database.
* Project.py = The application framework. 
* manifest.yml = deployment scirpt used by cloud foundry
* requirements.txt = imports helper software into your instance
* im not sure what the procfile does yet. however it does initiate the py program for me









-Prerequisites-




-DevBox
-SQLAlchemy - http://www.sqlalchemy.org/
-Flask- http://flask.pocoo.org/
-Sublime Text Editor- http://www.sublimetext.com/
-GIT terminal interface shell- https://help.github.com/articles/set-up-git/
-dicttoxml - https://github.com/quandyfactory/dicttoxml
- CSRF - http://webpy.org/cookbook/csrf
- http://docs.sqlalchemy.org/en/rel_0_9/orm/cascades.html

 
***** All imports and helper software must be placed in the requirements file******


Services- (these will have to be created and bound to the application)
Postgres db service
UAA service


-Application Setup-


1. Download the catalog folder and extract it to a folder within your dev box directory

2. Set up OAUTH2 for a new web app at https://console.developers.google.com . 

Note: Make sure you setup oauth for port 8000. Otherwise, you will need to change line 328 in project.py "app.run(host='0.0.0.0', port=8000)" to another port.

3.  Open the catalog folder and replace the client_secrets.JSON file with your own file from OAuth.

4. go to the templates templates folder and open login.html, with "sublime" text editor 
change  line #24 ( -data-clientid="491949169794-7qcq5os5dm4hgig61dc3uh8mjnra6io1.apps.googleusercontent.com") with the your information from Oauth
We are ready to run the application.



-Running the application-

1. cf push





------------JSON API-----------------------
http://localhost:8000/restaurants/JSON


-------------XML API------------------------

http://localhost:8000/restaurants/XML






Updates:
-Correct JSON API endpoint for all restaurants. http://localhost:8000/restaurants/JSON returns page
-Login Required Decorator created. 
-Saving an edited restaurant name now saves in the database. session.add( ) session.commit
-properly indented @property def serialize(self): JSON API request for http://restaurants/JSON retuns all restaurants.
-ON DELETE CASCADE all menu items related to a resaurant are deleted when the restaurant is deleted
-XML API request now return an XML page.



Updates- 
- fixed ON DELETE CASCADE implemented on the child tables (MenuItem) whe a parent (restaurant) restaurant is deleted so are the associated menu items.
- removed redundant code
- change the response's content-type to text/xml in order to deliver the XML endpoints (not complete)
- Added @login_required to the newRestaurant function
- Added @csrf exempt to gconnect in order to disable csrf protection fo 3rd party post 
- 
