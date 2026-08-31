# The word guard

**A small, measured defence against one thing only: SIXFINGERS printing a racist
word or a call to hatred in its own chrome, or saying one out loud under its own
robot's name.**

It is not a profanity filter and it is not moderation. Ordinary swearing is
deliberately let through. GitHub does the moderation of what people write on the
wall, because GitHub has staff and a reporting pipeline and this project has one
person who does not write code.

Everything below is either in this repository or measured against it.

| | |
|---|---|
| the list | [`tools/words.json`](words.json) — 52 entries, 5 languages, 6 categories |
| the two readers | [`tools/words.py`](words.py) here, `js/words.js` in the site |
| the written table | [`tools/words-cases.json`](words-cases.json) — 297 cases |
| the runner | [`tools/check-words.py`](check-words.py) — 357 checks, on every push |

---

## The rule that shapes everything

> **A guard that refuses somebody's real name does far more harm than a word that
> gets through.**

The textbook failure has a name: the *Scunthorpe problem*, after the English town
that 1990s filters refused because of the four letters in the middle. Real people
are called Nègre, Cockburn, Fagg, Dickinson, Bitton, Kiké or Penistone. Real people
are Nigerian or Nigerien. Refusing their name tells them the site finds them
obscene.

So a word enters the list only if it is **all three** of:

1. unambiguously a racist insult, a call to hatred, or a nazi slogan. Not rude, not
   coarse, nothing merely sexual;
2. not a surname, a first name, a place or a demonym. If it is also an ordinary
   word it may still enter, but only as a whole-word match, and the collision is
   written down next to it;
3. at least five letters once folded, when it is matched anywhere in a text. Below
   that, a run of letters turns up inside too many ordinary words.

`words.json` carries a `kept_out` section listing the words that were considered
and **rejected by these rules**, with the reason. *negro* is the ordinary Spanish
and Portuguese word for the colour black. *retard* is the ordinary French word for
lateness. *dyke* is a sea wall and the surname Van Dyke. *żyd* is the ordinary
Polish word for a Jewish person, so **only the Cyrillic form is refused**.

---

## Two tiers, because certainty is not uniform

| tier | what it means |
|---|---|
| **refuse** | unambiguous. The site will not print it; the robot will not pass it on. |
| **review** | probably hate, but the entry collides with something ordinary. A person decides, not a machine. |

The review tier is what lets the list be wide without paying for it. *chink* is a
serious slur and also an ordinary English noun in "a chink in the armour".
*redskin* is a slur and a potato. *tranny* is a slur and a gearbox. `1488` is a
neo-nazi code and also, once every few centuries, a date. All of those are held for
a human instead of being refused by a machine, and all of them are listed in
`known_collisions` in the same file.

**A trade that is written down can be reversed by deleting one line. A silent one
cannot.**

---

## What it defends against, and what it measured

Six disguises were tried against the previous version on 31 August 2026. **Four
walked straight through**, because unknown letters were simply deleted, which
turned the word into a harmless neighbour.

| disguise | before | now |
|---|---|---|
| the word in the clear | refused | refused |
| a Cyrillic `і` in place of the latin one | **passed** | refused |
| a Cyrillic `е` | **passed** | refused |
| fullwidth letters `ｎｉｇｇｅｒ` | **passed** | refused |
| mathematical letters `𝘯𝘪𝘨𝘨𝘦𝘳` | **passed** | refused |
| a zero-width character in the middle | refused | refused |
| Cherokee capitals in a slogan | *not tried* | refused |
| Armenian `հ` for `h` | *not tried* | refused |

### The six passes

1. **bare, anywhere.** The text is compatibility-normalised, lowercased, stripped
   of accents, its lookalike letters mapped back to latin, its digits put back as
   letters, and everything that is not a letter removed. Repeats are kept.
2. **folded, anywhere.** The bare form with runs of one letter collapsed, to catch
   `niiiggger`. Only for entries of five letters or more, and only when no rendered
   word explains the collision: folded, the English insult and the country *Niger*
   land on the same string, which is what the `allowed` list is for.
3. **slogan.** An entry written with spaces is matched against **whole words in a
   row**. Gluing the words together instead would find *race war* inside *race
   warmup*, and *sale negre* inside *wholesale negrete*.
