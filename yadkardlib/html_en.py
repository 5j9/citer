#! /data/project/yadkard/venv/bin python
# -*- coding: utf-8 -*-

'''HTML skeleton of the application and its predefined responses.'''


class ResposeObj():

    '''Create the responce object used by the main application.'''
    
    def __init__(self, ref, cite, error):
        self.ref = ref
        self.cite = cite
        self.error = error


skeleton = u"""<!DOCTYPE html>
<html>
    <head>
        <title>Yadkard</title>
        <style type="text/css">

            textarea, input {
                transition: background-color 1s ease-in;
                background-background-color: rgb(255, 255, 255);
                border: 1px solid rgb(204, 204, 204);
                padding: 2px 2px;
                margin-bottom: 10px;
                font-size: 14px;
                line-height: 16px;
                color: rgb(85, 85, 85);
                vertical-align: middle;
                border-radius: 5px 5px 5px 5px;
                }
            textarea{
                display:block;
                margin-left: auto;
                margin-right: auto;  
                width:100%%;
                }
            body {
                font-family: tahoma;
                font-size:0.8em
                }
            input[type=text]{
                width:50%%;
                }
            input[type=submit]{
                float:right;
                }
            #info{
                font-size:90%%;
                color:#666666;
                }
            input[type=submit]:hover{
                transition: background-color 2s ease-in;
                background-color:#EB551A;
                }
        </style>
    </head>
    <body>
        <div style="margin-left:auto; margin-right:auto; width:62%%;">
            <form method="get" action="yadkard.fcgi">
                <p>
                    URL/DOI/ISBN:<br><input type="text" name="url">
                    <input type="submit" value="Citation">
                </p>
            </form>
            <p>
                <a href="https://en.wikipedia.org/wiki/Help:Shortened_footnotes">Shortened footnote</a> and citation:<br>
                <textarea rows="10" readonly>%s\n\n%s</textarea>
            </p>
            <p>
                <!-- There may be error in language detection. %s %% -->
            </p>
            <div id="info">
                <p>
                        You can use this tool to create shortened footnotes. Currently the following inputs are supported:</p>
                <p>
                        <a href="http://books.google.com/">Google Books URLs</a>, <a href="https://en.wikipedia.org/wiki/Digital_object_identifier">DOI</a> (Any Digital object Identifier), <a href="https://en.wikipedia.org/wiki/International_Standard_Book_Number">ISBN</a> (International Standard Book Number),</p>
                <p>
                        Plus URL of the following news websites:<br />
                        <a href="http://www.nytimes.com/">The New York Times</a>, <a href="http://www.bbc.com/">BBC</a>, <a href="http://www.dailymail.co.uk/">Daily Mail</a>, <a href="http://www.mirror.co.uk/">Daily Mirror</a>, <a href="http://www.telegraph.co.uk/">The Daily Telegraph</a>, <a href="http://www.huffingtonpost.com/">The Huffington Post</a>, <a href="http://www.washingtonpost.com/">The Washington Post</a>, and The <a href="http://www.boston.com/">Boston</a> <a href="http://www.bostonglobe.com/">Globe</a>.</p>
                <p>
                        Found a bug or have a suggestion? Contact me on my talk page. (User:Dalba).</p>
            </div>
        </div>
    </body>
</html>"""

default_response = (
    u'Generated citation will appear here...',
    '',
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
