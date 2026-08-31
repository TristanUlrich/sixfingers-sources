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
to hatred. It is NOT a profanity filter: ordinary swearing is deliberately let
through. The admission rules for the list are written in `tools/words.json`
itself, next to the list they govern, along with the words that were considered
and kept out, and why.

THE SIX PASSES, AND WHY THERE ARE SIX

Everything starts from three views of the same text.

  * the BARE form: compatibility-normalised (so fancy unicode letters become
    ordinary ones), lower case, without accents, with lookalike letters from other
    alphabets mapped back to latin, with digits put back as letters, and then
    everything that is not a letter removed. Repeats are KEPT.
  * the FOLDED form: the bare form with runs of one letter collapsed, to catch
    "niiiggger".
  * the SCRIPT form: the same text with its own alphabet left alone, for words
    that are not written in latin at all.

  1. bare, anywhere      a single word appears anywhere in the bare form
  2. folded, anywhere    same on the folded form, and only for entries of five
                         letters or more, and only when no rendered word explains
                         the collision. Folding makes the English insult and the
                         country Niger land on the same string; that is what the
                         `allowed` list is for.
  3. word                the entry must be a WHOLE word. Reserved for short
                         entries and for words that are also ordinary English, so
                         that raccoon, Pakistan and a gearbox are left alone.
  4. slogan              an entry written with spaces is matched against whole
                         words in a row, so race war is caught and race warmup is
                         not.
  5. script              a substring of the non-latin form, for Cyrillic and the
                         like.
  6. code                a numeric hate code, matched as a whole token and never
                         as a substring, because 88 sits inside a great many
                         perfectly ordinary numbers.

