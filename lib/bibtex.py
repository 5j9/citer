"""This module is used for parsing BibTeX entries.

The goal of this code is to parse BibTeX entries from a number of known sites
with known BibTeX formats; therefore many other BiBteX entries may be parsed
incorrectly or incompletely as TeX system is very complex and this module is
not intended to parse TeX.

Known issues:
    * Currently it does not detect special symbols and many TeX escape
        sequences (more information: http://www.bibtex.org/SpecialSymbols/)
    * String concatenations are not recognized. (e.g. "str1" # "str2")
    * Abbreviations are not supported (e.g. @string { foo = "Mrs. Foo" })
"""

from lib.commons import first_last, rc

# To remove Texts like {APA} from input.
WORDS_IN_BRACES_SUB = rc(r'(?<!=\s*){([^\\{}\n]*)}').sub
FINDALL_BIBTEX_FIELDS = rc(
    r'(\w+)\s*=\s*(?:[{"]\s*(.*?)\s*["}]|(\d+))'
).findall
TYPE_SEARCH = rc(r'(?i)@(.*?)\s*\{').search


def search_for_tag(bibtex: str) -> dict:
    """Find all fields of the bibtex and return result as a dictionary."""
    fs = FINDALL_BIBTEX_FIELDS(bibtex)
    return {f[0].lower(): f[1] if f[1] else f[2] for f in fs}


def parse(bibtex: str) -> dict:
    """Parse bibtex string and return a dictionary of information."""
    bibtex = special_sequence_cleanup(bibtex)
    g = (d := search_for_tag(bibtex)).get
    # cite_type: book, journal, incollection, etc.
    if (m := TYPE_SEARCH(bibtex)) is not None:
        d['cite_type'] = m[1].strip().lower()
    # author
    if author := g('author'):
        d['authors'] = names = []
        names_append = names.append
        for author in author.split(' and '):
            if author.endswith(' and'):
                author = author[:-4]
            if not author:
                continue
            names_append(first_last(author))
        del d['author']
    # editor, not tested, just a copy of author
    if editor := g('editor'):
        d['editors'] = names = []
        names_append = names.append
        for editor in editor.split(' and '):
            if editor.endswith(' and'):
                editor = editor[:-4]
            if not editor:
                continue
            names_append(first_last(editor))
        del d['editor']
    if pages := g('pages'):
        d['page'] = pages.replace(' ', '').replace('--', '–').replace('-', '–')
    return d


def special_sequence_cleanup(bibtex: str) -> str:
    """Replace common TeX special symbol commands with their unicode value."""
    return WORDS_IN_BRACES_SUB(
        r'\g<1>',
        (
            bibtex.replace(r'{\textregistered}', '®')
            .replace(r'{\textquotesingle}', "'")
            .replace(r'{\texttrademark}', '™')
            .replace(r'{\textasciitilde}', '~')
            .replace(r'{\textasteriskcentered}', '∗')
            .replace(r'{\textordmasculine}', 'º')
            .replace(r'{\textordfeminine}', 'ª')
            .replace(r'{\textparagraph}', '¶')
            .replace(r'{\textbackslash}', '\\')
            .replace(r'{\textbar}', '|')
            .replace(r'{\textperiodcentered}', '·')
            .replace(r'{\textbullet}', '•')
            .replace(r'{\textbraceleft}', '{')
            .replace(r'{\textbraceright}', '}')
            .replace(r'{\textquotedblleft}', '“')
            .replace(r'{\textquotedblleft}', '“')
            .replace(r'{\textcopyright}', '©')
            .replace(r'{\textquoteleft}', '‘')
            .replace(r'{\textquoteright}', '’')
            .replace(r'{\textdagger}', '†')
            .replace(r'{\textdaggerdbl}', '‡')
            .replace(r'{\textdollar}', '$')
            .replace(r'{\textsection}', '§')
            .replace(r'{\textellipsis}', '…')
            .replace(r'{\textsterling}', '£')
            .replace(r'{\textemdash}', '—')
            .replace(r'{\textendash}', '–')
            .replace(r'{\textunderscore}', '_')
            .replace(r'{\textexclamdown}', '¡')
            .replace(r'{\textvisiblespace}', '␣')
            .replace(r'{\textgreater}', '>')
            .replace(r'{\textless}', '<')
            .replace(r'{\textasciicircum}', '^')
            .replace(r'{\textquestiondown}', '¿')
            .replace(r'\%', '%')
            .replace(r'\$', '$')
            .replace(r'\{', '{')
            .replace(r'\}', '}')
            .replace(r'\#', '#')
            .replace(r'\&', '&')
            .replace(r'{\={a}}', 'ā')
            .replace(r'{\v{c}}', 'č')
            .replace(r'{\={e}}', 'ē')
            .replace(r'{\v{g}}', 'ģ')
            .replace(r'{\={\i}}', 'ī')
            .replace(r'{\c{k}}', 'ķ')
            .replace(r'{\c{l}}', 'ļ')
            .replace(r'{\c{n}}', 'ņ')
            .replace(r'{\v{s}}', 'š')
            .replace(r'{\={u}}', 'ū')
            .replace(r'{\v{z}}', 'ž')
            .replace(r'{\={A}}', 'Ā')
            .replace(r'{\v{C}}', 'Č')
            .replace(r'{\={E}}', 'Ē')
            .replace(r'{\c{G}}', 'Ģ')
            .replace(r'{\={I}}', 'Ī')
            .replace(r'{\c{K}}', 'Ķ')
            .replace(r'{\c{L}}', 'Ļ')
            .replace(r'{\c{N}}', 'Ņ')
            .replace(r'{\v{S}}', 'Š')
            .replace(r'{\={U}}', 'Ū')
            .replace(r'{\v{Z}}', 'Ž')
        ),
    )
