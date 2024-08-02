// @ts-check
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
	var /**@type {any} */radio_group, i, /** @type {HTMLInputElement} */ button;
	radio_group = document.getElementsByName('dateformat');
	for (i = 0; i < radio_group.length; i = i + 1) {
		button = radio_group[i];
		if (button.checked) {
			return button;
		}
	}
}

/**
 * 
 * @param {number} y 
 * @param {number} m 
 * @param {number} d 
 * @returns {String}
 */
function ymd(y, m, d) {
	'use strict';
	return `${y}-${(m + 1).toString().padStart(2, '0')}-${d.toString().padStart(2, '0')}`;
}

/**
 * 
 * @param {number} y 
 * @param {number} m 
 * @param {number} d 
 * @returns {String}
 */
function bbdy(y, m, d) {
	'use strict';
	return longMonths[m] + ' ' + d + ', ' + y;
}

/**
 * 
 * @param {number} y 
 * @param {number} m 
 * @param {number} d 
 * @returns {String}
 */
function bdy(y, m, d) {
	'use strict';
	return shortMonths[m] + ' ' + d + ', ' + y;
}

/**
 * 
 * @param {number} y 
 * @param {number} m 
 * @param {number} d 
 * @returns {String}
 */
function dbby(y, m, d) {
	'use strict';
	return d + ' ' + longMonths[m] + ' ' + y;
}

/**
 * 
 * @param {number} y 
 * @param {number} m 
 * @param {number} d 
 * @returns {String}
 */
function dby(y, m, d) {
	'use strict';
	return d + ' ' + shortMonths[m] + ' ' + y;
}

/**
 * 
 * @param {String} s 
 * @returns {Array<number> | undefined}
 */
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

/**
 * 
 * @param {String} id 
 */
function changeDates(id) {
	'use strict';
	var i, text1, text2, dates, date, newdate, formatter;
	text1 = /**@type {HTMLElement} */(document.getElementById('shortened')).innerHTML;
	text2 = /**@type {HTMLElement} */(document.getElementById('named_ref')).innerHTML;
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
		/**@type {HTMLElement} */(document.getElementById('shortened')).innerHTML = text1;
		/**@type {HTMLElement} */(document.getElementById('named_ref')).innerHTML = text2;
	}
}


function applyLSDateFormat() {
	'use strict';
	var datefmt = localStorage.getItem("datefmt");
	if (datefmt) {
		/**@type {HTMLInputElement} */(document.getElementById(datefmt)).checked = true;
		changeDates(datefmt);
	}
}
applyLSDateFormat();
