# https://gist.github.com/DannyHinshaw/a3ac5991d66a2fe6d97a569c6cdac534

# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443


import http.server
import ssl
from pathlib import Path

test_dir = Path(__file__).parent

server_address = ('localhost', 4443)
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.check_hostname = False # If set to True, only the hostname that matches the certificate will be accepted
context.load_cert_chain(certfile=test_dir / "pki/issued/localhost.crt", keyfile=test_dir / "pki/private/localhost.key")
httpd.socket = context.wrap_socket(
    httpd.socket,
    server_side=True,
)
httpd.serve_forever()

