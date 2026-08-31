# What a source looks like

A source is a small JSON file describing one picture machine.

**It is data, never code.** There is no field for a script, a snippet, a function or
a URL to load and run, and there never will be. That is the whole reason this can be
open to strangers at all.

## There are two shapes, and `kind` decides

| | |
|---|---|
| **A name on the AI Horde** | `"kind": "horde"`. You name a model the Horde already runs. No address, no headers, no request. **Start here** — it is six lines, and there are 163 models waiting. |
| **A machine with its own address** | No `kind` field. You give the address, the request and where the picture sits in the answer. Everything below the Horde section is about this shape. |

Both are checked the same way and both land in the same shelf. The second shape
exists because not every machine is on the Horde; the first exists because almost
every good one already is.

---

## A name on the AI Horde

The AI Horde is a pile of volunteers lending their graphics cards. Anyone can ask
it for a picture, with no key and no account, and on 25 August 2026 it was running
**163 different models, every one of them with at least one volunteer**. The site
already knows how to talk to it.

So for these, the hard part is not technical. It is **editorial**: saying which of
the 163 is worth anyone's time, what it is good at, and how it gets things wrong.
That is a judgement, and it is the contribution this shelf actually wants.

```json
{
  "spec": 1,
  "kind": "horde",
  "id": "icbinp",
  "name": "ICBINP",
  "set": "Photographic",
  "model": "ICBINP - I Can't Believe It's Not Photography",
  "note": "Passes for a photograph until you look.",
  "what": "Ten photorealistic models merged together, so it comes back looking like a real camera: grain, depth of field, ordinary light.",
  "good": "ordinary moments, badly witnessed",
  "home": "https://civitai.com/models/28059",
  "colour": { "c1": "#eceff2", "c2": "#8b939c", "c3": "#2a2d31" },
  "measured": { "on": "2026-08-25", "pack_seconds": 46.6, "steps": 14 }
}
```

| Field | Required | What it is |
|---|---|---|
| `spec` | yes | Always `1`. |
| `kind` | yes | Exactly `"horde"`. This is what picks the rules; spell it wrong and your record is judged as an address, and refused. |
| `id` | yes | 3 to 32 characters, lower-case letters, digits and dashes. It is the filename too. |
| `name` | yes | What to call it on the folder, up to 40 characters. |
| `set` | yes | The short title printed on the folder, up to 24 characters. |
| `model` | yes | **The model name exactly as the Horde writes it**, up to 120 characters. Capitals and apostrophes matter; it is not cleaned up, it is taken or refused. Get it from the Horde's own model list. |
| `note` | no | One line, up to 120 characters. |
| `what` | no | Up to **700** characters. What it actually does to a picture, not what it advertises. The site folds it to three lines and puts a **Read the rest** link under it, so write the whole thing. |
| `good` | no | Up to **700** characters. What it is worth using *for*. |
| `home` | no | An `https` page about it. |
| `colour` | no | **One** colour as `#rrggbb`, and the site builds the shades. The folder is how people will recognise this machine, so this is the field to care about. |
| `finish` | no | **Reserved.** See below: the finishes belong to the machines this project publishes itself. A proposal that carries one is not refused, but the finish is dropped and the colour does the work. |
| `measured` | no | Numbers you took yourself. See below. |

**Nothing else.** `endpoint`, `method`, `headers`, `body`, `query`, `response`,
`size`, `count` and `timeoutMs` are all refused on a Horde record, by name. A
record like this names a model; the moment it carries an address it is not one of
these any more, and the whole reason this shape is safe is that there is nothing in
it to point anywhere.

### The folder, and why it is the whole point of `colour` and `finish`

Every machine on this site gets a folder, and that folder follows it everywhere:
the row where you pick a machine, the Community window, the icon on the desktop,
and the folder standing alone in the black room while you knock on it.

So the folder has to say **which machine made this**, at a glance, before a word
is read. Two things do that, and nothing else does:

**`colour`** is what carries at every size, and **it is yours to choose**. Write
one colour and the site works out the rest of the folder from it:

```json
"colour": "#6f9b62"
```

