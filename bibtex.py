#! /usr/bin/python
# -*- coding: utf-8 -*-

"""This module is used for parsing BibTeX entries.

The goal of this code is to parse BibTeX entries from a number of known sites
with known BibTeX formats; therefore many other BiBteX entries may be parsed
incorrectly or incompletely as TeX system is very complex and this module is
not intended to parse TeX.

Some of the known issues:
    * Currently it does not detect special symbols and many TeX escape
        sequences (more information: http://www.bibtex.org/SpecialSymbols/)
    * String concatinatins are not recognized. (e.g. "str1" # "str2")
    * Abbreviations are not supported (e.g. @string { foo = "Mrs. Foo" })
"""

from collections import defaultdict

import regex as regex

from commons import Name


# To remove Texts like {APA} from input.
WORDS_IN_BRACES_SUB = regex.compile(r'(?<!=\s*){([^\\{}\n]*)}').sub
FINDALL_BIBTEX_FIELDS = regex.compile(
    r'(\w+)\s*=\s*(?:[{"]\s*(.*?)\s*["}]|(\d+))'
).findall
TYPE_SEARCH = regex.compile('@(.*?)\s*\{', regex.IGNORECASE).search


def search_for_tag(bibtex: str) -> defaultdict:
    """Find all fields of the bibtex and return result as a defaultdict."""
    fs = FINDALL_BIBTEX_FIELDS(bibtex)
    return defaultdict(
        lambda: None, {f[0].lower(): f[1] if f[1] else f[2] for f in fs}
    )


def parse(bibtex):
    """Parse bibtex string and return a dictionary of information."""
    bibtex = special_sequence_cleanup(bibtex)
    d = search_for_tag(bibtex)
    # cite_type: book, journal, incollection, etc.
    m = TYPE_SEARCH(bibtex)
    if m:
        d['cite_type'] = m.group(1).strip().lower()
    # author
    author = d['author']
    if author:
        d['authors'] = names = []
        for author in author.split(' and '):
            if author.endswith(' and'):
                author = author[:-4]
            if not author:
                continue
            name = Name(author)
            names.append(name)
        del d['author']
    # editor, not tested, just a copy of author
    editor = d['editor']
    if editor:
        d['editors'] = names = []
        for editor in editor.split(' and '):
            if editor.endswith(' and'):
                editor = editor[:-4]
            if not editor:
                continue
            name = Name(editor)
            names.append(name)
        del d['editor']
    pages = d['pages']
    if pages:
        pages = d['pages'] = (
            pages.replace(' ', '').replace('--', '–').replace('-', '–')
        )
        startpage, sep, endpage = pages.partition('–')
        if sep:
            d['startpage'], d['endpage'] = startpage, endpage
    return d


def special_sequence_cleanup(bibtex):
    """Replace common TeX special symbol commands with their unicode value."""
    return WORDS_IN_BRACES_SUB(r'\g<1>', (
        bibtex
        .replace(r'{\textregistered}', '®')
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
    ))
