<div align="center">

<img src="art/icon.png" width="96" alt="">

# SIXFINGERS

**Type a phrase. Six pictures arrive in a pack.**

### [sixfingers.vercel.app](https://sixfingers.vercel.app)

Free. No account, no key, no payment, no advertising.

</div>

---

## What this repository is

This is **not** the site. It is the shelf the site keeps its picture machines on.

SIXFINGERS is a small website dressed as an operating system from 2001. You type
something, and six pictures come back in a folder you have to knock on to open.
The pictures are made by strangers' graphics cards, lent for free through the
[AI Horde](https://aihorde.net).

The site itself is closed. **This repository holds only the catalogue**: one small
file per picture machine the site knows how to ask, and the rules a machine has to
meet before it goes on the shelf. It exists so that somebody who knows about a
free image generator can add it without needing to see, touch, or run any of the
site's code.

| | |
|---|---|
| **The site** | closed source, all rights reserved, not in this repository |
| **This repository** | the catalogue of sources, and the rules for adding one |
| **What you can contribute** | a source: a few lines of JSON describing a machine |
| **What you cannot do** | copy, host, rebuild or adapt SIXFINGERS itself |

---

## Add a picture machine

You do not need to write code and you do not need to run anything.

1. Read [`sources/SCHEMA.md`](sources/SCHEMA.md) — it is short, and it explains
   every field in plain words.
2. Copy [`sources/example-pics.json`](sources/example-pics.json) and change it.
3. Check it: `python3 tools/check-source.py sources/your-source.json`
   — the same rules the site itself applies, so if this passes, the site will
   accept it.
4. Open [a New source issue](../../issues/new?template=new-source.yml) — the form
   asks for exactly what is needed — or send a pull request adding your file.

Everything is reviewed by hand before it ships. A source in this repository is not
live until the site is deployed with it.

### What a source must be

These are refusals, not preferences. A proposal that fails any of them is closed.

- **Free, and working without an identifier.** No API key, no token, no account, no
  `Authorization` header. The site refuses that header outright.
- **Reachable over HTTPS at a real domain name.** Not a numbered address, not
  `localhost`, not a machine on your home network. A page that can talk to
  somebody's own machine can look around inside it, so the site will not.
- **Honest about what it is.** The description says what the machine actually does
  to a picture. Nothing invented, no marketing.
- **Allowed to be used this way.** If its terms of service forbid being called from
  a web page, it does not go on the shelf.
- **Safe for a stranger to type at.** A machine that returns something illegal
  whatever you ask it is not welcome here.

### What happens to what you send

The site only ever sends a source the words you typed and the size of the picture.
Nothing else: no name, no account, no key, no cookie, and none of the pictures you
already have. Whatever comes back is decoded and redrawn by your own browser
before it is kept, so nothing hidden inside an image file survives the trip.

The details, including everything the design defends against and why, are in
[`SECURITY.md`](SECURITY.md).

---

## Anybody can add a source without asking

The catalogue here is the shelf that **ships with the site**. You do not have to
wait for it.

Inside SIXFINGERS, **Community → Add a source** takes the same JSON and keeps it in
your own browser. It works immediately, it is never uploaded, and it affects
exactly one person: you. Sources are shared between people as text — a recipe you
paste — not as code, and never automatically.

Proposing one here is for when you think everybody should have it.

---

## Licence, in plain words

**Copyright © 2026 Tristan Ulrich. All rights reserved.**

The site, its code, its artwork, its wallpaper, the pointer, the name SIXFINGERS
and the six-fingered hand are his. No licence is granted to copy, host, publish,
adapt, rebuild or redistribute any of it. Reading this repository is not
permission to reuse it.

The catalogue files and the schema in this repository may be read and used to
understand or write a source. If you contribute one, you keep the credit and you
grant Tristan the right to ship it with the site. See [`LICENSE`](LICENSE) and
[`CONTRIBUTING.md`](CONTRIBUTING.md).

`art/icon.png` is cut from the author's own pointer file. It is not stock, it is
not licensed for reuse, and it is not a template.

---

<div align="center">
<sub>Made by Tristan Ulrich · no monetisation, ever · no rarity, no scores, nothing invented</sub>
</div>
