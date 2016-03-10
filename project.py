# Importing functions for crud operations
# imports the flask framework,SQLAlchemy ORM and oauth authentication
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash

# Import sqlalchemy and datbase 
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

from flask import session as login_session
from datetime import datetime, timedelta
import random
import urllib
import string


#Import csrf protection
from flaskext.csrf import csrf, csrf_exempt

# Import oauth authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import os
from flask import make_response
import requests

# dicttoxml for XML functions
from dicttoxml import dicttoxml


app = Flask(__name__)

from functools import wraps

# call the csrf function
csrf(app)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# function decorator to avoid code repetition for login

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showRestaurants'))
        return f(*args, **kwargs)
    return decorated_function


    


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
# return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Google authentication gconnect----Begin
# Since we receive POST requests from a third-party site, 
# @csrf_exempt will disable csrf protection
@app.route('/gconnect', methods=['POST'])
#@csrf_exempt
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

# Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

# Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    # Grab the current time and length of time for the access token to determine when it expires
    login_session['logintime'] = datetime.now()
    login_session['access_length'] = credentials.token_response["expires_in"]

    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # store user data in session for later retrieval
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Generate html for welcome message to display on successful login
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Google Connection authentication ----END


# DISCONNECT - Revoke a current user's token and reset their login_session

@app.route('/gdisconnect')
def gdisconnect():
    """
    Revoke a current user's Google oauth2 token and resets their login_session
    """
# Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# logout the user and reset session
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        return logoutCleanup()
    else:
        if (datetime.now() - login_session['logintime']) > timedelta(
                                            seconds=login_session[
                                                'access_length']):
            return logoutCleanup()
# For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Removes session information


def logoutCleanup():
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['logintime']
    del login_session['access_length']

    flash("You have been successfully disconnected.")
    return redirect(url_for('showRestaurants'))

#################################################
# JSON APIs to view Restaurant Information


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(
                               id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


# JSON endpoint for a single restaurant and item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


# Return JSON showing all restaurants


@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])


###############################################
# XML API Endpoint


@app.route('/restaurants/XML')
def restaurantsXML():
    restaurants = session.query(Restaurant).all()
    response = make_response(dicttoxml({'restaurants': [r.serialize for r in restaurants]}))
    return response, 200, {'Content-Type': 'text/css; charset=utf-8'}
    


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/XML')
def menuItemXML(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    response = make_response(dicttoxml(Menu_Item.serialize), 200)
    return response, 200, {'Content-Type': 'text/css; charset=utf-8'}



@app.route('/restaurant/<int:restaurant_id>/menu/XML')
def restaurantMenuXML(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(
                               id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    response = make_response(dicttoxml({'items': [i.serialize for i in items]}), 200)
    return response, 200, {'Content-Type': 'text/css; charset=utf-8'}



###########################################
# The Main page of the website.
# Show all the objects in the "Restaurant" table.


@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants=restaurants)



# Create a new restaurant in the database
# csrf prtotected form 

@app.route('/restaurant/new/', methods=['GET', 'POST'])
@login_required
def newRestaurant():
    if request.method == 'POST':

        newRestaurant = Restaurant(
            name=request.form['name'])
        session.add(newRestaurant)
        flash('New Restaurant %s Successfully Created' % newRestaurant.name)
        session.commit()
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


# Edit a restaurant name in the database
# csrf prtotected form 

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
            if request.form['name']:
                    editedRestaurant.name = request.form['name']
                    session.add(editedRestaurant)
                    session.commit()    
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html',
                               restaurant=editedRestaurant)


# Delete a restaurant from the database
# csrf prtotected form 

@app.route('/restaurant/<int:restaurant_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(
        Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        flash('Category Successfully Deleted %s' % restaurantToDelete.name)
        return redirect(
            url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template(
            'deleteRestaurant.html', restaurant=restaurantToDelete)


# Show all menu items associated with a specific Restuarant.


@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return render_template('menu.html', items=items,
                           restaurant=restaurant)


# "Post" or add a new menu item to the database
# csrf prtotected form 

@app.route('/restaurant/<int:restaurant_id>/menu/new/',
           methods=['GET', 'POST'])
@login_required
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(
                               id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           picture=request.form['picture'],
                           restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showRestaurants',
                                restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html',
                               restaurant_id=restaurant_id)


# Edit a menu item
# csrf prtotected form 

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['picture']:
            editedItem.picture = request.form['picture']
            session.add(editedItem)
        session.commit()
        flash(editedItem.name + " has been edited.")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               item=editedItem)


# Delete a menu item from the database
# csrf prtotected form 

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted %s' % itemToDelete.name)
        return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)







port = int(os.getenv("PORT", 8000))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
