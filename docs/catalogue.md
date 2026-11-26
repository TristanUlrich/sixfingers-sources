# A machine is data, never code: opening a catalogue to strangers

The open side of [SIXFINGERS](https://sixfingers.art) is a catalogue of picture machines. Anyone can propose one: a model on the [AI Horde](https://aihorde.net), or a machine with its own address that the site will then call to make pictures. That second part is the dangerous one. A website that fetches an address a stranger supplied, with parameters a visitor typed, is a textbook server-side request forgery and injection surface. This note is about the one principle that makes it safe to open at all, and the specific refusals that enforce it. All of the code here is in this repository: [`tools/check-source.py`](../tools/check-source.py), the same rules the site applies, with no dependencies.

The principle is in the schema's first line: **a machine is data, never code.** There is no field for a script, a snippet, a function or a URL to load and run, and there never will be. Everything below follows from taking that literally.

## The rule set is chosen, never guessed

A record comes in one of two shapes: a name on the Horde (one string, no address, no request) or a machine with its own address (the full surface). Which set of rules judges a record is decided by an explicit `kind` field, never inferred from which fields happen to be present:

```python
def validate_any(raw, taken=()):
    """The one door. `kind` picks the rule set, exactly as the site does."""
    if isinstance(raw, dict) and raw.get('kind') == 'horde':
        return validate_horde(raw)   # names a model: the whole surface is one string
    return validate(raw, taken)      # an address: the full set of refusals
```

That looks like a detail and it is the heart of it. If the validator guessed the shape from the fields it saw, a submitter could choose which rules apply to their record by choosing which fields to include, and smuggle an address into the lighter path. So the Horde shape refuses, by name, every field that belongs to an address (`endpoint`, `method`, `headers`, `body`, `response`, and the rest): the moment a record that calls itself a model carries an address, it is not a model any more, and it is rejected rather than reinterpreted.

## Nothing unknown is ever ignored

Both shapes validate against a closed list of fields. A field that is not on the list is an error, not something quietly dropped:

```python
unknown = sorted(set(raw) - TOP_KEYS)
if unknown:
    bad('this site does not understand: ' + ', '.join(unknown[:4]))
```

Ignoring an unknown field is how a system ends up running a record that is not the one anybody reviewed: the field a human read as harmless might be the whole point of the submission. Refusing it means the record that runs is exactly the record that was checked.

## A parameter must stand alone

Inside a request body, the visitor's prompt is placed through a handful of placeholders. A placeholder has to be the entire value, never pasted into the middle of a string:

```python
SOLE = re.compile(r'^\{(\w+)\}$')        # the whole value is {prompt}
ANY_BRACE = re.compile(r'\{[^}]*\}')      # a brace anywhere else
...
m = SOLE.match(node)
if m:
    return None if m.group(1) in PLACEHOLDERS else '%s is not something this site fills in' % m.group(1)
if ANY_BRACE.search(node):
    return 'a value in braces must stand alone, not sit inside other text'
```

`"prompt": "{prompt}"` is allowed; `"prompt": "a photo of {prompt}"` is refused. A value pasted into the middle of another string is exactly how a template turns into an injection. Standing alone, the placeholder is replaced by a proper JSON value, so whatever the visitor typed arrives as a string, never as structure, no matter what characters it contains.

## The address is refused before any request is made

When a record does carry an address, the address itself is checked against the whole family of ways a URL can be turned back on the person running the site:

```python
PRIVATE_HOST = [
    r'^localhost$', r'\.localhost$', r'^127\.', r'^0\.', r'^10\.',
    r'^192\.168\.', r'^172\.(1[6-9]|2\d|3[01])\.', r'^169\.254\.',
    r'^100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.',
    r'^\[?::1\]?$', r'^\[?fc', r'^\[?fd', r'^\[?fe80',
    r'\.local$', r'\.internal$', r'\.home$', r'\.lan$',
]
```

On top of that list, `check_url` refuses anything that is not `https`, any address carrying a name or password, a bare IP address written any way, and a host with no dot in it. The reason is stated plainly in the schema: a web page that is allowed to call your own machine can be used to find out what you run on it. So a generator on your own computer cannot be plugged in, by design, not by oversight.

## The picture that comes back is treated as hostile too

The answer is not trusted either. Only PNG, JPEG and WEBP are accepted, and the type is decided by looking at the first bytes rather than by believing a label. SVG is refused outright, because it is a document that can carry a script, not a picture. Every image is decoded and redrawn through a canvas before it is kept, so what is stored is the pixels and nothing else: no metadata, no colour-profile tricks, no bytes hiding after the end of the file. The request goes out with no cookies, no referrer, and redirects refused.

## Two copies, held to a written table

The rules live twice: in `check-source.py` here, and in the site's own `js/sources.js`, which is the copy that actually decides what runs. Two rule sets that quietly disagree are worse than one, because the copy people check is not the copy that runs. That is not hypothetical: it happened on 25 August 2026, and nothing went red for three pushes. So neither copy is the reference. A written table of cases, [`tools/cases.json`](../tools/cases.json), is: records paired with whether each must be accepted, and both copies are held to it on every push. Change a rule in one place and the table turns it red.

## The lesson

Opening something to strangers is a design decision before it is a validation one, and the safe version of that decision is to remove the dangerous thing rather than to filter it. There is no code field because a catalogue with a code field could not be opened safely at all. The rule set is chosen by an explicit flag because a guessed one hands the choice to the attacker. Unknown fields are refused because ignoring them runs something unreviewed. And the rules are held to a written table because the only thing worse than one gate is two that disagree. None of it is clever; all of it is the same move, made everywhere: make the thing data, and give the data nowhere to hide.

The site's copy of these rules is in the private repository (`js/sources.js`). This repository holds the open copy you can run, the schema, and the written cases table. The full field reference is in [`sources/SCHEMA.md`](../sources/SCHEMA.md).

---

*More engineering notes: [The grey squares](grey-squares.md) · [Two worlds](two-worlds.md) · [The honest countdown](wait-time.md) · [The word guard](../tools/WORD-GUARD.md) · [all notes](README.md)*
