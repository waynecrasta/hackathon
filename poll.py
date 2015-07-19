import cherrypy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_declarative import Restaurant, User

Base = declarative_base()

user = 'texas'
password = 'texas'
database_host = 'hacksql.viasat.io'
engine = create_engine(
    'mysql+mysqlconnector://{}:{}@{}/texas'.format(user, password, database_host))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
metadata = MetaData()
import cherrypy
import os, os.path
import random
import string

class Poll(object):
    @cherrypy.expose
    def index(self):
        yield '''<html>
        <head>
            <link href="/static/css/style.css" rel="stylesheet">
          </head>
        '''
        yield '''<p>YOU HAVE BEEN INVITED TO LUNCH! </br>Enter Username and an Option</p></br>'''
        yield '''
        <form action="poll">
        Username: <input type="text" name="uname"></br>'''
        yield '''<label for="optout">
                <input type="radio" name="opt" value="1"/>I Don't Want To Go.
             </label></br>'''
        yield '''<label for="optout">
                <input type="radio" name="opt" value="2"/>I Want to Go but Don't Want to Vote.
             </label></br>'''
        yield '''<label for="optout">
                <input type="radio" name="opt" value="3"/>Take me to Submit My Vote!
             </label></br>'''
        yield '''<button type="submit">Login</button></form></html>'''

        
    @cherrypy.expose
    def poll(self, uname, opt):
        match = 0
        for row in session.query(User):
            if uname == row.username:
                match = 1
        if match == 0:
            yield '''USERNAME NOT RECOGNIZED'''
            opt = "0"
            yield '</br> <a href = "/">Return To Login</a>'
            
        if opt == "3":
            yield '''
            <form action="search">
            ZipCode: <input type="text" name="zip">
            <select name="radius">
                  <option value="5">5 miles</option>
                  <option value="10">10 miles</option>
                  <option value="20">20 miles</option>
            </select>

            <button type="submit">Search</button>
            </form>
            '''
        elif opt=="2":
            yield '''don't vote'''


        elif opt=="1":
            objects = session.query(User)
            objects = objects.filter(User.username == uname)
            for o in objects:
                session.delete(o)
            yield '{} has been removed from the list'.format(uname)
            session.commit()
            

    @cherrypy.expose
    def search(self, zip, radius):
        yield'''
            <legend>What is your Restaurant of choice?</legend>
            
            <form action="results">'''
        for row in session.query(Restaurant):
            
            yield'''<label for="restId">
                <input type="radio" name="restId" value="%s" id="Poll_0" />
                %s
             </label></br>'''%(str(row.id),row.name)
        yield '''<button type="submit">Vote</button>'''
        
        
        
    @cherrypy.expose
    def results(self,restId):
        objects = session.query(Restaurant)
        objects = objects.filter(Restaurant.id == int(restId))
        for o in objects:
            o.votes = o.votes + 1
        for row in session.query(Restaurant):
            yield '''<body>%s    %s      %s        %s     </body></br>
            ''' %(row.name, row.address, row.category, str(row.votes))


if __name__ == '__main__':
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
    cherrypy.quickstart(Poll(), '/', conf)




