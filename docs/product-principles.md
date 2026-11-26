# Measured, honest, responsible: the rules the product keeps

The other notes in this [notebook](README.md) are about how parts of [SIXFINGERS](https://sixfingers.art) are built. This one is about how it is run. It is a short set of rules I decided and hold the whole product to, and they are the part I would defend in a room: not the code, the judgment behind it. Each one below is a choice, and each is enforced rather than merely stated.

## Every number on the screen is measured

The site never prints a figure nobody took. Volunteer counts, queue sizes and wait times come from the Horde; wash times come from real washes; and when there is nothing reliable to show, the display stays blank rather than guessing. The wait estimate is refit from recorded washes rather than tuned by feel, and that is written up on its own in [The honest countdown](wait-time.md). "No invented numbers" sounds obvious until you notice how many interfaces round a guess up to look confident. This one would rather show nothing.

## No dark patterns, on purpose

Nothing is for sale. There are no ads, no trackers, no scores, no streaks and no artificial scarcity. The coins are not a currency to spend more of: you start with six, one comes back every hour, a wash that fails or that you stop refunds its coin, and if you bring your own Horde key it costs no coin at all. They exist for one reason, to keep things fair for the volunteers whose computers do the work. An earlier version of the site had a measured rarity rank and a loyalty card; I removed both deliberately, because they invented a hierarchy that served the product's engagement and not the person using it.

## Labelled as AI, by law and by choice

Every picture you download carries a visible "AI · SIXFINGERS" mark and the IPTC metadata that labels it as made by an AI model (`trainedAlgorithmicMedia`), which is what the EU AI Act asks for in its Article 50. It would have been less work to skip it. Labelling generated images honestly is the kind of thing a product should do before it is forced to, and it is cheap insurance for whoever ends up holding the picture later.

## Safe to open, safe to read

Two of the harder problems here are safety problems, and both are solved with written tables rather than good intentions. [The word guard](../tools/WORD-GUARD.md) keeps the site from ever printing a slur in its own chrome, homoglyph-aware and careful never to refuse a real person's name. [A machine is data, never code](catalogue.md) is how the catalogue can be extended by strangers, whose entries the site will then call, without that becoming a server-side request forgery or an injection hole. In both, the rules exist in two copies and are held to a written set of cases, so the copy that is checked cannot drift from the copy that runs.

## Private by default

The page may only talk to a short, declared list of hosts, enforced by its Content Security Policy, so an injected script would have nowhere to send anything. The database cannot be read from the site at all; the anonymous measurements and error reports that make the estimates better carry no name and are deleted after three years; signing in is optional and uses only the email address; and every piece of this can be switched off in the profile. The default is the private one, not the other way round.

## Usable by everyone, and kind to the machines that run it

Everything works from the keyboard, reduced motion is respected, and a plain-text setting swaps the pixel font for a system one; the pixel text drawn on canvas is doubled with invisible text so a screen reader can read it. And because the whole thing runs on strangers' graphics cards lent for free, it asks for as little as it can: small pictures, few steps, and six separate small requests per wash so different volunteers can share the load instead of one carrying it. If tips ever add up, they go towards a computer that works for the Horde, so the site gives back some of what it takes.

## What this part is

It is a static site with almost no server: the pages are served as they are, accounts and measurements sit on a hosted database, and a couple of tiny functions do the rest. It costs very little to run and has few moving parts to rot. But the reason it is in this notebook at all is the list above. The hard calls in a product like this are not technical. They are what you refuse to do, no ads, no scores, no invented numbers, no slur, no unlabelled output, and what you take on when nobody makes you, the accessibility and the AI label and the deleting of data. That is the part of the work I own the most.

---

*More engineering notes: [The grey squares](grey-squares.md) · [Two worlds](two-worlds.md) · [The honest countdown](wait-time.md) · [The word guard](../tools/WORD-GUARD.md) · [A machine is data, never code](catalogue.md) · [all notes](README.md)*
