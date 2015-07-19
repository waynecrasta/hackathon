import cherrypy
import os, os.path
from database import *
from search_by_radius import RestaurantSearch

class MainView(object):

    @cherrypy.expose
    def index(self):
        yield 'Create new poll<br><br>'
        yield 'Search for and add new restaurants<br>'
        yield 'View or delete existing restaurants<br>'
        """yield 'View or delete favorites<br>'
        yield 'View or delete blacklisted restaurants<br>'"""

    @cherrypy.expose
    def restaurants(self):
        restaurants = session.query(Restaurant)
        for rest in restaurants:
            yield rest.name
            yield '<br>'
        yield ''

    @cherrypy.expose
    def createpoll(self):
        yield ''

    @cherrypy.expose
    def blacklist(self):
        yield ''

    @cherrypy.expose
    def favorites(self):
        yield ''


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
    cherrypy.quickstart(MainView(), '/', conf)