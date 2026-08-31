#!/usr/bin/env python3
"""
SIXFINGERS — the word guard, python side.
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

This is the SECOND reader of `tools/words.json`. The first is `js/words.js` in the
site. THE LIST ITSELF IS NOT IN THIS FILE, and that is the whole point: two lists
kept in parallel always end up disagreeing, and this project has already paid for
that once, when the browser learned to read a record the checker could not.

    python3 tools/words.py "some name"        # says whether it would be refused

WHAT IT IS FOR, AND WHAT IT IS NOT

It is not moderation and it does not judge anybody. It stops the project from
printing, in its own chrome or under its own robot's name, a racist word or a call
to hatred. A word gets on the list only if it is all three of:

  1. unambiguously a racist insult, a call to hatred, or a nazi slogan. Not
     "rude", not "coarse", nothing merely sexual;
  2. NOT a surname, a first name, a place, a demonym, or an ordinary French or
     English word;
  3. at least five letters once folded.

The rule that matters most is the second one. A badly made list blocks real
people's names and lets everything else through: the textbook case is the town of
Scunthorpe. Missing things is the intended setting, not an oversight.

THE TWO PASSES, AND WHY THERE ARE TWO

The bare form is lower case, without accents, with digits put back as letters
(0 to o, 1 to i, 3 to e ...) and everything that is not a letter removed, so
spaces, dots, dashes and underscores hide nothing. Repeats are KEPT.

The folded form collapses repeated letters, to catch "niiiggger". And that is
where the trap is: folding makes the English insult and the country Niger land on
exactly the same string. So the folded pass only refuses when the bare form does
not contain one of the rendered words (niger, nigeria, nigel ...). The bare pass
takes no notice of them: the word spelled out in full is refused, country or no
country.
"""

import json
import os
import sys
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
_LIST = os.path.join(_HERE, 'words.json')

_cache = None


def load(path=_LIST):
    """The list, read from disk once. Nothing here is written in this file."""
    global _cache
    if _cache is None or path != _LIST:
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
        data = {
            'leet': dict(raw.get('leet') or {}),
            'banned': [str(w) for w in (raw.get('banned') or [])],
            'allowed': [str(w) for w in (raw.get('allowed') or [])],
        }
        if path != _LIST:
            return data
        _cache = data
    return _cache


def bare(name, data=None):
    """Lower case, no accents, digits back to letters, letters only. Repeats kept."""
    data = data or load()
    s = str(name or '').lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')
    for ch, rep in data['leet'].items():
        s = s.replace(ch, rep)
    return ''.join(c for c in s if 'a' <= c <= 'z')


def folded(name, data=None):
    """The bare form with runs of the same letter collapsed to one."""
    out = []
    for c in bare(name, data):
        if not out or out[-1] != c:
            out.append(c)
    return ''.join(out)


def check(name, data=None):
    """None when there is nothing to refuse, which is almost always.

    Otherwise {'pass': 'bare'} or {'pass': 'folded'} — which pass caught it, never
    which word. The word is not repeated back: printing it in the project's own
    voice is the thing being avoided.
    """
    data = data or load()
    raw = bare(name, data)
    if not raw:
        return None
    if any(w in raw for w in data['banned']):
        return {'pass': 'bare'}
    if any(ok in raw for ok in data['allowed']):
        return None
    fold = folded(name, data)
    if any(folded(w, data) in fold for w in data['banned']):
        return {'pass': 'folded'}
    return None


REFUSAL = (
    'Not that one. This site will not print a racist word or a call to hatred in '
    'its own chrome, even on a computer where nobody else will ever read it. '
    'Anything else is fine.'
)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    worst = 0
    for name in argv[1:]:
        hit = check(name)
        print('%s %s' % ('refused' if hit else 'fine   ', name))
        if hit:
            worst = 1
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
