#!/usr/bin/env python3
"""
SIXFINGERS — do the two validators still agree?
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

    python3 tools/check-cases.py

There are two rule sets. `js/sources.js` runs in the reader's browser and is the
one that actually decides what the site will use. `tools/check-source.py` runs
here, on GitHub, and is the one a stranger meets when they propose something.

They are written twice because they run in two places, and on 25 August 2026 they
drifted apart without a sound: the browser learnt to read a record naming a model
on the AI Horde, GitHub did not, and so the only real entry in the shelf was being
refused by the machine that is supposed to welcome it. Nothing was red until
somebody looked.

So neither of them is the reference any more. `tools/cases.json` is — one written
table of records and whether each must be let in. This script proves the python
side answers it correctly. `tools/agree-selftest.html`, inside the site, proves
the browser side answers the same table the same way. Change a rule and this file
turns red until the table and both sides say the same thing again.

Exit code 0 means every case came out the way the table says it must.
"""

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

# `check-source.py` carries a dash in its name, so it is loaded by path rather
# than imported. It stays the single copy of the rules: this script never
# restates one, it only asks.
_spec = importlib.util.spec_from_file_location('check_source', HERE / 'check-source.py')
_rules = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_rules)
validate_any = _rules.validate_any


def main():
    table = HERE / 'cases.json'
    try:
        doc = json.loads(table.read_text(encoding='utf-8'))
    except Exception as e:
        print('the table itself cannot be read: %s' % e)
        return 2

    cases = doc.get('cases') or []
    if not cases:
        print('the table is empty, which cannot be right')
        return 2

    wrong = []
    for i, case in enumerate(cases):
        want = case.get('want')
        why = case.get('why', '')
        if want not in ('accept', 'refuse'):
            print('case %d says neither accept nor refuse' % i)
            return 2
        errors = validate_any(case.get('record'))
        got = 'refuse' if errors else 'accept'
        if got == want:
            print('  ok      %-8s %s' % (want, why))
        else:
            wrong.append((why, want, got, errors))
            print('  WRONG   wanted %s, got %s: %s' % (want, got, why))

    print()
    if not wrong:
        print('%d of %d cases: the python side agrees with the table.' % (len(cases), len(cases)))
        print('Open /tools/agree-selftest.html in the site to hold the browser')
        print('side to the same table.')
        return 0

    print('%d of %d cases came out the wrong way.' % (len(wrong), len(cases)))
    print()
    for why, want, got, errors in wrong:
        print('  %s' % why)
        print('    wanted: %s' % want)
        print('    got:    %s' % got)
        for e in errors:
            print('      - %s' % e)
    print()
    print('Either the rule is wrong, or the table is. Do not fix this by editing')
    print('the table until you are sure the rule is the thing that is right.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
