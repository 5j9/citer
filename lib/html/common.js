/*jslint browser: true, regexp: true, white: true */
document.querySelector('link').href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>";

var shortElem = document.getElementById('shortened');
var namedElem = document.getElementById('named_ref');

function copyText(elem, mode) {
    var text = elem.innerText;
    switch (mode) {
        case 0:
        case 1:
            text = text.split('\n\n')[mode];
            break;
        case 3:  // self-closing ref
            text = text.slice(0, text.indexOf('>')) + '/>';
            break;
        case 4:  // ref without name
            text = text.replace(/ name=".*?">/, '>');
            break;
    }
    navigator.clipboard.writeText(text);
}

function onInputTypeSelect() {
    var elem = document.getElementById('input_type');
    var value = elem.options[elem.selectedIndex].value;
    var url = new URL(window.location);
    url.searchParams.set('input_type', value);
    history.replaceState(null, "", url);
}
