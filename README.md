yadkard
=======

A citation creation tool for Persian Wikipedia. Currently accessible from:
http://toolserver.org/~dalba/yadkard.fcgi

If running on local computer, the tool is accessible from:
http://127.0.0.1:8051/

If on a web server, the configuration of "Web Server Gateway Interface" (WSGI) will depend on your server. You may need to change yadkard.py's extension to something else (e.g. yadkard.fcgi on toolserver.org) and/or import appropriate module for it. (currently: "from flup.server.fcgi import WSGIServer")