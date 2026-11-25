# Engineering notebook

Write-ups on how [SIXFINGERS](https://sixfingers.art) is built, each with the measurements and the real code. The site's own source is private; these are the parts meant to be read.

| Note | What it covers |
|---|---|
| [The grey squares](grey-squares.md) | A GPU memory ceiling that only showed on a real phone, and the WebGL texture that replaced a tiled DOM surface. Debugging a device you cannot profile, and fixing the shape of a thing rather than its details. |
| [Two worlds](two-worlds.md) | A photographic room over an interface built entirely in whole pixels, with a typeface written in the source as a grid of `#` and `.`. The single rule the whole visual system follows. |
| [The honest countdown](wait-time.md) | Estimating a trustworthy wait over the AI Horde's volunteer render queue: a model refit nightly from real washes, and a countdown built never to lie. |
| [The word guard](../tools/WORD-GUARD.md) | A homoglyph-aware content defence that keeps the site from printing a slur in its own chrome, held to a written table of 297 cases, and careful never to refuse a real name. The code is public, here in this repository. |

## Assets

- [`img/`](img/) — the architecture diagram and the wash animation used in the README.
- [`screenshots/`](screenshots/) — the room at each time of day, the machine card, a wash, the collection, the phone and tablet layouts.

Back to the [project README](../README.md).
