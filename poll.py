import cherrypy
import os
import os.path
from database import *


class Poll(object):

    def __init__(self):
        self.uname = ""
        self.voteCount = 0

    @cherrypy.expose
    def index(self):
        yield '''<html>
        <head>
            <link href="/static/css/style.css" rel="stylesheet">
          </head>
        '''
        yield '''<p>YOU HAVE BEEN INVITED TO LUNCH! </br>Enter Username and an Option</p></br>'''
        yield '''
        <form action="search">
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
        yield '''<label for="optout">
                <input type="radio" name="opt" value="4"/>Change My Vote
             </label></br>'''
        yield '''<button type="submit">Login</button></form>'''
        yield '<a href = http://localhost:5588/reset>Clear Out Votes and Voted</a></html>'

    #needed for colin's management
    @cherrypy.expose
    def poll(self, uname, opt):
        
        
        
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
        

    @cherrypy.expose
    def search(self, uname, opt):

        match = 0
        for row in session.query(User):
            if uname == row.username:
                match = 1
        if match == 0:
            yield '''USERNAME NOT RECOGNIZED'''
            opt = "0"
            yield '</br> <a href = "/">Return To Login</a>'
        if opt == "2":
            yield '''don't vote'''
            self.voteCount = self.voteCount + 1

        elif opt == "1":
            objects = session.query(User)
            objects = objects.filter(User.username == uname)
            yield '{} is not going'.format(uname)
        elif opt == "4":
            yield'''
                <legend>What is your Restaurant of choice?</legend>

                <form action="results">'''
            previouslySelected = session.query(User)
            previouslySelected = previouslySelected.filter(User.username == uname)
            for o in previouslySelected:
                prev = o.rest_id
            for row in session.query(Restaurant):
                if prev == row.id:
                    yield'''<label for="restId">
                    <input type="radio" name="restId" value="%s" id="Poll_0" checked="checked" />
                    %s
                    </label></br>''' % (str(row.id), row.name)
                    row.votes = row.votes-1
                else:
                    yield'''<label for="restId">
                        <input type="radio" name="restId" value="%s" id="Poll_0" />
                        %s
                     </label></br>''' % (str(row.id), row.name)
            yield '''<button type="submit">Vote</button>'''

        elif opt == "3":
            self.uname = uname
            objects = session.query(User)
            objects = objects.filter(User.username == self.uname)
            for o in objects:
                if o.voted == 1:
                    yield '''YOU HAVE ALREADY VOTED XD'''
                else:
                    self.voteCount = self.voteCount + 1

                    yield'''
                        <legend>What is your Restaurant of choice?</legend>

                        <form action="results">'''
                    for row in session.query(Restaurant):

                        yield'''<label for="restId">
                            <input type="radio" name="restId" value="%s" id="Poll_0" />
                            %s
                         </label></br>''' % (str(row.id), row.name)
                    yield '''<button type="submit">Vote</button>'''
    
    @cherrypy.expose
    def reset(self):
        for row in session.query(Restaurant):
            row.votes = 0
        for place in session.query(User):
            place.voted = 0
        yield '''CLEARED'''


    @cherrypy.expose
    def results(self, restId):
        restobjects = session.query(Restaurant)
        restobjects = restobjects.filter(Restaurant.id == int(restId))
        for o in restobjects:
            o.votes = o.votes + 1
        for row in session.query(Restaurant):
            percent = int(int(row.votes) / int(self.voteCount) * 100)
            yield '''<body>%s    %s      %s        %s     %s Percent </body></br>
            ''' % (row.name, row.address, row.category, str(row.votes), str(percent))
        userobjects = session.query(User)
        userobjects = userobjects.filter(User.username == self.uname)
        if self.voteCount == 1:
            yield '''</br>%s Person Has Voted''' % str(self.voteCount)
        elif self.voteCount > 1:
            yield '''</br>%s People Have Voted''' % str(self.voteCount)
        for o in userobjects:
            for t in restobjects:
                restaurantId = t.id
            o.rest_id = restaurantId
            o.voted = 1
            session.commit()

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
    cherrypy.quickstart(Poll(), "/", conf)