WHAT IS DELIBERATELY NOT DONE: fuzzy matching. Edit distance one from the English
insult includes bigger, digger and trigger. Every pass here is aimed at DELIBERATE
disguise, never at a typo, and that is why none of them guesses.
"""

import json
import os
import sys
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))
_LIST = os.path.join(_HERE, 'words.json')

_cache = {}

_MIN_FOLD = 5          # below this, the folded pass catches too many ordinary words


def load(path=_LIST):
    """The list, read from disk once. Nothing here is written in this file."""
    if path not in _cache:
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
        entries = []
        for item in raw.get('banned') or []:
            if isinstance(item, str):           # spec 1, kept so nothing breaks
                item = {'w': item, 'match': 'anywhere'}
            entries.append({
                'w': str(item.get('w') or ''),
                'match': 'word' if item.get('match') == 'word' else 'anywhere',
                'kind': str(item.get('kind') or 'hate'),
                'lang': str(item.get('lang') or ''),
                'level': 'review' if item.get('level') == 'review' else 'refuse',
                'id': str(item.get('id') or ''),
            })
        _cache[path] = {
            'leet': dict(raw.get('leet') or {}),
            'confusables': dict(raw.get('confusables') or {}),
            'banned': entries,
            # THE ENTRIES ARE NORMALISED LIKE THE TEXT, OR THEY ARE NEVER FOUND.
            # Measured on 31 August 2026: one Cyrillic entry carries a breve, which
            # decomposition strips from the text but not from the list, so the entry
            # was doing nothing and nothing said so.
            'script': [{'w': script(s.get('w') or ''), 'kind': str(s.get('kind') or 'hate'),
                        'level': 'review' if s.get('level') == 'review' else 'refuse',
                        'id': str(s.get('id') or '')}
                       for s in (raw.get('script') or [])],
            'codes': [{'w': str(c.get('w') if isinstance(c, dict) else c).lower(),
                       'kind': str(c.get('kind') if isinstance(c, dict) else 'nazi'),
                       'level': ('review' if isinstance(c, dict) and c.get('level') == 'review'
                                 else 'refuse'),
                       'id': str(c.get('id') if isinstance(c, dict) else '')}
                      for c in (raw.get('codes') or [])],
            'allowed': [str(w) for w in (raw.get('allowed') or [])],
        }
    return _cache[path]


def _plain(text):
    """Compatibility-normalised, lower case, accents removed. Common to every view."""
    s = unicodedata.normalize('NFKC', str(text or '')).lower()
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')
    return s


def bare(name, data=None):
    """Letters only, lookalikes mapped back, digits put back as letters. Repeats kept."""
    data = data or load()
    s = _plain(name)
    s = ''.join(data['confusables'].get(c, c) for c in s)
    s = ''.join(data['leet'].get(c, c) for c in s)
    return ''.join(c for c in s if 'a' <= c <= 'z')


def folded(name, data=None):
    """The bare form with runs of the same letter collapsed to one."""
    out = []
    for c in bare(name, data):
        if not out or out[-1] != c:
            out.append(c)
    return ''.join(out)


def script(name):
    """The text with its own alphabet left alone: letters of any script, nothing else."""
    return ''.join(c for c in _plain(name) if unicodedata.category(c).startswith('L'))


def tokens(name):
    """The whole words of the text, as typed, before any substitution.

    A word is a run of letters or digits IN ANY SCRIPT, so a regular expression
    written for latin would cut Cyrillic into pieces. Everything else is a
    separator, which is why b.e.a.n.e.r is six words here and one in the bare form.
    """
    out, buf = [], []
    for c in _plain(name):
        if unicodedata.category(c)[0] in 'LN':
            buf.append(c)
        elif buf:
            out.append(''.join(buf))
            buf = []
    if buf:
        out.append(''.join(buf))
    return out


def joined(name, data=None):
    """The words of the text, normalised and glued together, with the seams kept.

    Returns (text, seams). `seams` holds every offset in `text` where a word starts
    or ends, which is how a SLOGAN is matched: it must begin at a seam and end at a
    seam. Without that, race war would be found inside race warmup, and sale negre
    inside wholesale negrete.
    """
    data = data or load()
    out, seams, at = [], {0}, 0
    for t in tokens(name):
        b = bare(t, data)
        if not b:
            continue
        out.append(b)
        at += len(b)
        seams.add(at)
    return ''.join(out), seams


def _slogan_hit(text, seams, needle):
    """Is `needle` in `text`, starting and ending on a seam?"""
    at = text.find(needle)
    while at != -1:
        if at in seams and (at + len(needle)) in seams:
            return True
        at = text.find(needle, at + 1)
    return False


def _verdict(which, entry):
    """The verdict, and NEVER the word that was found.

    `level` is 'refuse' when the entry is unambiguous, and 'review' when it collides
    with something ordinary and a person has to decide. `id` names the entry without
    reprinting it, for a log or a label.
    """
    return {'pass': which, 'kind': entry['kind'], 'level': entry['level'],
            'id': entry.get('id', '')}


MAX_TEXT = 4096          # past this only the beginning is looked at: see check()


def check(name, data=None):
    """None when there is nothing to refuse, which is almost always.

    Otherwise {'pass': ..., 'kind': ...} — which pass caught it and what family of
    thing it was, never which word. The word is not repeated back: printing it in
    the project's own voice is the thing being avoided.
    """
    data = data or load()
    # A CEILING BEFORE ANY WORK. Normalising a megabyte of text is expensive, and
    # a name field or a record has no reason to be that long. What is past the
    # ceiling is not judged: the length limits elsewhere are what refuse it.
    name = str(name or '')[:MAX_TEXT]
    raw = bare(name, data)
    fold = folded(name, data)
    excused = any(ok in raw for ok in data['allowed'])
    glued, seams = joined(name, data)

    for b in data['banned']:
        if b['match'] != 'anywhere':
            continue
        bw = bare(b['w'], data)
        if not bw:
            continue
        if ' ' in b['w']:
            # a slogan: whole words in a row, never a piece of a word
            if _slogan_hit(glued, seams, bw):
                return _verdict('slogan', b)
            continue
        if bw in raw:
            return _verdict('bare', b)
        fw = folded(b['w'], data)
        if len(fw) >= _MIN_FOLD and not excused and fw in fold:
            return _verdict('folded', b)

    toks = tokens(name)
    if toks:
        bares = [bare(t, data) for t in toks]
        folds = [folded(t, data) for t in toks]
        for b in data['banned']:
            if b['match'] != 'word':
                continue
            bw = bare(b['w'], data)
            fw = folded(b['w'], data)
            if not bw:
                continue
            for i, tb in enumerate(bares):
                if tb == bw:
                    return _verdict('word', b)
                if len(bw) >= _MIN_FOLD and folds[i] == fw and not any(
                        ok in tb for ok in data['allowed']):
                    return _verdict('word', b)

        # CODES ARE MATCHED LIKE SLOGANS. 14/88 and 14 88 are two words, 1488 is
        # one, and all three must count the same. The digits are therefore glued
        # back together with the seams kept: the code has to start and end on one,
        # which leaves 14880 and 31488 alone.
        digits, seams, at = [], {0}, 0
        for tk in toks:
            if tk.isdigit():
                digits.append(tk)
                at += len(tk)
                seams.add(at)
            else:
                # a word that is not a number breaks the run of digits, and a seam
                # has to be laid there too, or "gamer 1488" walks straight past
                digits.append('\x00')
                at += 1
                seams.add(at)
        glued_digits = ''.join(digits)
        for code in data['codes']:
            flat = ''.join(c for c in code['w'] if c.isdigit())
            if flat and _slogan_hit(glued_digits, seams, flat):
                return _verdict('code', code)

    if data['script']:
        sc = script(name)
        if sc:
            for s in data['script']:
                if s['w'] and s['w'] in sc:
                    return _verdict('script', s)

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
        print('%-8s %s%s' % (hit['level'] if hit else 'fine', name,
                             '  (%s pass, %s, %s)' % (hit['pass'], hit['kind'], hit['id'])
                             if hit else ''))
        if hit:
            worst = 1
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
