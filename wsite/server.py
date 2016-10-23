#!/usr/bin/python
# from www.acmesystems.it/python_httpserver
import sys
import json
import logging
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

from views import compute_departement_stats

#ROOT_FOLDER = "/home/jedi/Dropbox/projects/python/immodb/wsite"
ROOT_FOLDER = curdir + sep + "wsite"
PORT_NUMBER = 8080

def configure_logger():
  root = logging.getLogger()
  root.setLevel(logging.DEBUG)
  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  root.addHandler(ch)  

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
  #Handler for the GET requests
  def do_GET(self):
    if self.path == "/departements-stats":
      self.send_response(200)
      self.send_header('Content-type', 'application/json')
      self.end_headers()
      departement_average = compute_departement_stats()
      json.dump(departement_average, self.wfile)
      return
    self.fetch_file()
    return

  def fetch_file(self):
    if self.path=="/":
      self.path="/index.html"    
    try:
      #Check the file extension required and
      #set the right mime type
      sendReply = False
      if self.path.endswith(".html"):
        mimetype='text/html'
        sendReply = True
      elif self.path.endswith(".jpg"):
        mimetype='image/jpg'
        sendReply = True
      elif self.path.endswith(".gif"):
        mimetype='image/gif'
        sendReply = True
      elif self.path.endswith(".js"):
        mimetype='application/javascript'
        sendReply = True
      elif self.path.endswith(".css"):
        mimetype='text/css'
        sendReply = True
      elif (self.path.endswith(".json") or 
            self.path.endswith(".topojson")):
        mimetype='data/json'
        sendReply = True
      else:
        self.send_error(404,'File Not Found: %s' % self.path)
      if sendReply == True:
        #Open the static file requested and send it
        f = open(ROOT_FOLDER + sep + self.path) 
        self.send_response(200)
        self.send_header('Content-type',mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()
      return
    except IOError:
      self.send_error(404,'File Not Found: %s' % self.path)

def serve(port):
  try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', port), myHandler)
    print 'Started httpserver on port ' , port
    
    #Wait forever for incoming htto requests
    server.serve_forever()

  except KeyboardInterrupt:
    print '^C received, shutting down the web server'
    server.socket.close()


def main():
  configure_logger()
  port = int(sys.argv[1]) if len(sys.argv) == 2 else PORT_NUMBER
  serve(port)

if __name__ == "__main__":
  main()