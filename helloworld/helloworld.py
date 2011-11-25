import cgi
import webapp2
import datetime
import urllib

from google.appengine.ext import db
from google.appengine.api import users


class Greeting(db.Model):
    """
    Models an individual Guestbook entry with an author, content, and date.
    """
    author = db.UserProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
    """Constructs a datastore key for a Guestbook entity with guestbook_name"""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    """Pagina principal de la aplicacion"""

#    def get(self):
#        #self.obtener_user()
#        self.response.out.write(""
#          <html>
#            <body>
#              <form action="/sign" method="post">
#                <div><textarea name="content" rows="3" cols="60"></textarea></div>
#                <div><input type="submit" value="Sign Guestbook"></div>
#              </form>
#            </body>
#          </html>"")

    def get(self):
        self.response.out.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name')

        greetings = Greeting.all()
        greetings.ancestor(guestbook_key(guestbook_name))
        greetings.filter("author =", users.get_current_user())
        greetings.order("-date")

        for greeting in greetings:
            if greeting.author:
                self.response.out.write(
                '<b>%s</b> wrote:' % greeting.author.nickname())
            else:
                self.response.out.write('An anonymous person wrote:')

            self.response.out.write('<blockquote>%s</blockquote>' %
                                  cgi.escape(greeting.content))
            self.response.out.write('<blockquote>el dia %s</blockquote>' %
                                    cgi.escape(str(greeting.date.date())))

        self.response.out.write(
            """
                <form action="/sign?%s" method="post">
                    <div>
                        <textarea name="content" rows="3" cols="60"></textarea>
                    </div>
                    <div><input type="submit" value="Sign Guestbook"></div>
                </form>
                <hr>
                    <form>Guestbook name:
                        <input value="%s" name="guestbook_name">
                        <input type="submit" value="switch">
                    </form>
                </body>
            </html>""" % (urllib.urlencode({'guestbook_name': guestbook_name}),
                              cgi.escape(guestbook_name)))

    def obtener_user(self):
        """Funcion que obtiene el user actual.
        Si ningun usuario esta logueado redirige a la pagina de logueo"""
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Hello, ' + user.nickname())
        else:
            self.redirect(users.create_login_url(self.request.uri))


class Guestbook(webapp2.RequestHandler):
    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each greeting
        # is in the same entity group. Queries across the single entity group
        # will be consistent. However, the write rate to a single entity
        # group should be limited to ~1/second.
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/sign', Guestbook)], debug=True)
