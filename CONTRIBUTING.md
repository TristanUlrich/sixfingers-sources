# Adding a picture machine

Thank you for wanting to. Two minutes of reading saves a rejected proposal.

## What is welcome

**One thing only: a source.** A few lines of JSON describing a free picture
generator the site does not know about yet. That is the whole surface area of this
repository, and it is deliberate.

Also welcome: a correction to a source already here (an address that moved, a
description that is wrong), a fix to the schema documentation, and a bug in
[`tools/check-source.py`](tools/check-source.py).

## What is not

- **Code for the site.** The site is closed and not in this repository. Pull
  requests adding site code, features, styling or fixes will be closed unread.
- **A source that needs a key, a token, an account or a payment.** The site refuses
  the `Authorization` header outright, and this rule is not negotiable: it is what
  lets the log-on screen say "no account, no key" honestly, and it means nobody can
  ever be handed a bill for using SIXFINGERS.
- **A source on your own machine or your home network.** `localhost`, `127.0.0.1`,
  `192.168.x`, anything `.local`. Refused before a request is made. A web page
  allowed to call your own machine can look around inside it.
- **A service whose terms forbid this.** If calling it from a web page breaks its
  rules, it does not go on the shelf. Check, and say in your proposal that you did.
- **A generator that returns illegal material whatever you ask it.**
- **Anything invented.** If your description says a machine is fast, it is because
  you timed it.

## How

```bash
git clone https://github.com/TristanUlrich/sixfingers-sources
cd sixfingers-sources
cp sources/example-pics.json sources/my-machine.json
# edit it, then:
python3 tools/check-source.py sources/my-machine.json
```

The checker applies the same refusals as the site itself, so a source that passes
locally will be accepted by the site. Name the file after the `id` inside it.

Then either open [a New source issue](../../issues/new?template=new-source.yml), or
send a pull request with **one source per pull request**.

## What happens next

1. **The checker runs, and it answers you.** About a minute after you open the
   issue, a comment says whether the record passes and, if it does not, every rule
   it breaks in plain words. Fix it and edit the issue: the checker looks again and
   rewrites its own comment, so nobody has to reopen anything and the thread does
   not fill up with verdicts. It judges the record and never the person, and it
   decides nothing.
2. Tristan reads it. He does not write code, so a proposal that cannot be understood
   from its own description will be asked about rather than guessed at.
3. If it is accepted, it is merged — and it goes live **only when the site is next
   deployed**. The site never fetches this catalogue over the network while it is
   running, on purpose: nothing merged here can reach a visitor until it is shipped
   deliberately.

## You do not have to wait for anybody

The same JSON works immediately in your own browser: in SIXFINGERS, open
**Community → Add a machine** and paste it. It stays in that browser, it is never
uploaded, and it affects nobody but you. Propose it here when you think everybody
should have it.

## Two things about rights

By proposing a source you confirm it is yours to give, and you grant Tristan Ulrich
the right to ship it with SIXFINGERS. You keep the credit.

That grant covers your source record and nothing else. It gives you no rights over
SIXFINGERS, and reading this repository gives you no permission to reuse the site.
See [`LICENSE`](LICENSE).

## Tone

Descriptions in this catalogue are written like the rest of the site: plainly, in
short sentences, saying what a thing actually does rather than what it would like to
be thought of as doing. "It gets the composition right and the anatomy wrong" is the
register. No superlatives, no exclamation marks, no emoji.
