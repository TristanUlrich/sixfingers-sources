# The grey squares: debugging a GPU memory ceiling on mobile

This is an engineering write-up of the hardest problem I solved while building [SIXFINGERS](https://sixfingers.art), a browser-based image-generation site dressed as a laundromat. You move through a room that is a single photograph, six thousand pixels wide, by panning and zooming it. On a desktop it was smooth. On a mid-range Android phone it broke, in a way that took me two weeks to understand, because the fix was not a smaller version of what I kept trying. It was a different way of building the room.

The bug is worth writing down for its shape rather than its details. It is a precise example of the difference between making an architecture cheaper and choosing an architecture the platform was built to run, and of how long you can make real progress on the first while the second is what actually needs to change.

## The scene, and why it is heavy

The laundromat is not drawn in code. It is one photograph of 6336 by 3564 pixels that I generated and then retouched area by area, relit into day, sunset and night versions, and cut into layers: the wall without its machines, each drum without its door, each door on its own hinge, and an out-of-order version of every machine. At rest, a machine is simply part of the photograph. When it shakes, opens or washes, its layers are composited back on top, aligned to the pixel.

The whole room lives in a page element of that full size, and a single CSS transform scales and translates it to fit your screen. That one decision, a very large element moved and scaled with a transform, is the root of everything that follows. It is also what kept the rest of the site simple, because every coordinate in the code is then just a pixel of that one image. The cost of it was invisible on the hardware I developed on, and it fell entirely on the device least able to pay it.

## The symptom: artifacts that only appeared on real hardware

The bug reported itself as grey rectangles. During a zoom, while sliding from one machine to the next, or on the way back from a full-screen page, parts of the room would turn into flat grey patches, occasionally black, and repaint themselves roughly half a second late. The effect compounded over time: the longer a session ran, the more often it happened. One machine washing was fine; two produced occasional artifacts; three made the site unusable, and the whole thing turned choppy alongside the flicker.

The obstacle was that I could not reproduce it anywhere I could inspect it. On my Mac, in desktop Chrome, the room was flawless. The headless browsers I used for automated checks reported healthy frame times. Only the phone showed the fault, and a phone is the worst place to attach a profiler. That gap between environments was itself the first real clue, and I spent a week stepping over it: a defect that appears only under constrained memory, and only on a high-density display, is rarely a logic error. It is usually a resource ceiling that the roomy machines never reach.

## Seeing a bug I could not profile

For the first week the real problem was observation, not analysis. I could not fix what I could not watch, and the fault refused to appear anywhere I could instrument it, so before diagnosing anything I had to build the means to see it on the one device that showed it.

Three tools did that. The first was a self-diagnostic mode: a `?diagnostic` switch that makes the phone measure itself (frame times, memory, which subsystems are live) and post the report back to the site's feedback table, so that I could read on the desktop what the phone had recorded in my hand. The second was a set of elimination switches, `?sans=scene|anim|pixel|toiles`, each of which turns off one subsystem (the room, the animations, the pixel interface, or the canvas layers), so I could bisect which part produced the artifacts instead of guessing. The third was filming the GPU rather than the DOM. The browsers I could automate were the wrong instrument twice over: a headless browser has no real GPU and never tiles under memory pressure, and the app's embedded browser freezes its animations the moment it is hidden, so any smoothness it reports is fiction. The only faithful record was a screen capture of the real device under real load, taken over a USB debug bridge to the phone.

That produced the observation the whole fix turned on. The phone's frame times were fine: its GPU was fast, with almost no slow frames. The fault was purely visual, grey and black tiles appearing and being repainted late. A performance problem shows up as slow frames; this one did not. That single fact pointed away from "too expensive to compute" and toward "out of memory to display", and it is the fact my averaged, desktop-side tools had been quietly hiding from me for a week.

## Two weeks of correct fixes that changed nothing

Before I understood that, my approach was ordinary performance discipline, and on its own terms it worked. I profiled the page, found the most expensive operations, and brought their cost down, across roughly fifteen releases from 5.10 to 5.25:

- I stopped the machine halos and the neon from existing in the layout when they were not lit, instead of painting them and hiding them.
- I replaced every colour filter with a plain shadow, which cut the drawing work during a wash by about 43 percent, because a CSS filter forces the browser to re-rasterize the area it covers on every frame.
- I freed the large full-screen canvas used for the door-burst effect immediately after it played, instead of keeping it allocated.
- I hid the entire room underneath any full-screen page, which handed roughly 87 MB back to the system while a page was open.
- I made off-screen machines stop computing their physics and animation entirely.
- I stopped redrawing the interface icons every frame; they are now drawn once and placed as images, which took the collection screen from 59 separate graphics layers down to 13.

Every one of those changes was real, measurable, and an improvement, and each new version scored a little better on the bench. After every single one, the report from the phone was identical: the grey squares are still there. That pattern, a series of individually correct optimizations that keep moving the benchmark and never move the symptom, is the part worth keeping. It is the signal that you are tuning inside the wrong structure, where every change pays off on paper and fails in the hand. I treated it as a backlog of things to make cheaper for a week and a half before I let myself ask whether the structure itself was the fault.

## The root cause: how a browser rasterizes a large, scaled surface

A browser does not paint a page as one bitmap. It divides the painted content into tiles, rasterizes the ones it expects you to need, and keeps them in a bounded pool of GPU memory. It holds a budget for the tiles currently on screen and a second, larger budget for a margin around them, so that scrolling feels instant. When what you are looking at demands more tiles than the pool allows, the compositor evicts tiles and shows a placeholder, a flat grey fill, until it can rasterize them again. In Chromium this logic lives in `cc/tiles/tile_manager.cc`, and the artifact has a name: checkerboarding.

Apply that to my room. It is a single element of 6336 by 3564 pixels. On a phone with a device pixel ratio of 3, scaling that element up during a zoom asks the compositor to rasterize an enormous area at the screen's true resolution; panning across it continuously invalidates and requests fresh tiles; opening a page on top takes memory from the pool the room depends on; and every machine that moves dirties more of the surface. Each interaction I had built was, to the compositor, a request to raster more of a surface that was already too large to hold. The phone was not slow. It was out of tiles, which is exactly the shape the diagnostics had shown: fast frames, late grey fills.

This is also why the desktop hid the problem. On a machine with plenty of RAM, Chrome rasterizes generously far beyond the viewport: I measured it holding around 260 MB of tiles after a single zoom, well within what that machine could spare, so the ceiling was never reached and nothing went grey. The headless browsers hid it more simply still: with no real GPU and no real memory pressure, they never tile under constraint at all. The only honest test environment was the phone.

None of my optimizations had changed any of this. They each lowered the total memory the page used, which is why the bench improved, but not one changed the fact that the room was a giant surface built to be tiled. I was lowering the water level in a tank with a hole in the bottom. The right question was never how to use less memory; it was whether a zoomable, pannable, full-bleed photograph should be a tiled DOM surface at all. Figma answered that same question in 2015 when they moved their canvas off the DOM, on the grounds that the DOM is built to scroll, not to zoom. I had arrived at their conclusion from the far end of it, two weeks late.

## The rebuild: the room as a single GPU texture

The fix was to stop asking the browser to tile the room, and to hand the photograph to the GPU the way a game engine does.

The room is now uploaded once as a WebGL texture. A canvas the exact size of the screen draws that texture wherever the camera is looking. There are no tiles to rasterize, evict or repaint, because there is no large surface in the page any more: there is a screen-sized canvas and a texture resident in GPU memory. Panning and zooming no longer invalidate anything; they change three numbers (a zoom factor and a two-dimensional offset) that the GPU applies while sampling the texture. The room's camera is driven by the site frame by frame, with the same easing curves and durations as before, so the photograph and the composited machine layers move together with no drift.

The layer approach survives, sharpened. A machine is drawn as its own element only while it is actually moving: shaking, opening, washing, glowing or selected. At rest it is the texture, pixel for pixel, so nothing is composited over the room at all, and when a machine does need to move, its parts are cut from a strip four times smaller than the full photograph. That is what kept the composited-layer count low without losing any motion.

The renderer is also built to fail safely. If the device cannot give a WebGL context, or the GPU drops the one it gave, the old page-based photograph is still present underneath and takes over with no visible gap, and a `?gl=0` switch forces that old path so the two can be compared directly. The new path is progressive enhancement, not a hard dependency: the room that was too slow to keep is now the safety net under the room that replaced it.

## Inside the renderer

The whole module is about 160 lines and uses no library. Its core idea is that the camera is not geometry; it is a handful of uniforms the vertex shader applies to one rectangle.

```glsl
// a is a corner of the unit quad (0,0 .. 1,1); t is the room's size in pixels;
// u is the camera: u.z = zoom, u.xy = top-left offset on screen.
attribute vec2 a; uniform vec3 u; uniform vec2 t; uniform vec2 ecran; varying vec2 v;
void main() {
  vec2 p = a * t * u.z + u.xy;                 // place this corner on screen
  v = a;                                       // and remember where to sample the photo
  gl_Position = vec4(p.x / ecran.x * 2.0 - 1.0, 1.0 - p.y / ecran.y * 2.0, 0.0, 1.0);
}
```

Because the camera is computed in the shader, a pan or a zoom never rebuilds geometry and never touches the page. It writes three floats. The fragment shader is then as small as a shader gets: for each pixel on screen, read the matching pixel of the photograph.

```glsl
precision highp float;
uniform sampler2D s; varying vec2 v;
void main() { gl_FragColor = texture2D(s, v); }
```

The draw runs only when the camera actually moves, never at rest. This is a rule the whole site keeps, because an earlier version crashed my Mac twice by animating while nothing was happening, and it is also what keeps the renderer from draining a phone battery to hold a still image. A frame is requested on demand and coalesced, so ten camera updates in one tick still paint once:

```js
function peindre() {                 // peindre: paint one frame
  if (perdu || !prog) return;        // perdu: the GPU context was lost
  gl.clear(gl.COLOR_BUFFER_BIT);
  if (!tex) return;
  gl.uniform3f(uU, cam.x, cam.y, cam.e);   // push the camera
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);  // one quad, four vertices
}
const plusTard = () => { if (!demande) demande = requestAnimationFrame(peindre); };
```

Uploading the photograph is the one slow step, so it is kept off the main thread and out of the way of interaction. The image is decoded with `createImageBitmap`, which runs off-thread, and only then uploaded in a single call. The previously uploaded texture stays on screen until the new one is fully ready, so switching the room from day to sunset never shows a blank frame. On WebGL 2 the texture also gets mipmaps, the pre-computed smaller copies a GPU blends between (`LINEAR_MIPMAP_LINEAR`, trilinear filtering), so the room seen from far out does not shimmer as you slide across it.

```js
const bm = await createImageBitmap(await (await fetch(url)).blob()); // decode off-thread
if (bm.width > gl.getParameter(gl.MAX_TEXTURE_SIZE)) return false;   // refuse an oversized image
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, bm);
if (v2) { gl.generateMipmap(gl.TEXTURE_2D);                          // clean minification
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); }
if (tex) gl.deleteTexture(tex);                                      // only now drop the old one
tex = t;
```

The size check on that second line is not only housekeeping. The same site reads the dimensions of every generated picture out of its first bytes before decoding it, and refuses anything over 4096 pixels or 12 MB, because a crafted 10 KB file can expand into gigabytes and take the tab down; here the same instinct refuses a texture larger than the GPU's maximum rather than crashing on it.

The last piece is what makes a GPU renderer safe to depend on at all: the context can vanish. A phone going to sleep, switching apps, or simply running low on memory will take the WebGL context away and fire an event, and a renderer that does not listen for it silently goes blank. SIXFINGERS listens, falls back to the page photograph in the meantime, and rebuilds the program and re-uploads the texture when the context returns.

```js
cv.addEventListener('webglcontextlost', e => { e.preventDefault(); perdu = true; tex = null; });
cv.addEventListener('webglcontextrestored', () => { perdu = false; compiler(); poser(source); });
```

## Trade-offs and limits

Moving the room to the GPU is not free, and it is worth being exact about what it costs.

Accessibility and page semantics are untouched, by design. The texture canvas is purely decorative and marked `aria-hidden`; every interactive and readable element (the machine cards, the buttons, the prompt line, the generated pictures with their text alternatives) stays in the DOM layer composited on top, exactly as before. The change moved how one decorative image is drawn, nothing a screen reader or the keyboard ever touches.

The safety net has a price. Keeping the old page-photograph underneath, so the renderer can fail without a hole, means the medium-resolution image is effectively loaded twice at startup: once as the fallback, once as the texture source. I judged a safe failure worth one extra decode of an image that was already on its way down. Mipmaps make a similar trade: generating them adds about a third to the texture's GPU footprint, in exchange for a room that does not shimmer while you pan. On a device this constrained that was the right side of the trade; on a far larger texture it might not be.

And it is not perfect. A few small stutters remain when sliding quickly between machines, and the renderer depends on WebGL being present, which is the reason the DOM fallback exists at all rather than being deleted once the new path worked.

## Measured impact

Measured at the size of my phone, read from Chrome's own compositor memory counters in a tracing capture, so the figures are the browser's accounting rather than an estimate of mine:

| Moment | Before (tiled DOM) | After (GPU texture) |
|---|---|---|
| The room at rest | 136 MB | 71 MB |
| Zoomed in on a machine | 250 MB | 87 MB |
| Sliding between machines | 290 MB | 137 MB |

These are point-in-time measurements on one device, and GPU memory figures move with the browser version, so I read them as the shape of the win rather than exact constants. The shape is the point: the two peak cases, zoom and pan, which were the ones that went grey, each dropped by roughly two thirds, and all three moments now sit under the budget the phone could actually hold.

## Verifying the visuals did not change

A rewrite of the rendering path is only acceptable if the result is identical, so I checked that it was instead of trusting it. I compared the old and new room screen by screen: under 0.5 percent of pixels differ, and only along the edges, where sampling a texture and tiling a DOM element round the last fraction of a pixel differently. I also recorded a full wash frame by frame on both paths, to confirm the machine layers still line up with the photograph during motion, which is the one place a sub-pixel camera mismatch would show.

On the phone, the grey squares were gone. The site is smoother everywhere, including on the desktop it was already fine on. For the first time the app is genuinely usable on a phone, which is where most people open it.

## The lesson: fix the shape before the details

The useful part of this is not WebGL. It is the week and a half before it.

When a run of individually correct optimizations keeps moving the benchmark and never moves the symptom, the problem is no longer in the details, and more tuning inside the wrong structure will go on paying off on paper and failing in the hand. The faster path was a different question, asked earlier: not "what here costs too much?", which always has an answer and always feels like progress, but "did I build this in a shape the platform is built to run?". The grey squares were never a defect to be whittled down. They were the platform refusing the one thing it is worst at, a huge surface zoomed and panned on a device with little memory to spare, and the only real fix was to stop asking it.

The full internal note on the renderer, and the engine itself, are in the private repository. This repository is the open side of SIXFINGERS: it holds the story and the parts meant to be read, not the site's source. You can see the result at [sixfingers.art](https://sixfingers.art).

---

*More engineering notes: [The honest countdown](wait-time.md) · [The word guard](../tools/WORD-GUARD.md) · [all notes](README.md)*