That is the whole field. Light for the flap, mid for the body, dark for the
outline, and a readable ink for the label are all derived from it, so the folder
comes out looking like it belongs on this desktop whatever you pick. If you would
rather set all three shades yourself, `{ "c1": ..., "c2": ..., "c3": ... }` still
works, and nothing in the site prefers one form over the other.

Pick something that is not already taken: the shelf has amber, grey and sage on it
today. A colour close to one of those reads as a duller version of it rather than
as its own thing, which is a mistake that has already been made here once.

**`finish`** is what the folder is *made of* — the surface of the whole thing,
not a logo or a badge. **It is reserved for the machines this project publishes
itself**, and that is a deliberate line rather than a technical one: the shelf
should say at a glance which machines are the house's and which came from
somebody else, and it says it with the material rather than with a label or a
rank. Everyone gets the same folder and the same freedom of colour; the finishes
are the one thing that is not on offer.

A proposal carrying `finish` is **not refused** for it. The robot says so in its
answer, the field is dropped, and your colour carries the record.

For the record, the seven that exist:

| | |
|---|---|
| `sunburst` | nothing at all. Plain manila, the ordinary folder. **This is the default** |
| `film` | the grain of a print, and a little gloss. For machines that make photographs |
| `ink` | the tooth of drawing paper. For machines that draw or paint |
| `mirror` | one clean sweep of light and no texture at all. For machines whose strength is sharpness |
| `frost` | a fine crystalline weave. For cold, precise machines |
| `overprint` | a press that is a hair out of register. For machines that surprise you |
| `strata` | faint stacked layers. For merges of merges |

Seven, and no more. Below 40 pixels a finish is not drawn at all: at that size it
would be dirt, and the colour does the work alone — which is the other half of why
the colour is the field worth thinking about.

### `measured`, and the rule behind it

The site never prints a number nobody took. If you write
`"pack_seconds": 46.6`, it means you asked that model for six pictures and watched
a clock. Every value must be a number or a short note, nothing else — no objects,
no `true`, nothing that could be dressed up as a measurement without being one.

If you did not measure it, leave `measured` out. An entry with no numbers is fine.
An entry with invented ones is the one thing this project will not carry.

---

## A machine with its own address

Everything from here down describes the second shape: a source that says where a
picture machine lives, how to ask it for a picture, and where the picture sits in
its answer.

---

## The smallest complete example

```json
{
  "spec": 1,
  "id": "example-pics",
  "name": "Example Pictures",
  "set": "Example",
  "note": "A machine that makes pictures.",
  "what": "It draws whatever you type, badly.",
  "home": "https://example.com/about",
  "endpoint": "https://api.example.com/v1/txt2img",
  "method": "POST",
  "headers": { "Content-Type": "application/json" },
  "body": { "prompt": "{prompt}", "width": "{width}", "height": "{height}", "steps": 20 },
  "response": { "kind": "json-base64", "path": "images.0" },
  "size": { "width": 512, "height": 512 },
  "count": "one-per-call",
  "timeoutMs": 120000,
  "colour": { "c1": "#ffd98a", "c2": "#e8913f", "c3": "#8a4a10" }
}
```

---

## Every field

| Field | Required | What it is |
|---|---|---|
| `spec` | yes | Always `1`. The version of this format. |
| `id` | yes | A short name, 3 to 32 characters, lower-case letters, digits and dashes. It is the filename too. |
| `name` | yes | What the machine is called. Up to 40 characters. |
| `set` | yes | The short title printed on the folder, up to 24 characters. Think of it as the name of an expansion: *First Light*, *Cold Snap*. |
| `note` | no | One line, up to 120 characters. The thing you would say about it in passing. |
| `what` | no | Up to **700** characters, and the important one: **what it actually does to a picture.** Not what it advertises. |
| `home` | no | An `https` page about it, so somebody can go and read for themselves. |
| `endpoint` | yes | The `https` address that is asked. No question mark, no `#`, no name or password in it. |
| `method` | yes | `POST` or `GET`. |
| `headers` | no | Only `Content-Type` and `Accept`, and only with ordinary values. **`Authorization` is refused.** |
| `body` | POST only | The request, as JSON, with placeholders. Must use `{prompt}`. |
| `query` | GET only | The query, as a flat object with placeholders. Must use `{prompt}`. |
| `response` | yes | Where the picture is. See below. |
| `size` | yes | `width` and `height`, **whole numbers**, multiples of 8, from 128 to 1024. |
| `count` | no | `one-per-call` (default) or `n` — use `n` only if one call really returns several pictures, and then `{n}` must appear in the request. |
| `timeoutMs` | no | A whole number of milliseconds, 5000 to 180000. Defaults to 120000. |
| `colour` | no | **One** colour as `#rrggbb` and the site builds the shades, or the three named `c1`, `c2` and `c3` if you would rather set them yourself. |

