# What a source looks like

A source is a small JSON file. It says where a picture machine lives, how to ask it
for a picture, and where the picture sits in its answer.

**It is data, never code.** There is no field for a script, a snippet, a function or
a URL to load and run, and there never will be. That is the whole reason this can be
open to strangers at all.

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
| `what` | no | Up to 400 characters, and the important one: **what it actually does to a picture.** Not what it advertises. |
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
| `colour` | no | Three colours as `#rrggbb`, used for the folder's theme. |

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

Same rules as the site, no dependencies. If it passes there, it passes in the site.