4. **word.** The entry has to be a whole word. Reserved for short entries and for
   words that are also ordinary English, so that raccoon, tycoon, Pakistan,
   Maricopa and a transmission are left alone.
5. **script.** A substring of the non-latin form, for entries that are not written
   in latin at all.
6. **code.** A numeric hate code, matched as a whole run of digits and never as a
   substring, because 88 sits inside a great many perfectly ordinary numbers. The
   digits are glued back together with their seams kept, so `1488`, `14 88` and
   `14/88` all count the same while `14880` and `31488` do not.

### The lookalike table is not hand-written

It is derived from the **Unicode Security Mechanisms confusables data (UTS #39,
version 17.0.0)**. Every single character in that file is joined to its prototype in
one equivalence class; a class that resolves to exactly one ASCII letter maps all of
its members to that letter; **a class that resolves to more than one letter is
dropped as unsafe**. Characters that normalisation already reduces are left out as
redundant, and both cases of each character are listed because the text is
lowercased before the table is applied.

That yields **651 characters** from Cyrillic, Greek, Cherokee, Armenian, Coptic,
Canadian Syllabics, Lisu, Warang Citi and others, in 23 kB. The Unicode data files
are © Unicode, Inc.; see <https://www.unicode.org/terms_of_use.html>.

### What is deliberately not done

**No fuzzy matching.** Edit distance one from the English insult includes *bigger*,
*digger* and *trigger*. Every pass here is aimed at a **deliberate disguise**, never
at a typo, and that is why none of them guesses.

**No third-party word list.** The two obvious ones were read and not used.
[HurtLex](https://github.com/valeriobasile/hurtlex) is CC BY-NC-SA, which a project
reserving all rights cannot absorb, and
[LDNOOBW](https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words)
is CC BY. More to the point, both are lists of **profanity**, and this guard's own
test table requires *merde*, *connard*, *fuck* and *cabrón* to pass. They were read
as a map of the territory; every entry here was judged against the three rules
above.

---

## How it is held to account

Neither reader is the reference. **The written table is.**

| | |
|---|---|
| **83** cases that must be refused | each family, plus disguises, lookalikes, other alphabets, codes |
| **13** cases that must be *held*, never refused | the known collisions |
| **191** cases that must **pass** | Scunthorpe and its neighbours, surnames and first names from about twenty cultures, ordinary words in a dozen languages, swearing that must get through, and the specific collision of every whole-word entry |
| **10** cases on the machinery | that folding folds, that an unknown digit never erases the word |
| **the audit** | every entry in the list must catch **at least itself**, and no entry under five letters may be matched anywhere |
| **the mirror** | seven comparisons between the site's copy of the list and this one, the whole table included |
| **the project's own words** | the guard is run over every word this repository says in public. **1135 distinct words, none refused.** |
| **the cost** | **1 to 1.5 ms** for one ordinary sentence, printed by the checker on every run |

The site's own bench, `tools/words-selftest.html`, fetches this table and this list
**live from this repository** and holds the browser side to them. If it cannot reach
the network it falls back to its committed copies **and says so in yellow**, because
a green result that only proves a file agrees with itself is worse than a red one.

---

## Where it runs

- **In the site**, on account names, so the site never prints one in its own chrome.
- **In the robot that answers proposals**, before the record is even described. If a
  proposal carries hate, the answer says so in one line and repeats none of it: a
  human should not have to read the insult to know it arrived.

## Where it does not run yet

On the text of the wall itself: titles, account names and comments coming from
GitHub. That is the next piece of work, and it is written down rather than
forgotten.

---

## Its limits, stated plainly

**Five languages, not fifty.** English, French, German, Spanish, and Russian in
Cyrillic. Rule 2 knocks most candidates out: in Portuguese *macaco* and *preto* are
ordinary words; in Arabic the obvious candidate is part of a great many first names.
Adding a language properly needs somebody who speaks it, not a translation engine.
**That is the one part of this project where outside help would genuinely beat us.**

**It judges strings, not meaning.** A proposal quoting a slogan in order to condemn
it is refused exactly like one endorsing it. The review tier softens this; it does
not remove it.

**It is a guard, not a shield.** Somebody determined to write hate can write it in a
way no list catches. What this stops is the project repeating it.
