var longMonths = [
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
var shortMonths = longMonths.map((s) => s.slice(0, 3));
var monthPattern = '(' + shortMonths.join('|') + '|' + longMonths.join('|') + ')';


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

function ymd(y, m, d) {
	'use strict';
	return `${y}-${(m + 1).toString().padStart(2, 0)}-${d.toString().padStart(2, 0)}`;
}

function bbdy(y, m, d) {
	'use strict';
	return longMonths[m] + ' ' + d + ', ' + y;
}

function bdy(y, m, d) {
	'use strict';
	return shortMonths[m] + ' ' + d + ', ' + y;
}

function dbby(y, m, d) {
	'use strict';
	return d + ' ' + longMonths[m] + ' ' + y;
}

function dby(y, m, d) {
	'use strict';
	return d + ' ' + shortMonths[m] + ' ' + y;
}

function parseDate(s) {
	'use strict';
	var m = /(\d{4})-(\d{1,2})-(\d{1,2})/.exec(s);
	if (m) {
		return [parseInt(m[1]), parseInt(m[2]) - 1, parseInt(m[3])];
	}
	m = RegExp(monthPattern + ' ' + /(\d{1,2})/.source + ', ' + /(\d{4})/.source, 'i').exec(s);
	if (m) {
		return [parseInt(m[3]), shortMonths.indexOf(m[1].slice(0, 3)), parseInt(m[2])];
	}
	m = RegExp(/(\d{1,2})/.source + ' ' + monthPattern + ' ' + /(\d{4})/.source, 'i').exec(s);
	if (m) {
		return [parseInt(m[3]), shortMonths.indexOf(m[2].slice(0, 3)), parseInt(m[1])];
	}
}

function changeDates(id) {
	'use strict';
	var i, text1, text2, dates, date, newdate, formatter;
	text1 = document.getElementById('shortened').innerHTML;
	text2 = document.getElementById('named_ref').innerHTML;
	dates = text1.match(/date=.*?(?=\}\}| \| )/g);
	if (!dates) return;
	for (i = 0; i < dates.length; i = i + 1) {
		date = dates[i].slice(5);  // omit the `date=` part
		formatter = window[id];
		var ymd = parseDate(date);
		if (!ymd) {
			console.warn('parseDate(date) returned null');
			continue;
		}
		newdate = formatter(...ymd);
		text1 = text1.replace(new RegExp('((?:access)?date=)' + date + '(?=}}| \\| )'), '$1' + newdate);
		text2 = text2.replace(new RegExp('((?:access)?date=)' + date + '(?=}}| \\| )'), '$1' + newdate);
		document.getElementById('shortened').innerHTML = text1;
		document.getElementById('named_ref').innerHTML = text2;
	}
}

function onDateChange() {
	'use strict';
	var id;
	id = getCheckedRadio().id;
	changeDates(id);
	localStorage.setItem("datefmt", id);
}

// migrate cookie to localStorage (this code can be removed in 400 days)
function cookieToLocalStorage() {
	function getCookie(cname) {
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

	function deleteCookie() {
		document.cookie = 'datefmt=; expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=None; Secure';
	}

	var datefmt = getCookie('datefmt');
	if (datefmt !== '') {
		localStorage.setItem("datefmt", datefmt);
		deleteCookie();
	}
}
cookieToLocalStorage();


function applyLSDateFormat() {
	'use strict';
	var datefmt = localStorage.getItem("datefmt");;
	if (datefmt) {
		document.getElementById(datefmt).checked = true;
		changeDates(datefmt);
	}
}
applyLSDateFormat();
