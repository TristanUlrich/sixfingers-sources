#!/usr/bin/env python3
"""
SIXFINGERS — do the two word guards still judge the same way?
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

    python3 tools/check-words.py

There are two readers of `tools/words.json`. `js/words.js` runs in the reader's
browser and decides what the site will print. `tools/words.py` runs here and
decides what the robot will say to a stranger, in public, under Tristan's name.

Written twice because they run in two places, which is precisely the shape of the
bug this project has already paid for twice: the browser learnt something the
python did not, and nothing was red until somebody looked. So neither of them is
the reference. `tools/words-cases.json` is, and both answer to it: this file holds
the python side to it, `tools/words-selftest.html` in the site holds the browser
side to the same table.

The table is not a list of insults. It is mostly a list of REAL NAMES that must
pass — Scunthorpe, Niger, Nigeria, Nègre, Kiké, Fagg — because a guard that
refuses somebody's actual name does far more harm than one that lets a word
through on a machine where nobody else will read it.

Exit code 0 means the python side answers the table correctly.
"""

import importlib.util
import json
import time as _time
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location('words', HERE / 'words.py')
words = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(words)


def main():
    table = HERE / 'words-cases.json'
    try:
        doc = json.loads(table.read_text(encoding='utf-8'))
    except Exception as e:
        print('the table itself cannot be read: %s' % e)
        return 2

    refuse = doc.get('must_refuse') or []
    review = doc.get('must_review') or []
    allow = doc.get('must_pass') or []
    mech = doc.get('machinery') or []
    if not refuse or not allow:
        print('the table is missing one of its halves, which cannot be right')
        return 2

    wrong, total = [], 0

    print('  these must be refused, however they are written')
    for name in refuse:
        total += 1
        got = words.check(name)
        if got and got['level'] == 'refuse':
            print('    ok      %-24s refused on the %s pass' % (json.dumps(name), got['pass']))
        elif got:
            wrong.append((name, 'was only held, and it is unambiguous enough to refuse'))
            print('    WRONG   %s was only held' % json.dumps(name))
        else:
            wrong.append((name, 'should have been refused, and was let through'))
            print('    WRONG   %s was let through' % json.dumps(name))

    print('  these must be HELD FOR A PERSON, not refused by a machine')
    for name in review:
        total += 1
        got = words.check(name)
        if got and got['level'] == 'review':
            print('    ok      %-26s held (%s pass)' % (json.dumps(name), got['pass']))
        elif got:
            wrong.append((name, 'was refused outright, and it should only be held'))
            print('    WRONG   %s was refused outright' % json.dumps(name))
        else:
            wrong.append((name, 'was let through, and it should be held'))
            print('    WRONG   %s was let through' % json.dumps(name))

    print('  these must pass: real names, and what people actually type')
    for name in allow:
        total += 1
        got = words.check(name)
        if not got:
            print('    ok      %s' % json.dumps(name))
        else:
            wrong.append((name, 'WRONGLY REFUSED on the %s pass. bare "%s", folded "%s"'
                          % (got['pass'], words.bare(name), words.folded(name))))
            print('    WRONG   %s was refused' % json.dumps(name))

    print('  the machinery itself')
    for case in mech:
        total += 1
        fn = words.bare if case.get('form') == 'bare' else words.folded
        got = fn(case.get('input', ''))
        if got == case.get('want'):
            print('    ok      %s' % case.get('why', ''))
        else:
            wrong.append((case.get('why', ''), 'wanted "%s", got "%s"' % (case.get('want'), got)))
            print('    WRONG   %s' % case.get('why', ''))

    # ----------------------------------------------------------------- the audit
    # The table above proves the guard answers THE WRITTEN CASES correctly. It does
    # not prove that an entry added one evening does anything at all: a misspelt
    # entry, or one shorter than its pass allows, sleeps in the list with nothing
    # red anywhere. That is exactly the family of failure that has cost this project
    # the most.
    print('  the list itself')
    data = words.load()
    for b in data['banned']:
        total += 1
        hit = words.check(b['w'])
        if not hit:
            wrong.append((b['w'], 'is in the list and catches nothing, not even itself'))
            print('    WRONG   an entry catches nothing, not even itself')
        elif b['match'] == 'anywhere' and ' ' not in b['w'] and len(words.bare(b['w'])) < 5:
            wrong.append((b['w'], 'is matched anywhere and is shorter than five letters'))
            print('    WRONG   an entry under five letters is matched anywhere')
        else:
            print('    ok      an entry catches itself (%s pass)' % hit['pass'])
    for s in data['script']:
        total += 1
        if words.check(s['w']):
            print('    ok      a non-latin entry catches itself')
        else:
            wrong.append((s['w'], 'non-latin entry catches nothing'))
            print('    WRONG   a non-latin entry catches nothing')
    for c in data['codes']:
        total += 1
        if words.check(c):
            print('    ok      a code catches itself')
        else:
            wrong.append((c, 'code catches nothing'))
            print('    WRONG   a code catches nothing')

    # ------------------------------------------------ the project's own vocabulary
    # A word list can be green on its own cases and still refuse half of a real text.
    # So it is run over EVERYTHING this repository says in public: the README, the
    # rules, the schema, the records. Zero refusals expected.
    print('  the repository\'s own public words')
    import re as _re
    seen_words, refused_here = set(), []
    for f in sorted(HERE.parent.glob('*.md')) + sorted((HERE.parent / 'sources').glob('*')):
        try:
            text = f.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        for w in _re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text):
            seen_words.add(w)
    for w in sorted(seen_words):
        if words.check(w):
            refused_here.append(w)
    total += 1
    if refused_here:
        wrong.append(('the repository\'s own text', 'the guard refuses %d of its own words: %s'
                      % (len(refused_here), ', '.join(refused_here[:6]))))
        print('    WRONG   the guard refuses %d words of this repository' % len(refused_here))
    else:
        print('    ok      %d distinct words in this repository, none refused' % len(seen_words))

    # ------------------------------------------------------------------ the cost
    start = _time.perf_counter()
    for _ in range(200):
        words.check('Deliberate, a machine that draws')
    each = (_time.perf_counter() - start) / 200 * 1000
    print('  the cost')
    print('    ok      %.2f ms for one ordinary sentence, %d entries, %d lookalikes'
          % (each, len(data['banned']), len(data['confusables'])))

    print()
    if not wrong:
        print('%d of %d: the python side of the word guard agrees with the table,' % (total, total))
        print('and every entry in the list catches at least itself.')
        print('Open /tools/words-selftest.html in the site to hold the browser side')
        print('to the same table.')
        return 0

    print('%d of %d cases came out wrong.' % (len(wrong), total))
    for what, why in wrong:
        print('  %s: %s' % (json.dumps(what) if isinstance(what, str) else what, why))
    print()
    print('A name wrongly refused is the serious half of this table. Do not fix it')
    print('by editing the table.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
