import cherrypy
import requests
import json
import oauth2
import os
from database import *
from poll import Poll

# API_KEY = 'AIzaSyCY0yYTShIG54l8rUPNUOsl3Jm7NdWtXBQ'
API_HOST = 'http://api.yelp.com/v2/search/?'
CONSUMER_KEY = 'bH-ntL7Nv-iUC7mndRvujw'
CONSUMER_SECRET = 'B-Br6RdJJpyMZAwYAmoKPisv-Cw'
TOKEN = 'ugQuBYYmoJBNcnBDpVrVO2HiPpMyahmZ'
TOKEN_SECRET = 'ljnrQcblPl7yHbuQebRoqhvlRoI'

category_names = {'bbq':'Barbecue', 'pizza':'Pizza', 'burgers':'Burgers', 'cajun':'Cajun',
            'mexican':'Mexican','italian':'Italian', 'japanese':'Japanese'}


class RestaurantSearch(object):

    def  __init__(self):
        self.poll = Poll()

    @cherrypy.expose
    def index(self):
        yield '''<a href="http://localhost:5588/search_entry">
                Search for restaurants to add to the poll<a><br>'''
        yield '''<a href="http://localhost:5588/invite">
                Invite Members<a><br>'''
        yield '''<a href="http://localhost:5588/poll">
                Join current poll<a><br>'''
        yield '''<a href="http://localhost:5588/poll/results">
            View current poll results<a><br>'''


    @cherrypy.expose
    def search_entry(self):
        yield '''<html>
                <head>
                    <link href="/static/css/style.css" rel="stylesheet">
                </head>
                '''
        yield '''<body>
                <form action="search">
                <fieldset>
                <legend>Polling:</legend>
                Location:<br>
                <input type="text" name="location" value="Bryan, TX"> <br>
                Radius in Miles:<br>
                <input type="text" name="miles" value="5"> <br>
                Category:<br>'''
        for key in category_names:
            yield '<input type="radio" name="category" value="%s">%s<br>' % (key, category_names[key])
        yield '''<br><br>
                <input type="submit" value="Submit"></fieldset>
                </form></body>'''

    @cherrypy.expose
    def search(self, location='Bryan, TX', miles=5, category='bbq'):
        yield '''<html>
        <head>
            <link href="/static/css/style.css" rel="stylesheet">
          </head>
        '''
        # START USING YELP API

        meters = float(miles) * 1609.34
        consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        oauth_request = oauth2.Request(method="GET", url=API_HOST, parameters=None)

        oauth_request.update(
            {
                'oauth_nonce': oauth2.generate_nonce(),
                'oauth_timestamp': oauth2.generate_timestamp(),
                'oauth_token': TOKEN,
                'oauth_consumer_key': CONSUMER_KEY,
                'location': location,
                'category_filter': category,
                'radius_filter': meters
            }
        )
        token = oauth2.Token(TOKEN, TOKEN_SECRET)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        url = oauth_request.to_url()

        # END USING YELP API

        # # USING LOCAL RESULTS

        # if category == 'bbq':
        #     url = 'http://localhost:5588/results?category=barbecue'
        # elif category == 'pizza':
        #     url = 'http://localhost:5588/results?category=burgers'
        # elif category == 'burgers':
        #     url = 'http://localhost:5588/results?category=burgers'
            

        response = requests.get(url)
        restaurants = json.loads(response.text)['businesses']
        for restaurant in restaurants:
            name = restaurant['name']
            name = sanitize(name)

            if(session.query(Blacklist).get(name) is not None):
                continue

            yield '<div id=rest>'

            full_address = restaurant['location']['display_address']
            address = ""
            rating = restaurant['rating_img_url']
            yield'<div id=name>{}</div>'.format(name)

            yield '<div id=address>'
            for field in full_address:
                yield'{}<br>'.format(field)
                address += field + ' '
            yield '</div>'

            yield '<a href="http://localhost:5588/add?name={}&address={}&category={}">Add</a>'.format(name, address, category)

            yield '<br>'
            yield '<img src="{}"></img></br>'.format(rating)
            yield '<br>'

            yield '</div>'


    @cherrypy.expose
    def add(self, name, address, category):
        restaurantmatch = session.query(Restaurant).filter(Restaurant.name == name).first()
        if restaurantmatch is None:
            new_rest = Restaurant(name=name, address=address, category=category, votes=0)
            session.add(new_rest)
            session.commit()
            yield 'Restaurant Added'
        else:
            yield 'This restaurant is already in the poll'

    # @cherrypy.expose
    # def results(self, category):
    #     if category == 'burgers':
    #         with open('burgers.json') as data_file:
    #             data = json.loads(data_file.read())
    #         return json.dumps(data)
    #     elif category == 'barbecue':
    #         with open('barbecue.json') as data_file:
    #             data = json.loads(data_file.read())
    #         return json.dumps(data)
    #     elif category == 'pizza':
    #         with open('pizza.json') as data_file:
    #             data = json.loads(data_file.read())
    #         return json.dumps(data)

    @cherrypy.expose
    def invite(self):
        yield '<form action="invited">'
        for person in session.query(UserList):
            name = person.username
            yield '''   
             <input type="checkbox" name="person" value="%s">%s<br>
            ''' % (name, name)
            yield '<br>'
        yield 'Other:<br><input type ="field", name="new_person" value><br><br>'
        yield '<input type="submit" value="Submit">'
        yield '</form>'

    @cherrypy.expose
    def invited(self, **args):
        if 'new_person' in args:
            new_name = args['new_person']
            if(new_name != ""):
                if(session.query(UserList).get(new_name) is None):
                    new_person = UserList(username=new_name)
                    session.add(new_person)
                    session.commit
                if(session.query(User).get(new_name) is None):
                        new_user = User(username=new_name, voted=0)
                        session.add(new_user)
                        session.commit()
                yield new_name
                yield '<br>'


        if 'person' in args:
            names = args['person']
            if not isinstance(names, list):
                names = [names]
            for name in names:
                yield name
                if(session.query(User).get(name) is None):
                    new_user = User(username=name, voted=0)
                    session.add(new_user)
                    session.commit()
                yield '<br>'
            yield 'Invited'



def sanitize(s):
    s = s.replace("'","")
    s = s.replace("&","and")
    s = s.replace("?","")
    s = s.replace("%","")
    return s

conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './public'
    }
}
cherrypy.config.update({'server.socket_port': 5588})
cherrypy.quickstart(RestaurantSearch(), '/', conf)
