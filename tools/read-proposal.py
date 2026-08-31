#!/usr/bin/env python3
"""
SIXFINGERS — read a proposal written in the issue form, and answer it.
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

    python3 tools/read-proposal.py --body-file body.md --title "source: x" \
                                   --author someone

Prints one Markdown comment on standard output. Exit code 0 when the record
passes, 1 when it is refused, 2 when there is nothing usable to read.

WHY THIS EXISTS

`check-sources.yml` runs on FILES. Somebody who fills in the issue form has not
sent a file, so until now nobody answered them at all: they wrote into the void and
waited for Tristan to walk past. That is the widest hole left in the front door, and
this closes it. The same rules, the same words, one minute later, in public.

THE THREE RULES THIS FILE OBEYS, AND THEY ARE NOT STYLE

1. **Nothing a stranger wrote is ever printed back as Markdown.** Everything that
   came from the proposal goes inside a fenced block, with fences neutralised and
   lengths capped. A comment written by this robot must not be able to mention
   anybody, link anywhere, or pretend to be a decision.
2. **Nothing is executed, ever.** The proposal is read as data by `json.loads` and
   judged by `check_source.validate_any`. There is no eval, no import of anything
   the proposal names, and no request made to any address it carries.
3. **The word guard runs before the record is described.** If a proposal carries a
   racist word or a call to hatred, the answer says so in one line and repeats
   none of it. Tristan should not have to read the insult to know it arrived.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import words                                    # noqa: E402  the shared list
from importlib import util as _util             # noqa: E402

_spec = _util.spec_from_file_location(
    'check_source', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'check-source.py'))
check_source = _util.module_from_spec(_spec)
_spec.loader.exec_module(check_source)

MARKER = '<!-- sixfingers: proposal checker -->'

# The heading GitHub renders for each field of `.github/ISSUE_TEMPLATE/new-source.yml`.
# Matched on the label, because that is what ends up in the body: the field ids are
# not written anywhere in it.
FIELD = {
    'name': 'What is it called',
    'model': 'The model name, exactly as the Horde writes it',
    'set': 'The short title printed on the folder',
    'what': 'What does it actually do to a picture',
    'good': 'What is it worth using for',
    'note': 'One line, in passing',
    'home': 'A page about it',
    'colour': 'The colour of your folder',
    'secs': 'How long six pictures took, in seconds',
    'on': 'The day you measured that',
    'json': 'The source, as JSON',
    'checker': 'What the checker said',
    'rules': 'Please confirm',
    'anything': 'Anything else worth knowing',
}

MAX_BODY = 64 * 1024        # a proposal longer than this is not a proposal
MAX_QUOTE = 2000            # of a stranger's text, at most this much is echoed
MAX_LINES = 40              # and at most this many lines of reasons


def sections(body):
    """The issue form, split back into its fields.

    GitHub renders a form as `### Label`, a blank line, then the answer. An
    untouched optional field renders as `_No response_`.
    """
    out, key, buf = {}, None, []
    for line in (body or '').splitlines():
        if line.startswith('### '):
            if key is not None:
                out[key] = '\n'.join(buf).strip()
            key, buf = line[4:].strip(), []
        elif key is not None:
            buf.append(line)
    if key is not None:
        out[key] = '\n'.join(buf).strip()
    for k, v in list(out.items()):
        if v.strip() == '_No response_':
            out[k] = ''
    return out


def unfence(text):
    """The contents of the first fenced block, or the text itself if there is none."""
    m = re.search(r'^```[^\n]*\n(.*?)^```', text or '', re.S | re.M)
    return m.group(1) if m else (text or '')


def safe(text, limit=MAX_QUOTE):
    """A stranger's text, made safe to put inside a fenced block.

    Backticks are neutralised so nothing can close the fence and start writing
    Markdown; control characters go; the length is capped. This is the only route
    by which anything from a proposal reaches the answer.
    """
    t = str(text or '')
    t = ''.join(c for c in t if c in '\n\t' or ord(c) >= 32)
    t = t.replace('`', "'")
    if len(t) > limit:
        t = t[:limit] + '\n... (cut here)'
    return t


def ticked(text):
    """The confirmation checkboxes: how many are ticked, out of how many."""
    boxes = re.findall(r'^\s*- \[([ xX])\]', text or '', re.M)
    return sum(1 for b in boxes if b in 'xX'), len(boxes)


def known_ids(folder):
    out = []
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return out
    for n in names:
        if not n.endswith('.json'):
            continue
        try:
            with open(os.path.join(folder, n), encoding='utf-8') as f:
                raw = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(raw, dict) and isinstance(raw.get('id'), str):
            out.append(raw['id'])
    return out


def slug(name):
    """An id built from a name: lower case, dashes, nothing exotic.

    Nobody should have to invent an identifier to say that a model is good. If two
    people land on the same one, the duplicate check further down says so by name,
    which is a far better conversation than asking a stranger to guess a free slot.
    """
    out = []
    for ch in (name or '').lower():
        out.append(ch if ch.isascii() and ch.isalnum() else '-')
    s = re.sub(r'-+', '-', ''.join(out)).strip('-')[:32].strip('-')
    return s if len(s) >= 3 else None


def from_fields(got):
    """A record built from the form's own boxes, for people who never write JSON.

    THE POINT: asking a stranger to hand-write a JSON file, get the commas right,
    and invent an id, in order to say "this model is worth your time", is asking
    for the wrong thing. The judgement is the contribution; the file is clerical
    work, and clerical work is what a machine is for.

    NOTHING IS INVENTED HERE. Every value comes from a box the person filled in.
    An empty box means the field is left out, never guessed, and the measurement
    is only carried when BOTH the number and the day it was taken are given —
    a duration with no date is exactly the kind of number this project refuses to
    print.

    Returns None when there is not enough to build anything, so the caller can say
    so plainly instead of judging a half-record.
    """
    name = (got.get(FIELD['name']) or '').strip()
    model = (got.get(FIELD['model']) or '').strip()
    if not name or not model:
        return None
    sid = slug(name)
    if not sid:
        return None

    rec = {'spec': 1, 'kind': 'horde', 'id': sid, 'name': name,
           'set': (got.get(FIELD['set']) or '').strip() or name,
           'model': model}

    for key, field in (('note', 'note'), ('what', 'what'), ('good', 'good'),
                       ('home', 'home')):
        v = (got.get(FIELD[field]) or '').strip()
        if v:
            rec[key] = v

    colour = (got.get(FIELD['colour']) or '').strip()
    if colour:
        # Written as it was written. A colour that is not a colour is refused by
        # the rules, with the reason, rather than quietly dropped here.
        rec['colour'] = colour

    secs = (got.get(FIELD['secs']) or '').strip().replace(',', '.')
    on = (got.get(FIELD['on']) or '').strip()
    if secs and on:
        try:
            rec['measured'] = {'on': on, 'pack_seconds': float(secs)}
        except ValueError:
            rec['measured'] = {'on': on, 'pack_seconds': secs}
    elif secs or on:
        rec['_half_measure'] = True

    return rec


def guard(fields):
    """The word guard, over every piece of text a human wrote.

    Returns the NAME of the field it caught, never the word. Nothing about the
    word travels any further than this function.
    """
    for label, value in fields:
        if value and words.check(value):
            return label
    return None


def answer(body, title='', author='', folder='sources'):
    """The whole verdict: (markdown comment, exit code)."""
    lines = []
    say = lines.append

    if body and len(body) > MAX_BODY:
        say('This proposal is too long to read. A source record is a few lines of '
            'JSON; if something else is pasted in with it, please take it out and '
            'edit the issue.')
        return '\n'.join(lines), 2

    got = sections(body)
    raw_json = unfence(got.get(FIELD['json'], ''))

    hit = guard([
        ('the title', title),
        ('the name', got.get(FIELD['name'], '')),
        ('the description', got.get(FIELD['what'], '')),
        ('the notes', got.get(FIELD['anything'], '')),
        ('the record itself', raw_json),
        ('the account it was sent from', author),
    ])
    if hit:
        say('This one is not going any further, and it has not been read past %s.'
            % hit)
        say('')
        say('SIXFINGERS does not print a racist word or a call to hatred, not in '
            'the site and not under this robot. Nothing here is repeated back.')
        return '\n'.join(lines), 1

    if not got:
        say('This does not look like it came from the proposal form, so there is '
            'nothing here for the checker to read.')
        say('')
        say('If you meant to propose a picture machine, please open [a New source '
            'issue](../../issues/new?template=new-source.yml). If you meant '
            'something else, ignore this: Tristan reads every issue himself.')
        return '\n'.join(lines), 2

    built = None
    half_measure = False
    if not raw_json.strip():
        built = from_fields(got)
        if built is None:
            say('There is not enough here to build a record yet.')
            say('')
            say('The two boxes it cannot do without are **What is it called** and '
                '**The model name, exactly as the Horde writes it**. Fill those in '
                'and the rest is built for you.')
            say('')
            say('If the machine is not on the AI Horde at all, then it needs its '
                'own address, and that shape has to be written by hand: see '
                '[`sources/SCHEMA.md`](../blob/main/sources/SCHEMA.md) and paste it '
                'into **The source, as JSON**.')
            say('')
            say('**Editing this issue makes the checker look again**, straight '
                'away.')
            return '\n'.join(lines), 2
        half_measure = bool(built.pop('_half_measure', False))

    try:
        record = built if built is not None else json.loads(raw_json)
    except ValueError as e:
        say('That is not valid JSON yet, so the checker stopped before the rules.')
        say('')
        say('```text')
        say(safe(str(e), 300))
        say('```')
        say('')
        say('A missing comma or a stray quote is usually all it is. Run '
            '`python3 tools/check-source.py` on the file before pasting it, and '
            'edit this issue when it is fixed.')
        return '\n'.join(lines), 1

    # `finish` EST RETIRÉ ICI, ET PAS SEULEMENT SIGNALÉ. Le dire sans le faire
    # serait une promesse tenue par une intervention à la main, c'est à dire pas
    # tenue du tout. Le robot enlève donc le champ lui-même, et ce qu'il réimprime
    # plus bas est exactement ce qui a été jugé.
    had_finish = isinstance(record, dict) and 'finish' in record
    if had_finish:
        record.pop('finish', None)

    taken = known_ids(folder)
    errors = list(check_source.validate_any(record, taken=taken))

    # A record naming a Horde model carries no address, so the rules that judge it
    # have nothing to compare and take no list of what is already on the shelf.
    # Both sides are the same here, which is why this is not a divergence: the
    # site's own door (`js/main.js`) refuses the duplicate itself, right after the
    # rules have passed. The robot has to do the same, or the same machine can be
    # proposed twice and told both times that it passes.
    if (isinstance(record, dict) and record.get('kind') == 'horde'
            and isinstance(record.get('id'), str) and record['id'] in taken):
        errors.append('there is already a source called %s' % record['id'])

    sid = record.get('id') if isinstance(record, dict) else None
    sid = sid if isinstance(sid, str) and re.match(r'^[a-z0-9-]{1,32}$', sid) else None

    if errors:
        say('The checker refused this record. Every reason is below, in its own '
            'words:')
        say('')
        say('```text')
        for e in errors[:MAX_LINES]:
            say(safe(e, 200).replace('\n', ' '))
        if len(errors) > MAX_LINES:
            say('... and %d more' % (len(errors) - MAX_LINES))
        say('```')
        say('')
        say('These are the same rules the site itself applies, so a record that '
            'passes `python3 tools/check-source.py` here will be accepted there. '
            '**Edit this issue and the checker looks again**, so nobody has to '
            'reopen anything.')
        say('')
        say('Two of the refusals are worth knowing on sight: a machine that needs '
            'a key, a token, an account or a payment is not eligible at all, and '
            'neither is one on your own machine or your home network. See '
            '[CONTRIBUTING.md](../blob/main/CONTRIBUTING.md).')
        return '\n'.join(lines), 1

    say('The checker read this record and it passes%s.'
        % (' (`%s`)' % sid if sid else ''))
    say('')
    say(('Nothing here was written by hand: this is the record built from your '
         'answers, and it is exactly what was judged.') if built is not None else
        'This is the record as it was judged, and as it would go on the shelf.')
    say('')
    say('```json')
    say(safe(json.dumps(record, indent=2, ensure_ascii=False), 1800))
    say('```')
    say('')
    if had_finish:
        say('One difference from what was sent, and it is not a refusal: '
            '**`finish` is reserved** for the machines this project publishes '
            'itself, so it has been taken out of the record above. It is the one '
            'thing the shelf keeps for the house, and it is how anybody can tell '
            'at a glance which machines are ours. Your `colour` is untouched, and '
            'the colour is what carries at every size.')
        say('')
    if half_measure:
        say('One box is half filled: a duration needs the day it was taken, and a '
            'day needs the duration. **The site never prints a number nobody '
            'took**, so with only one of the two the measurement is left out '
            'altogether. Fill in both, or neither.')
        say('')
    say('That means it breaks none of the rules a machine has to meet. It does '
        'not mean it is on the shelf: Tristan reads every proposal himself, and '
        'a record that passes every check is still not a machine that answers. '
        'Nothing ships that has not answered.')

    done, total = ticked(got.get(FIELD['rules'], ''))
    if total and done < total:
        say('')
        say('One thing first: %d of the %d confirmations is not ticked. Please '
            'tick it, or say here why it does not apply.' % (total - done, total))

    if not (got.get(FIELD['what']) or '').strip():
        say('')
        say('It would also help to say what the machine actually does to a '
            'picture: what comes back, not what it advertises.')

    say('')
    say('And you do not have to wait for any of this to use it: **the record '
        'above** works right now in your own browser, in **Community, Add a '
        'machine**. Copy it, paste it there, and the machine is on your own shelf '
        'straight away. It stays in that browser and affects nobody but you.')
    return '\n'.join(lines), 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--body-file', help='the issue body, as a file. Default: stdin')
    p.add_argument('--title', default='')
    p.add_argument('--author', default='')
    p.add_argument('--sources', default='sources',
                   help='the folder of records already on the shelf')
    a = p.parse_args(argv)

    body = (open(a.body_file, encoding='utf-8').read() if a.body_file
            else sys.stdin.read())

    text, code = answer(body, title=a.title, author=a.author, folder=a.sources)
    print(MARKER)
    print(text)
    print('')
    print('*This is the checker, and it runs on every proposal before a human '
          'reads one. It judges the record, never the person. If it is wrong, say '
          'so here: it is a small python file in this repository and it has been '
          'wrong before.*')
    return code


if __name__ == '__main__':
    sys.exit(main())
