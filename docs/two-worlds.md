# Two worlds: a photographic room over an interface built in whole pixels

Most of the engineering notes in this repository are about a single hard problem. This one is about a rule that runs through the whole of [SIXFINGERS](https://sixfingers.art) and decides how almost every pixel on the screen is made. The page is two layers that are not allowed to touch: a photograph of a laundromat, and an interface drawn entirely in whole pixels on top of it. Keeping them strictly apart is what makes the site look like one deliberate object rather than a website with a nice background.

The reason it is built this way is the thing the site is about. Image models from the early era get the composition of a picture right and the anatomy wrong, which is where the six fingers and the name come from. The frame around that should feel like it belongs to the same moment: a worn machine you operate, not a modern web app. So the room is a real, slightly grubby photograph, and everything you touch is made of the same coarse pixels as the six-finger cursor.

## The room is a photograph, never CSS

The laundromat is one image of 6336 by 3564 pixels, generated with an image model and then retouched area by area: the neon, the INSTRUCTIONS sign, the names on the machine plates, the coin slot. It is relit into day, sunset and night, and each version is cut into layers (the wall without its machines, each drum without its door, each door on its own hinge, an out-of-order version of every machine). At rest a machine is simply part of the photograph, pixel for pixel; its own layers are composited back only while it shakes, opens or washes. How that photograph is drawn without tiling artifacts, and why it became a GPU texture, is its own note: [The grey squares](grey-squares.md).

The rule for the room is that nothing in it is ever drawn in code. An object that belongs in the laundromat (a note stuck to a machine, a coin slot, dried paint) is painted into the photograph and relit with it. It is never a CSS box dressed up to look photographic, because a drawn object next to a real one reads instantly as fake, and it was refused more than once for exactly that reason.

## The interface is whole pixels, at one size

Everything that is not the room (the windows, the buttons, the icons, the coins, the prompt line, the letters that fall into the drum) is drawn in code, in whole pixels. The system behind it is deliberately small:

- **One pixel unit.** A single unit, `--u`, is computed once from the screen and used for every measurement in the interface, so nothing has bigger or finer pixels than its neighbour. On a phone it is counted in real device pixels, because otherwise everything came out enormous. Only the large numerals step up to double.
- **Stepped corners, not smooth ones.** There is no `border-radius` in the interface on a desktop. Corners are quarter-circles built out of whole-pixel steps, so a rounded corner is made of the same pixels as everything around it instead of a smooth curve that gives the grid away.
- **Hard shadows, no blur.** Depth is one-unit hard shadows, offset and sharp. No blurred shadow, no filter on a window or a card or a picture in flight; those were removed because, on a phone, each of them forces the browser to repaint every frame.
- **Colours taken from the photograph.** The interface palette is sampled from the room: the cream of the tiles, the near-black of the grout, the pink of the neon. Each machine then lends its own colour to its card, its button and its numbers. The background is never pure black; it is the warm near-black of the room.

## The typeface is written in the code

The most literal expression of the rule is the font. A pixel font taken from the internet is one everybody has seen on a hundred other sites, so SIXFINGERS has its own, and it is not a font file that happens to sit in the repository. It is a grid, written out letter by letter in the source as rows of `#` and `.`, read and corrected by hand:

```js
const G = {
  A: ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
  B: ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
  a: ['....', '....', '.##.', '...#', '.###', '#..#', '.###'],
  g: ['....', '....', '.###', '#..#', '#..#', '#..#', '.###', '...#', '.##.'],
  // capitals sit on seven rows, lowercase on five, descenders drop two more
};
```

A build step turns those grids into a real web font (`sixfingers.woff2`), where each `#` becomes a square, so the text renders crisply at any size for which a font pixel lands on a whole number of screen pixels. Accents are not drawn into the letters. An `é` is an `e` with an acute accent placed above it by the code, so the accent can never drift away from the `e` the way it would if every accented letter were its own little drawing. The in-page icons are built the same way, on a grid of about eleven by eleven, with a one-pixel outline and a one-pixel shadow added in code so every icon carries the same weight.

## The rule that holds it together

Two worlds, and they never mix. No object of the room is drawn in code, and no pixel of the interface is laid onto the photograph pretending to belong to it. No realistic reflection on a button, no photographic frame around a window, no smooth curve in the interface, and no flat pixel shape sitting in the scene. The scene moves like filmed objects, on springs and with weight; the interface moves in steps of one pixel, buttons that lift and press and icons that hop. Each world keeps its own physics.

This is as much a list of refusals as of choices, and that is the point. A single unit, a single hand-made font, a single source for the palette, and a hard line between the photograph and the pixels: held strictly, they read as one intentional object. The moment any of them is relaxed, a smooth corner here, a stock font there, a drawn object in the photo, the whole thing starts to read as a template with a theme on top. The consistency is not decoration. It is the difference between a made thing and a configured one.

The interface and the font live in the private repository (`js/laverie/pixel.js`, `js/laverie/police.js`). This repository is the open side of SIXFINGERS: it holds the write-ups and the parts meant to be read, not the site's source. You can see both worlds at [sixfingers.art](https://sixfingers.art).

---

*More engineering notes: [The grey squares](grey-squares.md) · [The honest countdown](wait-time.md) · [The word guard](../tools/WORD-GUARD.md) · [all notes](README.md)*
