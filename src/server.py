import http.server, socket, socketserver, sys, re

class Handler (http.server.BaseHTTPRequestHandler):

  def response(self, n):
    self.send_response(n)
    self.send_header("Content-type", "text/html")
    self.end_headers()

  def do_GET(self):

    if re.search(r"^/resolve", self.path) == None:
      self.response(400)
      return

    re_name = r"(?<=name=)(.*?)(?=&|$)"
    name_or_ip = re.search(re_name, self.path)
    if name_or_ip == None:
      self.response(400)
      return

    re_type = r"(?<=type=)(A|PTR)(?=&|$)"
    response_type = re.search(re_type, self.path)
    if response_type == None:
      self.response(400)
      return
    
    elif response_type.group(1) == 'A':
      try:
        resolved_name_or_ip = socket.gethostbyname(name_or_ip.group(1))
      except:
        self.response(404)
        return
    
    elif response_type.group(1) == 'PTR':
      try:
        resolved_name_or_ip = socket.gethostbyaddr(name_or_ip.group(1))[0]
      except:
        self.response(404)
        return

    self.response(200)
    self.wfile.write((name_or_ip.group(1) + ':' + response_type.group(1)+ '=' + resolved_name_or_ip).encode('utf-8'))

  def do_POST(self):

    if re.search(r"^/dns-query", self.path) == None:
      self.response(400)
      return

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

if __name__ == "__main__":

  if len(sys.argv) > 1 and sys.argv[1].isdigit() and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 65535:
    PORT = int(sys.argv[1])
  else:
    PORT = 5353

  with socketserver.TCPServer(("", PORT), Handler) as httpd:
      print("serving at port", PORT)
      try:
        httpd.serve_forever()
      except:
        pass
      httpd.server_close()
