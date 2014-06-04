#! /data/project/yadkard/venv/bin
# -*- coding: utf-8 -*-

'''HTML skeleton of the application and its predefined resposes.'''


class ResposeObj():

    '''Create the response object used in the main application.'''
    
    def __init__(self, ref, cite, error):
        self.ref = ref
        self.cite = cite
        self.error = error


skeleton = u"""<!DOCTYPE html>
<html dir="rtl">
<head>
 <title>یادکرد</title>
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
   نشانی وب:<br><input type="text" size="100" name="url">
  <input type="submit" value="یادکرد">
  </p>
 </form>
  <p>
   پانویس کوتاه‌شده و یادکرد:<br>
   <textarea rows="15" cols="80" readonly>%s\n\n%s</textarea>
  </p>
  <p>
   احتمال خطا در تشخیص زبان: %s ٪
  </p>
</body>
</html>"""

default_response = (
    u'این ابزار برای تولید یادکرد مناسب ویکی‌پدیای فارسی، برابر شیوه‌نامهٔ شیکا\
گو، کاربرد دارد.',
    u'هم‌اکنون از وب‌گاه‌های زیر پشتیبانی می‌شود:\n\
* http://books.google.com (گوگل بوکس)\n\
* http://www.noormags.com (نورمگز)\n\
* http://www.noorlib.ir (کتابخانه دیجیتال نور)\n\
* http://www.adinebook.com (آدینه‌بوک)\n\
* http://dx.doi.org (یا متنی که شامل «شناسانۀ برنمود رقمی» (doi) باشد)\n\
* شابک (ISBN) برای بیشتر کتاب‌ها (ایرانی و خارجی)\n\n\
در صورت بروز مشکل یا درست عمل نکردن ابزار می‌توانید با من (دالبا) تماس \
بگیرید. امکان گسترش ابزار برای کتابخانه‌های دیجیتالی که خروجی Bibtex یا \
RefMan ‏(RIS) تولید می‌کنند وجود دارد.',
    u'؟؟')

undefined_url_response = (u'نشانی واردشده برای این ابزار تعریف نشده‌است.',
                      u'اگر کتابخانهٔ دیجیتالی می‌شناسید که خروجی \
bibtex یا RIS تولید می‌کند، لطفاً موضوع را با توسعه‌دهنده ٔ ابزار در میان بگذارید\
 تا در صورت امکان به ابزار افزوده شود.',
                      u'۱۰۰')

httperror_response = (u'خطای اچ‌تی‌تی‌پی در دریافت اطلاعات.',
                      u'اطلاعات قابل دسترس نبودند.',
                      u'۱۰۰')

other_exception_response = (u'خطای پیش‌بینی‌نشده‌ای رخ داد.',
                      u'لطفاً مطمئن شوید که نشانی وب را درست وارد کرده‌اید.',
                      u'۱۰۰')
