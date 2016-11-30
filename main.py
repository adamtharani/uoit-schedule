#! /usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from schedule import get_schedule
from datetime import datetime
from base64 import b64encode
from urllib import parse

# Winter semester, 2017
start_date = datetime(2017, 1, 9)

class Server(BaseHTTPRequestHandler):
  def _set_headers(self):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

  def do_GET(self):
    self._set_headers()
    with open('index.html', 'rb') as f:
      self.wfile.write(f.read())

  def do_HEAD(self):
    self._set_headers()
      
  def do_POST(self):
    self.send_response(200)
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    post_data = {k:v for k, v in (x.split('=') for x in post_data.decode('utf-8').split('&'))}

    schedule, warnings = get_schedule(post_data['username'], parse.unquote(post_data['password']), start_date)
    if schedule:
      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      self.end_headers()
      encoded_schedule = 'data:application/octet-stream;base64,' + b64encode(str(schedule).encode('utf-8')).decode('utf-8')
      output = '<html><body><h1>Schedule created '
      if warnings:
        output += 'with %s warning%s!</h1><ul>'% (len(warnings), '' if len(warnings) == 1 else 's')
        for warning in warnings:
          output += '<li>' + warning + '</li>'
        output += '</ul>'
      else:
        output += 'successfully!</h1>'
      output += '<h2><a download="%s" href="%s" title="Download Schedule">Click here to download your schedule</a></h2>' % (post_data['username'] + '.ics', encoded_schedule)
      output += '<a href="/"">go back</a><p>Created by <a href="https://arilotter.com/">Ari Lotter</a></p></body></html>'

      self.wfile.write(output.encode('utf-8'))
      
    else:
      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      self.end_headers()
      self.wfile.write(b'<html><body><h1>Bad username or password!</h1><a href="/"">go back</a><p>Created by <a href="https://arilotter.com/">Ari Lotter</a></p></body></html>')


def run(server_class=HTTPServer, handler_class=Server, port=8080):
  server_address = ('', port)
  httpd = server_class(server_address, handler_class)
  print('Starting httpd...')
  httpd.serve_forever()

if __name__ == "__main__":
  run()