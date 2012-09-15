from framework import bottle
from framework.bottle import route, template, request, error, debug
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from models import PythonTerm
import urllib2
 
@route('/')
def search_form():
    output = template('templates/home')
    return output

@route('/search', method='GET')
def process_search():
          help_string = search_query
          dict = make_function_dict('http://docs.python.org/library/functions.html')
         help_html = dict[help_string]
    search_query = request.GET.get('search_query', '').strip()
    return template('templates/results', search_query=search_query) 
          #return template('templates/results', search_query=search_query)
	
	
def main():
    debug(True)
    run_wsgi_app(bottle.default_app())
 
@error(403)
def error403(code):
    return 'Get your codes right dude, you caused some error!'
 
@error(404)
def error404(code):
    return 'Stop cowboy, what are you trying to find?'
 
if __name__=="__main__":
    main()