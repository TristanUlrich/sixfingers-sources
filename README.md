<div align="center">

<img src="art/icon.png" width="88" alt="">

# SIXFINGERS

A laundromat for prompts. You write one, pick a washing machine, and six pictures come out of the door.

**[sixfingers.art](https://sixfingers.art)**

<img src="docs/screenshots/room-day.jpg" width="900" alt="The front wall of an old laundromat: seven coloured washing machines, a yellow INSTRUCTIONS sign, a pink neon that reads sixfingers, a chequered floor. The prompt line waits on the floor.">

</div>

## What it is

SIXFINGERS is a small website that makes pictures with AI image models. It is dressed as one wall of an old laundromat. There are seven machines, and each one runs a different model. You write a prompt on the floor (the sentence you give the model), drop a coin in a machine, and your words get pulled in and washed. When the machine beeps you hold the door until it bursts, and six pictures come out.

It's free and you don't sign up for anything. The pictures come from the [AI Horde](https://aihorde.net), a network of people who lend their graphics cards to strangers for free.

I'm Tristan Ulrich, a student in Paris, and I make it on my own.

## Why it exists

Image models are bad at hands. Ask one for a person waving and there is a fair chance the hand comes back with six fingers, or four, or a thumb on the wrong side. Stable Diffusion 1.5, the model behind the orange machine in the middle, was the first one that most people could run, and it gets the composition of a picture right while getting the anatomy wrong. That is where the name comes from. The sign on the wall says so too: "Not responsible for extra fingers."

A free model on volunteer computers can take a minute, sometimes several, and most sites cover that with a spinner. I wanted the wait to be the part you enjoy. A laundromat is a room built for waiting: you put something in, you watch it go round, and you get your things back a little changed. Words going into a machine and coming back as six pictures felt like a fair description of what these models do.

The first version of the site, from August to October 2026, was dressed as Windows XP, and six pictures arrived as a "pack" you opened by knocking on it. The laundromat replaced it on 12 October 2026.

## How a wash goes

**Pick a machine.** Clicking a machine walks you up to it. Its card says which model it runs and what that model is good at, then three numbers: "wait", how long a wash would take if you started now; "ahead", how many requests are already waiting for this machine; and "helpers", how many volunteer computers are running its model right now.

<img src="docs/screenshots/machine-card.jpg" width="900" alt="Close-up of the yellow Daydream machine with its card: Anything Diffusion, 2023, a short description, then the wait, the number of requests ahead and the computers online, and a Generate button with a coin">

**Drop a coin.** The coin goes into the slot, the door swings open and the letters of your prompt fly in one at a time.

<img src="docs/screenshots/letters-fly-in.jpg" width="900" alt="The door of the yellow machine swings open and the letters of the prompt tumble into the drum">

**Wait in line.** The red display on the machine becomes a countdown, like a real one, and the card shows the same number. It only ever goes down, one second per second. The drum runs a programme picked at random for each wash: turns one way then the other, rocking, short shakes, pauses, and quick bursts of spin that pin the letters to the wall before letting them drop.

<img src="docs/screenshots/washing.jpg" width="900" alt="The machine mid-wash: pixel letters tumbling in water behind the glass, the card with six squares in coarse pixels and the countdown">

**Your turn.** When a volunteer picks up your prompt, the machine chimes and says so. From there the time is ours: the six pictures appear one by one in the squares as they really finish, the drum rinses, drains and spins, and the countdown reaches 0:00 exactly when the machine stops.

You don't have to stand there. Up to three machines can wash at once, one coin each, and you can walk between them; a machine that finishes while you're elsewhere lights up and beeps.

**Hold the door.** When the machine is done it glows. You press and hold on it, the drum rumbles, steam hisses through the seal, and the door blows open.

<img src="docs/screenshots/done.jpg" width="900" alt="The yellow machine glowing after its wash, with a pink line on the floor that says hold the door">

<img src="docs/screenshots/holding-door.jpg" width="900" alt="Holding the door: the glass glows, and a pink line on the floor says keep holding">

**Six pictures come out,** one at a time. You can keep them, share them, love them, or wash the same prompt in another machine.

<img src="docs/screenshots/one-picture.jpg" width="900" alt="The first picture large in the middle of the screen">

<img src="docs/screenshots/six-pictures.jpg" width="900" alt="All six pictures from the Daydream machine together">

Those six are a real wash on the Daydream machine with the prompt "a lighthouse keeper feeding seagulls in a storm", made for this page on 14 October 2026.

The collection keeps every wash with its prompt, its machine and its date, in your browser. Accounts are built (Supabase, hosted in Paris) so that a collection can follow you from one device to another; signing in with Google and GitHub opens as soon as those two are switched on.

<img src="docs/screenshots/collection.jpg" width="900" alt="The collection window in pixel style: a search box, sorting by newest, oldest or machine, and the wash with its six pictures">

## The room changes with the time

The light coming into the room follows your own clock: daylight, sunset, and night with the neon doing most of the work.

<table>
<tr>
<td><img src="docs/screenshots/room-sunset.jpg" alt="The laundromat at sunset, warm orange light across the floor"></td>
<td><img src="docs/screenshots/room-night.jpg" alt="The laundromat at night, blue and dim, the pink neon glowing"></td>
</tr>
</table>

It also works on a phone: the machines are close enough to touch, you swipe from one to the next, the card slides up underneath, and the prompt moves above the keyboard.

<table>
<tr>
<td><img src="docs/screenshots/phone-room.jpg" width="260" alt="SIXFINGERS on a phone at night: the sign, the machines and the prompt line on the floor"></td>
<td><img src="docs/screenshots/phone-machine.jpg" width="260" alt="The High Gloss machine on a phone, with its card underneath"></td>
<td><img src="docs/screenshots/phone-washing.jpg" width="260" alt="The High Gloss machine washing on a phone, with the countdown"></td>
</tr>
</table>

## The seven machines

From left to right on the wall. Each machine adds a "recipe" to your prompt: a few words of style, plus a list of things the picture should avoid. A machine doesn't have one fixed recipe. It has a small library sorted along a few axes (technique, light, colour), and for each wash every axis is shuffled like a deck of cards, so the six pictures each get a different combination and two washes of the same prompt don't come out alike.

| Machine | Model | What it does |
|---|---|---|
| Brushwork | Deliberate | Paints everything. Each picture gets its own technique (oil with thick impasto, watercolour, gouache, impressionist, Dutch golden age, acrylic), its own brushwork and its own palette. |
| Daydream | Anything Diffusion | A strong anime style that ignores half of what you type, and the regulars' favourite (there's a note on it that says so). The recipe moves between cel shading, manga panels, chibi and 1990s anime stills. |
| Sketch | Anything V5 | Pencil, ink and paper: graphite, pen, charcoal, ink wash, clean lineart. One picture in six keeps a little watercolour, because six black and white faces in a row felt grim. |
| Standard | Stable Diffusion 1.5 | No recipe at all. Your prompt goes in as you typed it. This is the model everything else here was built from, and the one with the most extra fingers. |
| High Gloss | Dreamshaper | The most capable and the least surprising. Concept art, glossy renders, storybook illustration, studio light. |
| Cinematic | AbsoluteReality | Every picture is a film still or a poster: its own shot, its own light (rim light, golden hour, a single hard lamp) and its own colour grade. |
| Photographic | ICBINP ("I Can't Believe It's Not Photography") | No recipe. It looks like a real camera took it, right up until you look at the hands. |

I picked the models with a stopwatch. On 12 October 2026 I sent the same prompt to eight models at the same time and kept the ones that came back in a reasonable time; two machines changed model that evening because almost nobody was running their old one.

## How the wait is estimated

This took four tries, and the fourth is the one worth describing.

What the real washes showed, once they were recorded: a wash is two very different waits. First the line, until a volunteer picks up the request. Then the work, which is short: the six pictures of a wash usually come back within 12 to 33 seconds of each other. The line is the long and unpredictable part. And it follows one thing far better than anything else: how many requests are already waiting for that particular model. The Horde's overall queue (often 600 or 700 requests) said almost nothing, because each computer only serves the models it has loaded.

So a machine announces:

```
line  = (10 s + 7 s per request waiting for this model) x a learned margin x 1.15 + 10 s
ritual = the time this machine usually needs to finish six pictures, + 8 s, + 12 s of spin (35 to 70 s)
wait   = line + ritual
```

The learned margin comes from every wash anyone has done on that machine in the last two weeks (its 30 most recent): the 85th percentile of how long the line really took compared to the rule, so that the announced time is one you will almost never go over. With few measurements it leans towards a cautious default.

During the wash, the countdown follows two rules.

- **In line, it only goes down.** If a volunteer picks you up early, the ritual takes what was left (up to 75 seconds), so the clock usually doesn't even jump: it keeps going down and reaches zero when the machine stops. If the line is slower than announced, the ritual can shrink to 35 seconds to absorb it.
- **If that is not enough, it says so.** The card reads "small delay: +30s", then "+60s" at most, never more than twice; after that it waits and says the line is slow tonight. Tapping the line explains it in full.

"Ahead" is the Horde's place in its queue multiplied by this model's share of that queue, because only this model's requests stand between you and its computers. It never goes up during a wash.

After each real wash, the site sends what it measured, without any identifier: the machine, the prompt, how it ended, the time announced, the line and the work as they really were, the state of the Horde when it started, and whether it was a phone. That is what the margins learn from. When you love a picture, the picture itself, its recipe and its seed are kept too, in a private store nobody can read through the site. You can switch all of this off in your profile.

## What the site sticks to

When you aren't doing anything, nothing runs. An earlier version crashed my Mac twice by animating all the time, so the room now comes alive through spaced-out events (a car going by outside, a neon flicker), and the only loops that run every frame are the ones for a wash in progress, which stop when the letters settle. Everything goes to sleep when the tab is hidden, and less happens if your system asks for reduced motion.

Every number on the screen comes from a measurement. Volunteer counts, queue sizes and wait times come from the Horde. Wash times come from washes. If there's nothing reliable to show, the display stays blank.

Nothing is for sale, and there are no ads, trackers or scores. Coins exist to keep things fair for the volunteers: you start with six, one comes back every hour, and a wash that fails or that you stop gives its coin back. If you have your own Horde key, washing costs no coin.

Every picture you download carries a small visible "AI · SIXFINGERS" mark and the IPTC metadata that labels it as made by an AI model (`trainedAlgorithmicMedia`), as the EU AI Act asks.

To go easy on the volunteers, pictures are small (384 pixels, or 320 when a model has few computers behind it) and drawn in 10 to 14 steps. A wash is six separate requests, so different volunteers can paint them in parallel and you watch them arrive one by one.

## How it is built

It has no dependencies and no build step: plain JavaScript modules served as they are, and one stylesheet.

The room is one photograph of a laundromat that I generated with an image model and retouched area by area, 6336 by 3564 pixels. The name plates are re-engraved by a script, and the few details on the machines (a note on Daydream, dried paint on Brushwork, an old photo on Photographic) were added with one edit of the daylight picture, then relit for sunset and night. Day, sunset and night are relit copies of that same picture, and each copy is cut into layers: the wall without machines, each drum without its door, each door on its own hinge, and an out-of-order version of every machine. At rest each machine is exactly the background, pixel for pixel; when it shakes or the door opens, the layers underneath show. One CSS transform scales the whole room to your screen, so every coordinate in the code is a pixel of that one image.

Everything that isn't the room is drawn in code, in whole pixels: the windows, the buttons, the icons, the coins, the letters in the drum. There is one pixel unit for the whole interface, so nothing has bigger or finer pixels than its neighbour. The typeface is my own, written in the code as rows of `#` and `.`, and accents are drawn once and placed on the letter, so an "é" can't drift away from its "e".

The drum is a little physics simulation: gravity at the scale of a real 50 cm drum, a wall that drags the letters by friction, three paddles, letters that collide and stack and roll over each other, and a spin cycle fast enough to pin them to the wall. The machine's shaking comes from the load. When the letters sit off-centre it wobbles, and every drop gives it a small knock.

The machine's sounds are real recordings released into the public domain on Freesound (washing, rinsing, spinning, draining, filling, the door unlocking, steam bursting), cut, looped and levelled by a script; the rest of the room (the street, the neon, the bell) is synthesised. Nothing loads before your first click. The radio in the corner plays six real stations and connects to nothing until you switch it on.

The site's code is private. The repository you're reading holds the parts that are meant to be open.

## What this repository is

This is the public side of SIXFINGERS. It holds no site code. It holds the catalogue of picture machines the site knows how to call, the rules a machine has to meet, the tools that check those rules, and the robots that answer proposals.

| Path | What's in it |
|---|---|
| `sources/` | The catalogue. Each machine is a small JSON record. `SCHEMA.md` explains every field in plain words. |
| `tools/check-source.py` | Checks a record against the same refusals the site applies. |
| `tools/cases.json` | 35 written records and whether each must be accepted. The python checker and the site's own checker are both held to this table. |
| `tools/words.py`, `words.json`, `words-cases.json`, `WORD-GUARD.md` | The word guard that keeps slurs out of public names, with a test table that is mostly real names it must leave alone. |
| `tools/read-proposal.py`, `proposal-cases.json` | Reads a proposal pasted into an issue and builds the record from it. |
| `.github/workflows/` | The robot that answers a proposal in about a minute, the check that runs on every pull request, and the one that writes `feed.json`. |
| `feed.json`, `moderation.json` | The feed of community machines and discussions, and a list that can only hide things from it. |
| `art/` | Pictures for this page and for links. |

Everything runs on the python3 that comes with macOS or Linux, with nothing to install:

```bash
python3 tools/check-source.py sources/*.json
python3 tools/check-cases.py
python3 tools/check-words.py
python3 tools/check-proposals.py
```

### Proposing a machine

The Horde runs well over a hundred image models, and every one of them is free and needs no key. The useful work here is deciding which ones are worth having and describing what they really do. A Horde machine is six lines:

```json
{
  "spec": 1,
  "kind": "horde",
  "id": "deliberate",
  "name": "Deliberate",
  "set": "Painterly",
  "model": "Deliberate",
  "note": "One sentence, on the object.",
  "what": "What comes back. Not what it promises.",
  "measured": { "on": "2026-08-26", "pack_seconds": 52.0 }
}
```

`measured` is optional and it's the most useful part. If you time a wash, write it down with the date.

[Propose one](../../issues/new?template=new-source.yml), or just [say something](../../discussions). You don't have to write the JSON yourself: the form asks the questions and the robot builds the record.

A record is data and never code. There is no field for a script or for an address to load, so there is nothing to run. Records that need a key, an account or a payment are refused, and so are addresses on your own network, redirects and plain `http`. Every image is redrawn in a canvas before it's kept. [`CONTRIBUTING.md`](CONTRIBUTING.md) has the details.

For now the laundromat ships its seven fixed machines. The community catalogue and the discussion wall were built for the Windows XP version and aren't plugged into the laundromat yet. They will come back once it has a back room for them.

## Thanks

To the volunteers of the [AI Horde](https://aihorde.net), who lend their graphics cards so that strangers can make pictures for free. Every picture on SIXFINGERS was painted on one of their machines. If you have a graphics card that sits idle, you can [lend it too](https://github.com/Haidra-Org/horde-worker-reGen).

To the people who recorded and gave away the sounds of the machine, all under CC0 on [Freesound](https://freesound.org): ilmari_freesound, afnan808, hansfbaier, ohrpilot, somatik7, PhilllChabbb, greatsoundstube, pengo_au and craigsmith.

To the people who trained and shared the seven models. Stable Diffusion 1.5 was developed by Robin Rombach and Patrick Esser. The Horde's pages for the other six don't name their authors, and I'd rather leave a blank than guess: Deliberate, Anything Diffusion, Anything V5, Dreamshaper, AbsoluteReality and ICBINP.

## Support

The site will stay free. If you'd like to help keep the machines running, you can leave a tip on [Ko-fi](https://ko-fi.com/tristanulrich). If tips ever add up, they'll pay for a computer that works for the Horde, so the site gives back some of what it uses.

## Contact

tristanulrichlobey@gmail.com, or open an [issue](../../issues).

## Licence

Copyright (c) 2026 Tristan Ulrich. All rights reserved.

SIXFINGERS is not open source. The site, its code, its artwork, its own sounds, its typeface and its name are not licensed to anyone (the recordings credited above stay in the public domain). This repository is public so that you can read the catalogue, run the checkers and propose a machine; [`LICENSE`](LICENSE) says exactly what that allows, and nothing beyond it.
