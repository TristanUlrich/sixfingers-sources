#!/usr/bin/env python3
"""
SIXFINGERS — check a community source before it goes anywhere near the site.
Copyright (c) 2026 Tristan Ulrich. All rights reserved.

    python3 tools/check-source.py sources/my-source.json
    python3 tools/check-source.py sources/*.json

Applies the same refusals as js/sources.js in the site. No dependencies: it runs
on the python3 that comes with macOS and with every Linux.

Exit code 0 means every file passed. Anything else means at least one did not, and
every reason is printed in plain words.

If you change a rule here, change it in js/sources.js too, and run the site's own
self-test at /tools/source-selftest.html. Two rule sets that disagree are worse
than one, because the one people check is not the one that runs.
"""

import json
import re
import sys
import unicodedata
from urllib.parse import urlsplit

LIMITS = {
    'manifestBytes': 8 * 1024,
    'idLen': 32, 'nameLen': 40, 'setLen': 24, 'noteLen': 120, 'whatLen': 400,
    'templateNodes': 64, 'pathDepth': 6,
    'minTimeout': 5000, 'maxTimeout': 180000,
    'minSide': 128, 'maxSide': 1024,
}

PLACEHOLDERS = {'prompt', 'width', 'height', 'n', 'seed'}

HEADERS_ALLOWED = {
    'content-type': {'application/json'},
    'accept': {'application/json', 'image/png', 'image/jpeg', 'image/webp', '*/*'},
}

KINDS = {'binary', 'json-base64', 'json-url'}

TOP_KEYS = {'spec', 'id', 'name', 'set', 'note', 'what', 'home', 'endpoint',
            'method', 'headers', 'body', 'query', 'response', 'size', 'count',
            'timeoutMs', 'colour'}

PRIVATE_HOST = [
    r'^localhost$', r'\.localhost$', r'^127\.', r'^0\.', r'^10\.',
    r'^192\.168\.', r'^172\.(1[6-9]|2\d|3[01])\.', r'^169\.254\.',
    r'^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.',
    r'^\[?::1\]?$', r'^\[?fc', r'^\[?fd', r'^\[?fe80',
    r'\.local$', r'\.internal$', r'\.home$', r'\.lan$',
]

INVISIBLE = re.compile('[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\ufeff]')

SOLE = re.compile(r'^\{(\w+)\}$')
ANY_BRACE = re.compile(r'\{[^}]*\}')