Any field not on this list is an **error**, not something ignored. A field the site
does not understand might be the whole point of your record, and using it anyway
would mean using a source that is not the one you described.

---

## Placeholders

Inside `body` and `query`, five values get filled in:

| Placeholder | Becomes |
|---|---|
| `{prompt}` | what the person typed, as a string, up to 400 characters |
| `{width}` `{height}` | the numbers from `size` |
| `{n}` | how many pictures are wanted in this call |
| `{seed}` | a random number, so six pictures are not identical |

A placeholder must **stand alone**: `"prompt": "{prompt}"` is right,
`"prompt": "a photo of {prompt}"` is refused. A value pasted into the middle of
another string is how a template turns into an injection, so it is simply not
allowed. Standing alone, the placeholder is replaced by a proper JSON value, which
means the prompt arrives at your machine as a string whatever it happens to say.

---

## Where the picture is

`response.kind` is one of three:

**`json-base64`** — the answer is JSON and the picture is base64 inside it.
```json
"response": { "kind": "json-base64", "path": "images.0" }
```

**`json-url`** — the answer is JSON and it holds an `https` address to fetch.
```json
"response": { "kind": "json-url", "path": "output.url" }
```

**`binary`** — the answer *is* the picture. No `path`.
```json
"response": { "kind": "binary" }
```

`path` is dotted, letters, digits and dots only. A number is an array position:
`images.0` means "the field `images`, then its first item". Six levels deep at most.
No brackets: `images[0]` is refused.

---

## What the site does with the answer

Worth knowing, because it changes what you should declare:

- Only **PNG, JPEG and WEBP** are accepted. **SVG is refused** — it is a document
  that can contain a script, not a picture.
- For base64, the type is decided by **looking at the first bytes**, never by
  trusting a label.
- One picture may be at most **8 MB**, a pack at most **48 MB**.
- Every picture is **decoded and redrawn through a canvas** before it is kept.
  What is stored is the pixels. No metadata, no colour-profile tricks, no bytes
  hiding after the end of the file, no original container.
- The request goes out with **no cookies, no referrer, and redirects refused**.

---

## Addresses that are refused before a request is made

- anything that is not `https`
- `localhost`, `127.0.0.1`, `::1`, and every name ending `.local`, `.internal`,
  `.home`, `.lan`
- the private ranges `10.x`, `192.168.x`, `172.16–31.x`, `169.254.x`, `100.64–127.x`
- a bare IP address, written any way
- a host name with no dot in it
- an address carrying a name and password

This is why a generator running on your own computer cannot be plugged in: a web
page that is allowed to call your own machine can find out what you run on it. It is
not an oversight. If you want your own rig reachable, give it a real name and a
certificate.

---

## Check it before proposing it

```bash
python3 tools/check-source.py sources/your-source.json
```

Same rules as the site, no dependencies, both shapes. It also runs by itself on
every proposal, so you will get the same answer either way — it is just faster to
hear it from your own machine.

## And how we know the two copies still agree

The rules exist twice: in `tools/check-source.py`, which you just ran, and in the
site's own `js/sources.js`, which is the copy that actually decides what gets used.
Two rule sets that quietly disagree are worse than one, because the one people
check is not the one that runs. It happened here, on 25 August 2026, and nothing
went red for three pushes.

So neither copy is the reference. **`tools/cases.json` is** — one written table of
records and whether each must be let in. `tools/check-cases.py` holds this side to
it on every push; a page inside the site holds the browser side to the same table.
Change a rule in one place and the table turns it red.

```bash
python3 tools/check-cases.py
```
