/*jslint browser: true, regexp: true, white: true */
var months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
];

function getCheckedRadio() {
	'use strict';
	var radio_group, i, button;
	radio_group = document.getElementsByName('dateformat');
	for (i = 0; i < radio_group.length; i = i + 1) {
		button = radio_group[i];
		if (button.checked) {
			return button;
		}
	}
}

function ymd(date) {
	'use strict';
	return date.toISOString()
		.slice(0, 10);
}

function bbdy(date) {
	'use strict';
	return months[date.getMonth()] + ' ' + date.toISOString()
		.slice(8, 10) + ', ' + date.getFullYear();
}

function bdy(date) {
	'use strict';
	return months[date.getMonth()].slice(0, 3) + ' ' + date.toISOString()
		.slice(8, 10) + ', ' + date.getFullYear();
}

function dbby(date) {
	'use strict';
	return date.toISOString()
		.slice(8, 10) + ' ' + months[date.getMonth()] + ' ' + date.getFullYear();
}

function dby(date) {
	'use strict';
	return date.toISOString()
		.slice(8, 10) + ' ' + months[date.getMonth()].slice(0, 3) + ' ' + date.getFullYear();
}

function changeDates(id) {
	'use strict';
	var i, utcdate, text1, text2, dates, date, newdate, formatter;
	text1 = document.getElementById('shortened').innerHTML;
	text2 = document.getElementById('named_ref').innerHTML;
	dates = text1.match(/date=.*?(?=\}\}| \| )/g);
	if (!dates) return;
	for (i = 0; i < dates.length; i = i + 1) {
		date = dates[i].slice(5);
		if (date.indexOf('-') !== -1) {
			utcdate = date;
		} else {
			utcdate = date + " UTC";
		}
		formatter = window[id];
		newdate = formatter(new Date(utcdate))
			.replace(/^[0]+/g, "")
			.replace(" 0", " ");
		text1 = text1.replace(new RegExp('((?:access)?date=)' + date + '(?=}}| \\| )'), '$1' + newdate);
		text2 = text2.replace(new RegExp('((?:access)?date=)' + date + '(?=}}| \\| )'), '$1' + newdate);
		document.getElementById('shortened').innerHTML = text1;
		document.getElementById('named_ref').innerHTML = text2;
	}
}

function setCookie(cname, cvalue, exdays) {
	'use strict';
	var expires, d = new Date();
	d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
	expires = 'expires=' + d.toGMTString();
	document.cookie = cname + '=' + cvalue + '; ' + expires;
}

function getCookie(cname) {
	'use strict';
	var c, i, ca, name = cname + '=';
	ca = document.cookie.split(';');
	for (i = 0; i < ca.length; i = i + 1) {
		c = ca[i].trim();
		if (c.indexOf(name) === 0) {
			return c.substring(name.length, c.length);
		}
	}
	return '';
}

function checkCookie() {
	'use strict';
	var datefmt = getCookie('datefmt');
	if (datefmt !== '') {
		document.getElementById(datefmt).checked = true;
		changeDates(datefmt);
	}
}

function onDateChange() {
	'use strict';
	var id;
	id = getCheckedRadio().id;
	changeDates(id);
	setCookie('datefmt', id, 365);
}
checkCookie();
