import webapp2

import cgi
import urllib
import math

from google.appengine.ext import ndb

def event_key(name):
    return ndb.Key('Event', name)

class User(ndb.Model):
    username = ndb.StringProperty()

class Event(ndb.Model):
    name = ndb.StringProperty()
    # location = ndb.StringProperty()
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()
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
        event_lat = float(self.request.get('lat'))
        event_lon = float(self.request.get('lon'))
        event_dist = float(self.request.get('dist'))
        
        event = Event()
        event.name = event_name
        event.latitude = event_lat
        event.longitude = event_lon
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
            #create a query and fetch list of everything query returns
            user_events = User.query(User.username == username).fetch(1)
            #retrieves the key of the user given user id and parent id 
            sandy_key = ndb.Key(Event, user_events[0].key.parent().id(), User, user_events[0].key.id())
            sandy_key.delete()
            self.response.write('User deleted! ' + sandy_key.urlsafe())
            
            
        # otherwise add a user to an event
        else:
            # Check to see if the event actualy exists
            qry = Event.query(Event.name == event_name)
            if qry.get() == None:
                self.response.write("Wrong event name! " + event_name)
                return
            chosen_event = qry.fetch(1)
            # gives the user the parent by getting the key of the event if the event exists
            user = User(parent=ndb.Key(Event, chosen_event[0].key.id()))
            user.username = self.request.get('username')
            user.put()
            # self.response.write('Post received!' + user.username)
            self.response.write('Post received! event name = '+ event_name)

# Check to see whether user is in an event
class CheckLocation(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        user_lat = float(self.request.get('lat'))
        user_lon = float(self.request.get('lon'))
        qry = Event.query()
        for event in qry:
            event_lat = event.latitude
            event_lon = event.longitude
            dist = distance_on_unit_sphere(user_lat, user_lon,
                                            event_lat, event_lon)
            if (dist <= event.distance):
                self.response.write('Event found! ' + str(dist))
                break


def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )*6373

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc

#the address
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/user', UserManagement),
    ('/check', CheckLocation)
], debug=True)