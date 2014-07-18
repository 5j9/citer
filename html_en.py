#! /usr/bin/python
# -*- coding: utf-8 -*-

"""HTML skeleton of the application and its predefined responses."""


from string import Template
from datetime import date

class Respose:

    """Create the responce object used by the main application."""

    def __init__(self, sfnt, ctnt='', reft='', error='100'):
        self.sfnt = sfnt
        self.ctnt = ctnt
        self.reft = reft
        self.error = error


def response_to_template(response):
    """Insert the response into the template and return response_body."""
    return template % (response.sfnt,
                       response.ctnt,
                       response.reft,
                       response.error)


template = Template("""<!DOCTYPE html>
<html>
    <head>
        <title>Yadkard</title>
        <style type="text/css">

            textarea, input {
                transition: background-color 5s ease-in;
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
            textarea{
                display:block;
                margin-left: auto;
                margin-right: auto;
                width:100%;
                word-break: break-all;
                }
            body {
                font-family: tahoma;
                font-size:0.8em
                }
            input[type=text]{
                width:50%;
                }
            input[type=submit]{
                float:right;
                }
            #info{
                font-size:90%;
                color:#666666;
                }
            input[type=submit]:hover{
                transition: background-color 1s ease-in;
                background-color:#33CC33;
                }
        </style>
    </head>
    <body>
        <div style="margin-left:auto; margin-right:auto; width:62%;">
            <form method="get" action="yadkard.fcgi">
                <p>
                    URL/DOI/ISBN:<br><input type="text" name="user_input">
                    <input type="submit" value="Submit">
                </p>
                <p>Date format:</p>
                <input type="radio" value="%Y-%m-%d" name="dateformat" id="Ymd" onclick="setCookie('datefmt', 'Ymd', 365)" checked>$Ymd
                <input type="radio" value="%B %d, %Y" name="dateformat" id="BdY" onclick="setCookie('datefmt', 'BdY', 365)">$BdY
                <input type="radio" value="%b %d, %Y" name="dateformat" id="bdY" onclick="setCookie('datefmt', 'bdY', 365)">$bdY
                <input type="radio" value="%d %B %Y" name="dateformat" id="dBY" onclick="setCookie('datefmt', 'dBY', 365)">$dBY
                <input type="radio" value="%d %b %Y" name="dateformat" id="dbY" onclick="setCookie('datefmt', 'dbY', 365)">$dbY
            </form>
            <p>
                <a href="https://en.wikipedia.org/wiki/Help:Shortened_footnotes">Shortened footnote</a> and citation:<br>
                <textarea rows="6" readonly>$s\n\n$s</textarea>
                <a href="https://en.wikipedia.org/wiki/Wikipedia:NAMEDREFS#WP:NAMEDREFS">Named reference</a>:<br>
                <textarea rows="4" readonly>$s</textarea>
            </p>
            <p>
                <!-- There may be error in language detection. $s % -->
            </p>
            <div id="info">
                <p>
                        You can use this tool to create shortened footnote/named reference for a given:</p>
                <p>
                        <a href="http://books.google.com/">Google Books URL</a>, <a href="https://en.wikipedia.org/wiki/Digital_object_identifier">DOI</a> (Any Digital object Identifier) or <a href="https://en.wikipedia.org/wiki/International_Standard_Book_Number">ISBN</a> (International Standard Book Number).</p>
                <p>
                        Additionaly, URL of many major news websites are supported. That includes (but is not limited to):<br />
                        <a href="http://www.nytimes.com/">The New York Times</a>, <a href="http://www.bbc.com/">BBC</a>, <a href="http://www.dailymail.co.uk/">Daily Mail</a>, <a href="http://www.mirror.co.uk/">Daily Mirror</a>, <a href="http://www.telegraph.co.uk/">The Daily Telegraph</a>, <a href="http://www.huffingtonpost.com/">The Huffington Post</a>, <a href="http://www.washingtonpost.com/">The Washington Post</a>, The <a href="http://www.boston.com/">Boston</a> <a href="http://www.bostonglobe.com/">Globe</a>, <a href="http://www.businessweek.com/">Bloomberg Businessweek</a>, <a href="http://www.ft.com/">Financial Times</a>, and <a href="http://timesofindia.indiatimes.com/">The Times of India</a>.</p>
                <p>
                        Note that there is always a chance of error in the generated output. <b>Please check the results before using them on Wiki</b>.</p>
                <p>
                        Found a bug or have a suggestion? Contact me on my talk page. (<a href="https://wikitech.wikimedia.org/wiki/User_talk:Dalba">User:Dalba</a>).</p>
            </div>
        </div>
        <script>
            function setCookie(cname, cvalue, exdays) {
                var d = new Date();
                d.setTime(d.getTime() + (exdays*24*60*60*1000));
                var expires = "expires="+d.toGMTString();
                document.cookie = cname + "=" + cvalue + "; " + expires;
            }

            function getCookie(cname) {
                var name = cname + "=";
                var ca = document.cookie.split(';');
                for(var i=0; i<ca.length; i++) {
                    var c = ca[i].trim();
                    if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
                }
                return "";
            }

            function checkCookie() {
                var datefmt = getCookie('datefmt');
                if (datefmt != '') {
                  document.getElementById(datefmt).checked = true;
                }
            }
            checkCookie()
        </script>
    </body>
</html>""")

# Predefined responses
default_response = Respose('Generated citation will appear here...',
                           '',
                           '',
                           '??')

undefined_url_response = Respose('Undefined input.',
                                 'Sorry, the input was not recognized. ' +
                                 'The error was logged.')

httperror_response = Respose('HTTP error:',
                             'One or more of the web resources required to ' +
                             'create this citation are not accessible at ' +
                             'this moment.')

other_exception_response = Respose('An unknown error occurred.',
                                   'The error was logged.')

today = date.today()
template = template.safe_substitute({'Ymd': today.strftime('%Y-%m-%d'),
                                     'BdY': today.strftime('%B %d, %Y'),
                                     'bdY': today.strftime('%b %d, %Y'),
                                     'dBY': today.strftime('%d %B %Y'),
                                     'dbY': today.strftime('%d %b %Y'),
                                     }).replace('%', '%%').replace('$', '%')

