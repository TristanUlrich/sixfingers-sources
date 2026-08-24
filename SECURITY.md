# Security

## Reporting something

Open a [private security advisory](../../security/advisories/new). If that is not
available to you, open an issue saying only that you have found something and asking
for a way to send it — **do not put the details in a public issue**.

There is no bounty. There is a name in the credits and a fast fix.

In scope: the live site at `sixfingers.vercel.app`, the source format and its
validator, and `tools/check-source.py`. Out of scope: the services listed in the
catalogue, which are run by other people, and the AI Horde.

---

## How this is built, so you know where to look

The site is one static page. **There is no server, no database, no account, no
session, no cookie and no analytics.** Everything a person makes lives in their own
browser, in IndexedDB, and never leaves it unless they press Share themselves. There
is nothing on a server to steal because there is no server.

That shape removes most of a web application's attack surface and concentrates the
rest in one place: what happens when the site talks to somebody else's picture
machine.

## What a community source can and cannot do

A source is **data, never code.** There is no field for a script, a snippet, a
function, or a URL to be loaded and executed, and there will not be one. There is no
sandbox to escape because nothing is ever run.

Everything below is enforced in `js/sources.js` in the site, mirrored in
`tools/check-source.py` here, and covered by 58 checks in the site's own self-test.

| Attempt | What stops it |
|---|---|
| JavaScript in a field | Nothing is executed or written into the page as HTML. The site contains no `innerHTML`, no `eval`, no `new Function` — and the deployed pages send `require-trusted-types-for 'script'`, so a future mistake in that direction fails closed in Chromium. |
| Probing the visitor's own machine | `https` only. `localhost`, loopback, link-local, every private range, bare IP addresses and `.local`-style names are refused **before a request is made**. |
| Reading what is already in the browser | A source is handed the prompt and the size. It cannot ask for more: the request is built from a template whose only substitutable values are `{prompt}`, `{width}`, `{height}`, `{n}`, `{seed}`. |
| Injecting into the request | A placeholder must stand alone. `"a photo of {prompt}"` is refused. Standing alone it is replaced by a JSON value, so the prompt reaches the machine as a string whatever it contains. |
| Sending a key or a cookie | Only `Content-Type` and `Accept` may be set. `Authorization` is refused by name. Every request goes out with `credentials: 'omit'`, `referrerPolicy: 'no-referrer'` and `redirect: 'error'`. |
| A picture that is not a picture | SVG is refused — it is a document that can carry a script. For base64 the type is decided by sniffing the first bytes, not by trusting a label. Everything that survives is **decoded and redrawn through a canvas** before it is stored, so what is kept is pixels: no metadata, no trailing bytes, no container. |
| Being enormous or endlessly slow | 8 MB per picture, 48 MB per pack, six pictures maximum, and a deadline of 5 to 180 seconds on every request, enforced with `AbortController`. |
| Pretending to be another entry | Names are normalised (NFC), stripped of control characters, zero-width padding and the bidirectional overrides that let a name print backwards, length-capped, and only ever placed in the page as text. |
| A bad entry reaching everybody | The catalogue is **baked into the site at deploy time and never fetched over the network while the site runs.** Nothing merged here reaches a visitor until the site is deployed. A source somebody adds in their own browser affects exactly one person. |
| An unknown field slipping through | Unknown fields are an **error**, not something ignored. A field the site does not understand might be the point of the record. |
| A number that is not a number | Refused rather than converted. `"width": "512"` used to be accepted by silent coercion; the self-test caught it and it is now refused. Nothing is repaired quietly. |

## Headers the site sends

Set in `vercel.json` and verified live:

```
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self';
  img-src 'self' blob: data:; font-src 'self'; connect-src 'self' https:;
  media-src 'none'; object-src 'none'; frame-src 'none'; child-src 'none';
  worker-src 'none'; manifest-src 'self'; base-uri 'none'; form-action 'none';
  frame-ancestors 'none'; upgrade-insecure-requests;
  require-trusted-types-for 'script'; trusted-types 'none'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
Strict-Transport-Security: max-age=63072000; includeSubDomains
Permissions-Policy: camera=(), microphone=(), geolocation=(), … (all off)
```

`connect-src` allows any `https` host on purpose: the AI Horde hands back image
addresses on hosts it chooses, and a community source is by definition somewhere the
site has never heard of. The protection against a bad address is not the CSP — it is
the validator, which refuses the address before a request exists.

## What we do not claim

- The site cannot vouch for the machines in the catalogue. Whoever runs an address
  sees the prompts sent to it. The consent screen says so before a source is added.
- Trusted Types is enforced by Chromium and ignored by other browsers today. It is a
  second lock, not the only one: the first is that the code has no injection sinks at
  all.
- A picture is redrawn, not inspected. Nothing here judges what a machine returns.
