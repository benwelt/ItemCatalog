#!usr/bin/python
from dbsetup import Base, User, Category, Bike
from flask import Flask, jsonify, make_response, request, url_for, abort, g
from flask import render_template, redirect, flash
from flask import session as login_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import json
import requests
import httplib2
import random
import string


engine = create_engine('sqlite:///bikecatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open(
        'client_secrets.json', 'r').read())['web']['client_id']


def newState():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return state


@app.route('/glogin', methods=['POST'])
def glogin():

    # Validate state token
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
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print "Abort"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash('You have been logged in as ' + login_session['username'])
    return jsonify(name=login_session['username'])


@app.route('/logout')
def logout():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You have been logged out')
        return redirect(url_for('showAllBikes'))
    else:
        response = make_response(
                    json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash('Logout failed')
        return redirect(url_for('showAllBikes'))


# Main page
@app.route('/')
@app.route('/main')
def showAllBikes():
    state = newState()
    categories = session.query(Category).all()
    bikes = session.query(Bike).all()
    return render_template('main.html', categories=categories, bikes=bikes,
                           login_session=login_session, state=state)


# Items within a selected category
@app.route('/category/<string:category_name>/')
@app.route('/category/<string:category_name>/bikes')
def showCategoryBikes(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).first()
    bikes = session.query(Bike).filter_by(category=category).all()
    return render_template('categorybikes.html', bikes=bikes,
                           category=category,
                           categories=categories,
                           login_session=login_session)


# Items within a selected brand
@app.route('/brand/<string:brand_name>/')
@app.route('/brand/<string:brand_name>/bikes')
def showBrandBikes(brand_name):
    categories = session.query(Category).all()
    bikes = session.query(Bike).filter_by(brand=brand_name).all()
    return render_template('brandbikes.html',
                           bikes=bikes,
                           brand=brand_name,
                           categories=categories,
                           login_session=login_session)


# Show details for specific bikes
@app.route('/bike/<string:bike_name>/')
@app.route('/bike/<string:bike_name>/details')
def showBikeDetails(bike_name):
    categories = session.query(Category).all()
    bike = session.query(Bike).filter_by(name=bike_name).one()
    return render_template('bikedetails.html',
                           bike=bike,
                           categories=categories,
                           login_session=login_session)


# Add a new category
@app.route('/category/new', methods=['GET', 'POST'])
def addNewCategory():
    categories = session.query(Category).all()
    if 'provider' in login_session and login_session['provider'] != 'null':
        if request.method == 'POST':
            newCategory = Category(name=request.form['name'])
            session.add(newCategory)
            session.commit()
            flash('New category successfuly added')
            return redirect(url_for('showAllBikes'))
        else:
            return render_template('newcategory.html',
                                   categories=categories,
                                   login_session=login_session)
    else:
        flash('Please login to add a new category')
        return redirect(url_for('showAllBikes'))


# Add a new item
@app.route('/bike/new', methods=['GET', 'POST'])
def addNewBike():
    categories = session.query(Category).all()
    # Check for logged in user
    if 'provider' in login_session and login_session['provider'] != 'null':
        if request.method == 'POST':
            newBike = Bike(name=request.form['name'],
                           brand=request.form['brand'],
                           category_id=request.form['category'],
                           imageUrl=request.form['bikeImageUrl'],
                           description=request.form['description'])
            session.add(newBike)
            session.commit()
            flash('New bike successfully added')
            return redirect(url_for('showAllBikes'))
        else:
            return render_template('newbike.html',
                                   categories=categories,
                                   login_session=login_session)
    else:
        flash('Please login to add a new bike')
        return redirect(url_for('showAllBikes'))


# Edit an existing item
@app.route('/<string:brand_name>/<string:bike_name>/edit',
           methods=['GET', 'POST'])
def editBike(brand_name, bike_name):
    categories = session.query(Category).all()
    bike = session.query(Bike).filter_by(name=bike_name).one()
    # Check for logged in user
    if 'provider' in login_session and login_session['provider'] != 'null':
        if request.method == 'POST':
            bike.name = request.form['name']
            bike.brand = request.form['brand']
            bike.category_id = request.form['category']
            bike.imageUrl = request.form['bikeImageUrl']
            bike.description = request.form['description']
            session.add(bike)
            session.commit()
            flash('Bike successfully edited')
            return redirect(url_for('showAllBikes'))
        else:
            return render_template('editbike.html', brand=brand_name,
                                   bike=bike, categories=categories,
                                   login_session=login_session)
    else:
        flash('Please login to edit a bike')
        return redirect(url_for('showAllBikes'))


# Delete an existing bike
@app.route('/<string:brand_name>/<string:bike_name>/delete',
           methods=['GET', 'POST'])
def deleteBike(brand_name, bike_name):
    categories = session.query(Category).all()
    bike = session.query(Bike).filter_by(name=bike_name).one()
    # Check for logged in user
    if 'provider' in login_session and login_session['provider'] != 'null':
        if request.method == 'POST':
            session.delete(bike)
            session.commit()
            flash('Bike successfully deleted')
            return redirect(url_for('showAllBikes'))
        else:
            return render_template('deletebike.html',
                                   bike=bike,
                                   brand=brand_name,
                                   categories=categories,
                                   login_session=login_session)
    else:
        flash('Please login to delete a bike')
        return redirect(url_for('showAllBikes'))


# Custom 404 page
@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html')


def createUser(login_session):
    newUser = User(
                username=login_session['username'],
                email=login_session['email'],
                picture=login_session['picture']
                )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Endpoints
@app.route('/category/json')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/bike/json')
def bikeJSON():
    bikes = session.query(Bike).all()
    return jsonify(bikes=[b.serialize for b in bikes])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'secret_key'
    app.run(host='0.0.0.0', port=8000)
