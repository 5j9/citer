from re import MULTILINE, findall

from curl_cffi.requests import get

github_content = get(
    'https://github.com/SebastianJ/fiber-freeze/raw/master/data/https_urls.txt'
).content
github_domains = set(
    findall(rb'(?<=//)books\.google\.[^/\n]*', github_content, MULTILINE)
)
assert len(github_domains) == 16

# Most referenced domains on the English Wikipedia (2015-05-15) (T96927)
# https://phabricator.wikimedia.org/P587
phab_content = get(
    'https://phab.wmfusercontent.org/file/data/nw6aboiuwxgb4mytb45u/PHID-FILE-perbg6gmtj55dgenca5h/Most_referenced_domains_on_the_English_Wikipedia_%282015-05-15%29_%28T96927%29'
).content
phab_domains = set(
    findall(rb'(?<=//)books\.google\.[^/\n]*', phab_content, MULTILINE)
)

assert 'books.google.co' not in phab_domains | github_domains
