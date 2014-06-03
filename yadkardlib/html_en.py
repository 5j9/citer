#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''This module contains html skeleton of the application and its predefined
 responses'''

class ResposeObj():
    def __init__(self, ref, cite, error):
        self.ref = ref
        self.cite = cite
        self.error = error

skeleton = u"""<!DOCTYPE html>
<html>
<head>
 <title>Yadkard</title>
 <style type="text/css">
  select, textarea, input {
   background-color: rgb(255, 255, 255);
   border: 1px solid rgb(204, 204, 204);
   padding: 2px 2px;
   margin-bottom: 10px;
   font-size: 14px;
   line-height: 16px;
   color: rgb(85, 85, 85);
   vertical-align: middle;
   border-radius: 5px 5px 5px 5px;
   }
  body {
  font-family: tahoma;
  font-size:0.8em
  }
  </style>
</head>
<body>
 <form method="get" action="yadkard.fcgi">
  <p>
   URL/DOI/ISBN:<br><input type="text" size="95" name="url">
  <input type="submit" value="Citation">
  </p>
 </form>
  <p>
   <a href="https://en.wikipedia.org/wiki/Help:Shortened_footnotes">Shortened footnote</a> and citation:<br>
   <textarea rows="15" cols="80" readonly>%s\n\n%s</textarea>
  </p>
  <p>
   <!-- There may be error in language detection. %s %% -->
  </p>
</body>
</html>"""

default_response = (
    u'You can use this tool to create shortened footnotes.',
    u'Currently the following inputs are supported:\n\n\
* http://books.google.com\t(Google Books URLs)\n\
* http://www.nytimes.com\t(New York Times)\n\
* http://www.bbc.com\t\t(BBC)\n\
* http://www.dailymail.co.uk\t(Daily Mail)\n\
* http://www.mirror.co.uk\t(Daily Mirror)\n\
* http://www.telegraph.co.uk\t(The Daily Telegraph)\n\
* http://www.huffingtonpost.com\t(The Huffington Post)\n\
* http://www.washingtonpost.com\t(The Washington Post)\n\
* DOI\t\t\t\t(Any Digital object Identifier)\n\
* ISBN\t\t\t\t(International Standard Book Number)\n\n\
Found a bug or have a suggestion? Contact me on my talk page. (User:Dalba).',
    u'??')

undefined_url_response = ('Undefined input.',
                      'Sorry, the input was not recognized. \
The error was logged.',
                      '100')

httperror_response = ('HTTP error:',
                      'One or more of the web resources required to create \
this citation are not accessible at this moment.',
                      u'100')

other_exception_response = (u'An unknown error occurred.',
                      u'The error was logged.',
                      u'100')
