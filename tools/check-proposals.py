#!/usr/bin/env python3
"""
SIXFINGERS — does the proposal robot still answer the way the table says?
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

    python3 tools/check-proposals.py

`tools/read-proposal.py` is the first thing a stranger meets: it reads what they
filled in and answers them, in public, under the project's name. So it is held to a
written table, `tools/proposal-cases.json`, exactly as the two validators are held
to `tools/cases.json`. Nobody has to trust that the robot is polite and careful; it
is checked, on every push.

Two things are checked on EVERY case, whatever it is about, because they are the
two ways this robot could do real harm:

  * **it never prints a word from the list**, however the proposal was written. A
    robot that repeats an insult back has published it under Tristan's name;
  * **every fence it opens, it closes.** Everything a stranger wrote goes inside a
    fenced block. If one could be broken out of, a proposal could make the robot
    appear to say something it never said.

Exit code 0 means every case came out the way the table says it must.
"""

import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load(name, as_name):
    spec = importlib.util.spec_from_file_location(as_name, HERE / name)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(HERE))
    spec.loader.exec_module(mod)
    return mod


robot = load('read-proposal.py', 'read_proposal')
words = load('words.py', 'words')


def fences_balanced(text):
    return sum(1 for line in text.splitlines() if line.startswith('```')) % 2 == 0


def main():
    table = HERE / 'proposal-cases.json'
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
        why = case.get('why', 'case %d' % i)
        want = case.get('want') or {}
        body = case.get('body')
        if body is None and isinstance(case.get('body_repeat'), dict):
            # One character repeated, rather than 64 kB of it written out. A table
            # nobody can read is a table nobody checks.
            rep = case['body_repeat']
            body = str(rep.get('of', 'x')) * int(rep.get('times', 0))
        body = '\n'.join(body) if isinstance(body, list) else str(body or '')

        reply, code = robot.answer(body,
                                   title=case.get('title', ''),
                                   author=case.get('author', ''),
                                   folder=str(HERE.parent / 'sources'))
        low = reply.lower()

        faults = []
        if code != want.get('code'):
            faults.append('wanted exit %s, got %s' % (want.get('code'), code))
        for needle in want.get('contains') or []:
            if needle.lower() not in low:
                faults.append('the reply never says "%s"' % needle)
        for needle in want.get('absent') or []:
            if needle.lower() in low:
                faults.append('the reply says "%s", and it must not' % needle)

        # The two rules that hold on every case, table or no table.
        if words.check(reply):
            faults.append('THE REPLY CARRIES A WORD FROM THE LIST')
        if not fences_balanced(reply):
            faults.append('a fence is left open, so a proposal can write Markdown')

        if faults:
            wrong.append((why, faults, reply))
            print('  WRONG   %s' % why)
        else:
            print('  ok      %s' % why)

    print()
    if not wrong:
        print('%d of %d cases: the robot answers the way the table says.'
              % (len(cases), len(cases)))
        return 0

    print('%d of %d cases came out wrong.' % (len(wrong), len(cases)))
    for why, faults, reply in wrong:
        print()
        print('  %s' % why)
        for f in faults:
            print('    - %s' % f)
        print('    what it actually replied:')
        for line in reply.splitlines()[:12]:
            print('      | %s' % line)
    print()
    print('Either the robot is wrong, or the table is. Do not fix this by editing')
    print('the table until you are sure the robot is the thing that is right.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
