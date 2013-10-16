#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from cgi import escape
from urlparse import parse_qs

from yadkardlib import noormags, googlebooks, noorlib


html = """
<html dir="rtl">
<head>
 <title>یادکرد</title>
</head>
<body style="font-family: tahoma; font-size:0.8em">
 <form method="get" action="yadkard.fcgi">
  <p>
   نشانی وب:<br><input type="text" size="100" name="url">
  <input type="submit" value="یادکرد">
  </p>
 </form>
  <p>
   پانویس کوتاه‌شده و یادکرد:<br>
   <textarea rows="10" cols="80" readonly>%s\n\n%s</textarea>
  </p>
  <p>
   احتمال خطا در تشخیص زبان: %s ٪
  </p>
</body>
</html>"""

    	
def application(environ, start_response):
    qdict = parse_qs(environ['QUERY_STRING'])
    url = qdict.get('url', [''])[0]
    url = escape(url)
    
    try:
        if 'noormags.com' in url:
            obj = noormags.NoorMag(url)
        elif 'noorlib.ir' in url:
            obj = noorlib.NoorLib(url)
        elif 'books.google' in url:
            obj = googlebooks.GoogleBook(url)
        else:
            obj = object()
            obj.ref = 'نشانی‌وارد شده برای این ابزار تعریف نشده است'
            obj.cite = 'اگر کتابخانهٔ دیجیتالی می‌شناسید که خروجی bibtex یا RIS \
تولید می‌کند، لطفاً موضوع را با توسعه‌دهندهٔ ابزار در میان بگذارید تا در صورت \
امکان به ابزار افزوده شود'
            obj.error = '۱۰۰'
        response_body = html % (obj.ref,
                                obj.cite,
                                obj.error)
    except (TypeError, AttributeError), e:
        response_body = html % ('این ابزار برای تولید یادکرد مناسب ویکی‌پدیا\
 برابر شیوه‌نامهٔ شیکاگو کاربرد دارد.',
                                'در صورت بروز مشکل یا درست عمل نکردن ابزار \
می‌توانید با من (دالبا) تماس بگیرید\n\n\
امکان گسترش ابزار برای کتابخانه‌های دیجیتالی که خروجی bibtex یا refman (ris)‎ \
تولید می‌کنند وجود دارد. هم‌اکنون از وب‌گاه‌های زیر پشتیبانی می‌شود:\n\n\
* http://books.google.com\n\
* http://www.noormags.com\n\
* http://www.noorlib.ir',
                                '??')
    status = '200 OK'

    response_headers = [('Content-Type', 'text/html; charset=UTF-8'),
                  ('Content-Length', str(len(response_body)))]
    start_response(status, response_headers)

    return [response_body]

try:
    from flup.server.fcgi import WSGIServer
    #on toolserver:
    WSGIServer(application).run()
except ImportError:
    #on local computer:
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    httpd.serve_forever()
