from re import search, sub

from curl_cffi.requests import get

identifiers = get(
    'https://en.wikipedia.org/wiki/Module:Citation/CS1/Identifiers'
).text
# note: in Lua `-` is equivalent of `*?` in PCRE.
assert '^10%.([^/]+)/[^%s–]-[^%.,]$' in identifiers, (
    'registrant matcher has changed'
)


configuration = get(
    'https://en.wikipedia.org/wiki/Module:Citation/CS1/Configuration?action=raw'
).text
new_set = search(
    r'\nlocal function build_free_doi_registrants_table\(\)'
    r'[^{]*?\{}[^{]*?'  # skip local registrants_t = {};
    r'(\{[\s\S]+?})',
    configuration,
)[1]
with open(__file__ + '/../../lib/doi.py', 'r+') as f:
    data = f.read()
    output = sub(
        r'known_free_doi_registrants = {[\s\S]*?}',
        'known_free_doi_registrants = ' + new_set,
        data,
        1,
    )
    f.seek(0)
    f.write(output)
    f.truncate()
