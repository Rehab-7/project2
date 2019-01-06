from flask import Flask, render_template ,request ,redirect , url_for , flash , jsonify
from flask import session as login_session
from sqlalchemy import create_engine , desc
from sqlalchemy.orm import sessionmaker
from database_serise import Base, Series, CatalogItem , User
import random
import string
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
from flask import make_response
import requests

app = Flask(__name__ , template_folder='template')
#load googel sgin-in API Client-id
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Series Catalog Application"

engine = create_engine('sqlite:///seriescatalogwithuseress.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    # User Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
       # del login_session['access_token']
        #del login_session['gplus_id']
        #del login_session['username']
        #del login_session['email']
        #del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


    # JSON APIs to view Serieses Information
@app.route('/series/<int:series_id>/catalog/JSON')
def seriesCatalogJSON(series_id):
    series = session.query(Series).filter_by(id=series_id).one()
    items = session.query(CatalogItem).filter_by(series_id=series_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])

@app.route('/series/<int:series_id>/catalog/<int:catalog_id>/JSON')
def catalogItemJSON(series_id, catalog_id):
    Catalog_Item = session.query(CatalogItem).filter_by(id=catalog_id).one()
    return jsonify(Catalog_Item=Catalog_Item.serialize)

@app.route('/series/JSON')
def seriesesJSON():
    serieses = session.query(Series).all()
    return jsonify(serieses=[r.serialize for r in serieses])

#show all serieses

@app.route('/')
@app.route('/series')
def showSerieses():
    serieses = session.query(Series).order_by(desc(Series.name))
    if 'username' not in login_session:
        return render_template('publicshowseries.html', serieses=serieses)
    else:
        return render_template('showSeries.html', serieses=serieses)


#create new series

@app.route('/series/new', methods=['GET', 'POST'])
def newSeries():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method =='POST':
        newSeries=Series(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newSeries)
        session.commit()
        flash("new series is created")
        return redirect(url_for('showSerieses'))
    else:
        return render_template('newSeries.html')

#show series catalog item

@app.route('/series/<int:series_id>/')
@app.route('/series/<int:series_id>/catalog/')
def showCatalogItem(series_id):
    series = session.query(Series).filter_by(id=series_id).one()
    creator = getUserInfo(series.user_id)
    items = session.query(CatalogItem).filter_by(series_id=series_id).all()
    if 'username' not in login_session :
        return render_template('publicshowcatalogitem.html', series=series, items=items, creator=creator )
    else:
        return render_template('showCatalogItem.html',series=series, items=items, creator=creator )


#create new catalog item

@app.route('/seriest/<int:series_id>/catalog/new/', methods=['GET', 'POST'])
def newCatalogItem(series_id):

    if 'username' not in login_session:
        return redirect('/login')
    series = session.query(Series).filter_by(id=series_id).one()
    if login_session['user_id'] != series.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add catalog items to this series. Please create your own series in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newItem = CatalogItem(name=request.form['name'],
                               description=request.form['description'],
                               rating=request.form['rating'],
                               seasons=request.form['seasons'],
                               series_id=series_id,
                               user_id=series.user_id)
        session.add(newItem)
        session.commit()
        flash('New Catalog Item Successfully Created')
        return redirect(url_for('showCatalogItem', series_id=series_id))
    else:
        return render_template('newCatalogItem.html', series_id=series_id)

#Edit catalog item

@app.route('/series/<int:series_id>/catalog/<int:catalog_id>/edit/', methods=['GET','POST'])
def editCatalogItem(series_id, catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    editeToItem = session.query(CatalogItem).filter_by(id = catalog_id).one()
    series = session.query(Series).filter_by(id=series_id).one()
    if login_session['user_id'] != series.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit catalog items to this series. Please create your own series in order to edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editeToItem.name = request.form['name']
        if request.form['description']:
            editeToItem.description = request.form['description']
        if request.form['rating']:
            editeToItem.rating = request.form['rating']
        if request.form['seasons']:
            editeToItem.seasons = request.form['seasons']
        session.add(editeToItem)
        session.commit()
        flash("catalog  edited successfully!")
        return redirect(url_for('showCatalogItem' , series_id=series_id ))
    else:
         return render_template('editCatalogItem.html', series_id=series_id, catalog_id=catalog_id ,item=editeToItem)

#Delete catalog item

@app.route('/series/<int:series_id>/catalog/<int:catalog_id>/delete/', methods=['GET','POST'])
def deleteCatalogItem(series_id, catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    series = session.query(Series).filter_by(id=series_id).one()
    itemToDelete = session.query(CatalogItem).filter_by(id=catalog_id).one()
    if login_session['user_id'] != series.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete catalog items to this series. Please create your own series in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("catalog deleted successfully!")
        return redirect(url_for('showCatalogItem', series_id=series_id))
    else:
        return render_template('deleteCatalogItem.html', item=itemToDelete)

#disconnect from the login session
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            # del login_session['gplus_id']
            # del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('showSerieses'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showSerieses'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000 )
