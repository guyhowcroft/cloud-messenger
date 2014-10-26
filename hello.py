import webapp2
import cgi
import urllib
import time

from google.appengine.ext import ndb

class User(ndb.Model):
    username = ndb.StringProperty()

class Event(ndb.Model):
    name = ndb.StringProperty()
    location = ndb.StringProperty()
    distance = ndb.IntegerProperty()

class MainPage(webapp2.RequestHandler):
	def get(self):
		# user_name = self.request.get('event')
		our_user = Event.query(Event.name=="Bristol uni").fetch(1)
		self.response.headers['Content-Type'] = 'text/plain'
		# Writes response on screen
		self.response.write(str(our_user[0].key.id()))
		# self.response.write('finished ' + str(sandy_key.id()))

#the address
application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)