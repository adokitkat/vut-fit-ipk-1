import http.server, socket, socketserver, sys, re, cgi

class Handler (http.server.BaseHTTPRequestHandler):

  def response(self, n):
    self.send_response(n)
    self.send_header("Content-type", "text/html")
    self.end_headers()

  def validate(self, line, method):
    if method == 'GET':
      re_name = r"(?<=name=)(.*?)(?=&|$)"
      re_type = r"(?<=type=)(A|PTR)(?=&|$)"
    elif method == 'POST':
      re_name = r"^(.*?)(?=:)"
      re_type = r"(?<=:)(A|PTR)$"

    name_or_ip = re.search(re_name, line)
    response_type = re.search(re_type, line)
    if name_or_ip == None or response_type == None:
      self.response(400)
      return None
    
    if response_type.group(1) == 'A':
      try:
        resolved_name_or_ip = socket.gethostbyname(name_or_ip.group(1))
      except:
        self.response(404)
        return None
    
    elif response_type.group(1) == 'PTR':
      try:
        resolved_name_or_ip = socket.gethostbyaddr(name_or_ip.group(1))[0]
      except:
        self.response(404)
        return None

    return name_or_ip.group(1), response_type.group(1), resolved_name_or_ip

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

if __name__ == "__main__":

  if len(sys.argv) > 1 and sys.argv[1].isdigit() and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 65535:
    PORT = int(sys.argv[1])
  else:
    PORT = 5353

  with socketserver.TCPServer(("", PORT), Handler) as httpd:
      print("serving at port", PORT)
      try:
        httpd.serve_forever()
      except Exception:
        pass
      finally:
        httpd.server_close()
