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
        if got:
            print('    ok      %-24s refused on the %s pass' % (json.dumps(name), got['pass']))
        else:
            wrong.append((name, 'should have been refused, and was let through'))
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

    print()
    if not wrong:
        print('%d of %d: the python side of the word guard agrees with the table.' % (total, total))
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
