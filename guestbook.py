import webapp2

import cgi
import urllib

from google.appengine.ext import ndb

def event_key(name):
    return ndb.Key('Event', name)

class User(ndb.Model):
    username = ndb.StringProperty()

class Event(ndb.Model):
    name = ndb.StringProperty()
    location = ndb.StringProperty()
    distance = ndb.IntegerProperty()

class MainPage(webapp2.RequestHandler):
    # Responds to GET HTTP request
    def get(self):
        # Query the datastore for all the locations of current events
        qry = Event.query()
        response_string = ""
        for event in qry.fetch():
            response_string += "["
            response_string += event.location
            response_string += ","
            response_string += str(event.distance)
            response_string += "]"
        self.response.headers['Content-Type'] = 'text/plain'
        # Writes response on screen
        self.response.write(response_string)
        
    # Creates an event    
    def post(self):
        event_name = self.request.get('event')
        event_loc = self.request.get('loc')
        event_dist = self.request.get('dist')
        
        event = Event()
        event.name = event_name
        event.location = event_loc
        event.distance = int(event_dist)
        event.put()
        self.response.write('Event added to database')

# Adds a user to an event
class UserManagement(webapp2.RequestHandler):
    def post(self):
        # for response  
        self.response.headers['Content-Type'] = 'text/plain'
        # get the event name from the request
        event_name = self.request.get('event')
        
        
        # if no event name given, delete the user from the event
        if len(event_name) == 0:
            username = self.request.get('username')
            #que = User.query(User.username == username).fetch(keys_only=True)
            #ndb.delete_multi(que)
            ndb.Key(User, int(username)).delete()
            self.response.write('User deleted! ')
            
            
        # otherwise add a user to an event
        else:
            # Check to see if the event actualy exists
            qry = Event.query(Event.name == event_name)
            if qry.get() == None:
                self.response.write("Wrong event name! " + event_name)
                return
            # gives the user the parent by getting the key of the event if the event exists
            user = User(parent=ndb.Key(Event, event_name))
            user.username = self.request.get('username')
            user.put()
            # self.response.write('Post received!' + user.username)
            self.response.write('Post received! event name = '+ event_name)
        
    
#the address
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/user', UserManagement),
], debug=True)