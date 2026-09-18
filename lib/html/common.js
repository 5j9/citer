/*jslint browser: true, regexp: true, white: true */
document.querySelector('link').href = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>";

var shortElem = document.getElementById('shortened');
var namedElem = document.getElementById('named_ref');
var form = document.getElementById('form');

function copyText(elem, mode) {
    var text = elem.textContent;
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

function updateURL(paramName, paramValue) {
    var url = new URL(window.location);
    url.searchParams.set(paramName, paramValue);
    history.replaceState(null, "", url);
}

function onInputTypeSelect() {
    var elem = document.querySelector('input[name="input_type"]:checked');
    updateURL('input_type', elem.value);
}

// Reusable core logic to execute the POST request with the custom header
async function submitData(jsonData) {
    var submitElem = document.getElementById("submit");
    submitElem.disabled = true;
    try {
        var response = await fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Gateway-Validation': 'CITER_IS_NOT_INTENDED_FOR_BOTS'
            },
            body: JSON.stringify(jsonData)
        });

        var scr = await response.json();
        document.getElementById('shortened').textContent = scr[0] + '\n\n' + scr[1];
        document.getElementById('named_ref').textContent = scr[2];
    } catch (error) {
        document.getElementById('shortened').textContent = `Failed to fetch citation: ${error}`;
        document.getElementById('named_ref').textContent = '';
    } finally {
        submitElem.disabled = false;
        document.getElementById("user_input").value = '';
    }
}

async function onFormSubmit(event) {
    event.preventDefault();
    var formData = new FormData(this);
    var j = Object.fromEntries(formData);
    var user_input = j['user_input'] = j['user_input'].trim();
    if (!user_input) {
        return;
    }
    updateURL('user_input', user_input);
    await submitData(j);
}

form.onsubmit = onFormSubmit;

// Detect query parameters on page load and automatically submit via POST
window.addEventListener('DOMContentLoaded', async () => {
    var urlParams = new URLSearchParams(window.location.search);
    var inputType = urlParams.get('input_type');
    if (inputType) {
        var elem = document.querySelector(
            `input[name="input_type"][value="${CSS.escape(inputType)}"]`
        );
        if (elem) {
            elem.checked = true;
        }
    }
    var userInput = urlParams.get('user_input');
    if (userInput) {
        userInput = userInput.trim();
        if (!userInput) return;

        // Build the data object directly from URL parameters
        var jsonData = {
            user_input: userInput,
            input_type: urlParams.get('input_type') || '',
            dateformat: urlParams.get('dateformat') || '',
            pipeformat: urlParams.get('pipeformat') || ''
        };

        // Trigger the automatic lookup via POST
        await submitData(jsonData);
    }
});