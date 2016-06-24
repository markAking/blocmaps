import logging
import logging.handlers

from wsgiref.simple_server import make_server
import os

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/opt/python/log/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

welcome = """

"""

def content_type(path):                                                          
if path.endswith(".css"):                                                    
    return "text/css"                            
else:                                                                        
    return "text/html"

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    resource = path.split("/")[1] 

    if not resource:                                                             
      resource = "index.html"

    resp_file = os.path.join("static", resource)

    try:
      with open(resp_file, "r") as f:
        resp_file = f.read()
    except Exception:
        start_response("404 Not Found", headers)
        return ["404 Not Found"]

    status = '200 OK'
    headers = []
    headers.append(("Content-Type", content_type(resource))) 
    start_response(status, headers)
    return [resp_file]


if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
