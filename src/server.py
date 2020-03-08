import http.server, socket, socketserver, sys, re, cgi

class Handler (http.server.BaseHTTPRequestHandler):

  verbose_response = {200: "OK", 400: "Bad Request.", 404: "Not Found.", 405: "Method Not Allowed.", 500: "Internal Server Error."}

  def parse_request(self):
    """
    Alters behaviour of identical named parent's method to accept only GET and POST requests
    """
    super().parse_request()
    if self.command != 'GET' and self.command != 'POST':
      self.response(405, self.verbose_response[405])
      return
    elif self.command == 'GET':
      self.GET()
    elif self.command == 'POST':
      self.POST()
    self.wfile.flush()
  

  def response(self, n, msg=None):
    """
    Quick response method
    """
    self.protocol_version = 'HTTP/1.1'
    self.send_response(n, msg)
    self.send_header("Content-type", "text/plain")
    self.end_headers()

  def validate(self, line, method):
    """
    Validates request
    """
    if method == 'GET':
      re_type = r"(?<=type=)(A|PTR)(?=&|$)"
    elif method == 'POST':
      re_type = r"(?<=:)(A|PTR)$"

    response_type = re.search(re_type, line)
    if response_type == None:
      return (400, None, None, None)
    
    if response_type.group(0) == 'A':
      if method == 'GET':
        re_name = r"(?<=name=)(.*?)(?=&|$)"
      elif method == 'POST':
        re_name = r"^(.*?)(?=:)"
        
    elif response_type.group(0) == 'PTR':
      if method == 'GET':
        re_name = r"(?<=name=)(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?=&|$)"
      elif method == 'POST':
        re_name = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?=:)"
        
    name_or_ip = re.search(re_name, line) 
    if name_or_ip == None:
      return (400, None, None, None)

    try:
      if response_type.group(0) == 'A':
        resolved_name_or_ip = socket.gethostbyname(name_or_ip.group(0))
      elif response_type.group(0) == 'PTR':
        resolved_name_or_ip = socket.gethostbyaddr(name_or_ip.group(0))[0]
    except:
      return (404, None, None, None)

    if repr(name_or_ip.group(0)) == repr(resolved_name_or_ip):
      return (400, None, None, None)
    else:
      return (200, name_or_ip.group(0), response_type.group(0), resolved_name_or_ip)

  def GET(self):
    """
    Answers GET requests
    """
    if re.search(r"^/resolve", self.path) == None:
      self.response(400, self.verbose_response[400])
      return

    code, name_or_ip, response_type, resolved_name_or_ip = self.validate(self.path, 'GET')
    self.response(code, self.verbose_response[code])
    if code == 200:
      self.wfile.write((name_or_ip + ':' + response_type + '=' + resolved_name_or_ip).encode('utf-8'))

  def POST(self):
    """
    Answers POST requests
    """
    if self.path != "/dns-query":
      self.response(400, self.verbose_response[400])
      return

    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    output = ''
    codes = []
    for line in iter(post_data.decode('utf-8').splitlines()):
      code, name_or_ip, response_type, resolved_name_or_ip = self.validate(line, 'POST')
      codes.append(code)
      if code == 200:
        output += (name_or_ip + ':' + response_type + '=' + resolved_name_or_ip + '\n')

    if 200 in codes:
      self.response(200, self.verbose_response[200])
      self.wfile.write(output.rstrip().encode('utf-8'))
    elif 400 in codes:
      self.response(400, self.verbose_response[400])
    else:
      self.response(code, self.verbose_response[code])

if __name__ == "__main__":

  # Sets port
  if len(sys.argv) > 1 and sys.argv[1].isdigit() and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 65535:
    PORT = int(sys.argv[1])
  else:
    PORT = 5353

  # Server init
  with socketserver.TCPServer(("", PORT), Handler) as server:
      try:
        server.serve_forever()
      finally:
        server.shutdown()
        server.server_close()
