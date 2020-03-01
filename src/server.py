import http.server, socket, socketserver, sys, re, cgi

class Handler (http.server.BaseHTTPRequestHandler):

  def response(self, n):
    self.send_response(n)
    self.send_header("Content-type", "text/html")
    self.end_headers()

  def validate(self, line, method):
    if method == 'GET':
      re_type = r"(?<=type=)(A|PTR)(?=&|$)"
    elif method == 'POST':
      re_type = r"(?<=:)(A|PTR)$"

    response_type = re.search(re_type, line)
    if response_type == None:
      self.response(400)
      return None
    
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
      self.response(400)
      return None

    try:
      if response_type.group(0) == 'A':
        resolved_name_or_ip = socket.gethostbyname(name_or_ip.group(0))
      elif response_type.group(0) == 'PTR':
        resolved_name_or_ip = socket.gethostbyaddr(name_or_ip.group(0))[0]
    except:
      self.response(404)
      return None

    return name_or_ip.group(0), response_type.group(0), resolved_name_or_ip

  def do_GET(self):

    if re.search(r"^/resolve", self.path) == None:
      self.response(400)
      return

    result = self.validate(self.path, 'GET')
    if result == None:
      return
    else:
      name_or_ip, response_type, resolved_name_or_ip = result

    self.response(200)
    self.wfile.write((name_or_ip + ':' + response_type + '=' + resolved_name_or_ip).encode('utf-8'))

  def do_POST(self):

    if self.path != "/dns-query":
      self.response(400)
      return

    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    output = ''
    for line in iter(post_data.decode('utf-8').splitlines()):
      result = self.validate(line, 'POST')
      if result == None:
        return
      else:
        name_or_ip, response_type, resolved_name_or_ip = result
        output += (name_or_ip + ':' + response_type + '=' + resolved_name_or_ip + '\n')

    self.response(200)
    self.wfile.write(output.rstrip().encode('utf-8'))

  def do_HEAD(self):
    self.response(405)

  def do_PUT(self):
    self.response(405)

  def do_DELETE(self):
    self.response(405)
  
  def do_CONNECT(self):
    self.response(405)

  def do_OPTIONS(self):
    self.response(405)

  def do_TRACE(self):
    self.response(405)

  def do_PATCH(self):
    self.response(405)

if __name__ == "__main__":

  if len(sys.argv) > 1 and sys.argv[1].isdigit() and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 65535:
    PORT = int(sys.argv[1])
  else:
    PORT = 5353

  with socketserver.TCPServer(("", PORT), Handler) as httpd:
      try:
        httpd.serve_forever()
      except Exception:
        pass
      finally:
        httpd.server_close()