def clean(s, max_len):
    """Text made safe to look at. Returns None if nothing survives."""
    if not isinstance(s, str):
        return None
    t = unicodedata.normalize('NFC', s)
    t = INVISIBLE.sub('', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if not t:
        return None
    return t[:max_len]


def check_url(raw, allow_query=False):
    try:
        u = urlsplit(str(raw))
    except ValueError:
        return 'that is not an address'
    if u.scheme != 'https':
        return 'the address must start with https'
    if u.username or u.password:
        return 'the address must not carry a name or a password'
    host = (u.hostname or '')
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', host) or str(raw).split('//')[-1].startswith('['):
        return 'the address must be a name, not a numbered address'
    for pat in PRIVATE_HOST:
        if re.search(pat, host, re.I):
            return 'that address points at your own machine or your home network'
    if '.' not in host:
        return 'that address has no domain in it'
    if not allow_query and (u.query or u.fragment):
        return 'the address must not carry a question mark or a #'
    return None


def check_template(node, depth, count):
    if depth > LIMITS['pathDepth']:
        return 'the request is nested too deeply'
    if node is None or isinstance(node, (int, float, bool)):
        return None
    if isinstance(node, str):
        m = SOLE.match(node)
        if m:
            return (None if m.group(1) in PLACEHOLDERS
                    else '%s is not something this site fills in' % m.group(1))
        if ANY_BRACE.search(node):
            return 'a value in braces must stand alone, not sit inside other text'
        return None if len(node) <= 400 else 'a value in the request is too long'
    if isinstance(node, list):
        items = list(enumerate(node))
    elif isinstance(node, dict):
        items = list(node.items())
    else:
        return 'the request contains something that is not JSON'
    count[0] += len(items)
    if count[0] > LIMITS['templateNodes']:
        return 'the request has too many fields in it'
    for k, v in items:
        if isinstance(node, dict) and not re.match(r'^[\w.\-]{1,40}$', str(k)):
            return '%s is not a usable field name' % str(k)[:20]
        e = check_template(v, depth + 1, count)
        if e:
            return e
    return None


def uses(node, name):
    if isinstance(node, str):
        return node == '{%s}' % name
    if isinstance(node, list):
        return any(uses(v, name) for v in node)
    if isinstance(node, dict):
        return any(uses(v, name) for v in node.values())
    return False


def validate(raw, taken=()):
    errors = []

    def bad(m):
        errors.append(m)

    if not isinstance(raw, dict):
        return ['a source is a JSON object']
    if len(json.dumps(raw)) > LIMITS['manifestBytes']:
        return ['that source record is too big']

    unknown = sorted(set(raw) - TOP_KEYS)
    if unknown:
        bad('this site does not understand: ' + ', '.join(unknown[:4]))
    if raw.get('spec') != 1:
        bad('this record is not written for this version of the site')

    sid = clean(raw.get('id'), LIMITS['idLen'])
    if not sid or not re.match(r'^[a-z0-9][a-z0-9-]{2,31}$', sid):
        bad('the short name must be 3 to 32 characters, lower case letters, '
            'digits and dashes')
    elif sid in taken:
        bad('there is already a source called %s' % sid)

    if not clean(raw.get('name'), LIMITS['nameLen']):
        bad('it needs a name')
    if not clean(raw.get('set'), LIMITS['setLen']):
        bad('it needs a short title for the folder')

    if raw.get('home'):
        e = check_url(raw['home'], allow_query=True)
        if e:
            bad('the page about it: ' + e)

    e = check_url(raw.get('endpoint'), allow_query=False)
    if e:
        bad('the address it is asked at: ' + e)

    method = str(raw.get('method', 'POST')).upper()
    if method not in ('POST', 'GET'):
        bad('it must be asked with GET or POST')

    headers = raw.get('headers')
    if headers is not None:
        if not isinstance(headers, dict):
            bad('the headers must be a plain object')
        else:
            for k, v in headers.items():
                lk = str(k).lower()
                if lk not in HEADERS_ALLOWED:
                    extra = (': sources on this site work without a key'
                             if lk == 'authorization' else '')
                    bad('the header %s is not allowed here%s' % (str(k)[:24], extra))
                elif str(v).lower() not in HEADERS_ALLOWED[lk]:
                    bad('%s cannot be set to that' % k)

    count = [0]
    if method == 'POST':
        if raw.get('body') is None:
            bad('a POST needs a request body')
        else:
            e = check_template(raw['body'], 0, count)
            if e:
                bad('the request body: ' + e)
            elif not uses(raw['body'], 'prompt'):
                bad('the request body never uses {prompt}')
        if 'query' in raw:
            bad('a POST does not take a query')
    else:
        if raw.get('query') is None:
            bad('a GET needs a query')
        else:
            e = check_template(raw['query'], 0, count)
            if e:
                bad('the query: ' + e)
            elif not uses(raw['query'], 'prompt'):
                bad('the query never uses {prompt}')
        if 'body' in raw:
            bad('a GET does not take a body')

    r = raw.get('response')
    if not isinstance(r, dict):
        bad('it must say where the picture is')
    elif r.get('kind') not in KINDS:
        bad('the answer must be one of: ' + ', '.join(sorted(KINDS)))
    elif r['kind'] == 'binary':
        if 'path' in r:
            bad('a picture sent on its own has no path')
    else:
        path = str(r.get('path', '')).strip()
        if not re.match(r'^[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*$', path):
            bad('the path to the picture looks like images.0 — letters, digits '
                'and dots')
        elif len(path.split('.')) > LIMITS['pathDepth']:
            bad('the path to the picture is too deep')

    size = raw.get('size') or {}
    def ok_side(v):
        return (isinstance(v, int) and not isinstance(v, bool)
                and LIMITS['minSide'] <= v <= LIMITS['maxSide'] and v % 8 == 0)
    if not ok_side(size.get('width')) or not ok_side(size.get('height')):
        bad('the size must be whole numbers, multiples of 8, between %d and %d'
            % (LIMITS['minSide'], LIMITS['maxSide']))

    cnt = str(raw.get('count', 'one-per-call'))
    if cnt not in ('n', 'one-per-call'):
        bad('count is either n or one-per-call')
    if cnt == 'n':
        t = raw.get('body') if method == 'POST' else raw.get('query')
        if t is not None and not uses(t, 'n'):
            bad('it says it returns several at once but never uses {n}')

    t_ms = raw.get('timeoutMs', 120000)
    if (not isinstance(t_ms, int) or isinstance(t_ms, bool)
            or not LIMITS['minTimeout'] <= t_ms <= LIMITS['maxTimeout']):
        bad('the deadline must be a whole number between %d and %d milliseconds'
            % (LIMITS['minTimeout'], LIMITS['maxTimeout']))

    if 'colour' in raw:
        c = raw['colour'] or {}
        hexish = lambda v: isinstance(v, str) and re.match(r'^#[0-9a-fA-F]{6}$', v)
        if not all(hexish(c.get(k)) for k in ('c1', 'c2', 'c3')):
            bad('the three colours must be written like #ff8800')

    return errors


def main(argv):
    paths = argv[1:]
    if not paths:
        print(__doc__.strip())
        return 2

    worst = 0
    seen = []
    for path in paths:
        try:
            text = open(path, encoding='utf-8').read()
        except OSError as e:
            print('✗ %s\n    cannot be read: %s' % (path, e))
            worst = 1
            continue
        if len(text) > LIMITS['manifestBytes']:
            print('✗ %s\n    that file is too long to be a source' % path)
            worst = 1
            continue
        try:
            raw = json.loads(text)
        except ValueError as e:
            print('✗ %s\n    that is not valid JSON: %s' % (path, e))
            worst = 1
            continue

        errors = validate(raw, taken=seen)
        name = raw.get('id') if isinstance(raw, dict) else None
        if isinstance(name, str):
            seen.append(name)

        if errors:
            worst = 1
            print('✗ %s' % path)
            for e in errors:
                print('    %s' % e)
        else:
            stem = path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            note = ''
            if isinstance(name, str) and stem != name:
                note = ('  (note: the file should be named %s.json to match its id)'
                        % name)
            print('✓ %s%s' % (path, note))

    print()
    print('all clear' if worst == 0 else 'at least one source was refused')
    return worst


if __name__ == '__main__':
    sys.exit(main(sys.argv))
