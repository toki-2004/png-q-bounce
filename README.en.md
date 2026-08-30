# png-q-bounce

> **Language:** English | [简体中文](README.md)

Turn a single PNG into a **one-shot bouncy ("Q") GIF**: a bottom-anchored
squash → stretch → decaying wobble that settles back to the original image.
The animation **plays exactly once** (players stop on the final frame), and
transparency is preserved.

Typical use: make an interaction animation skin for the
[desktop-pet](https://github.com/toki-2004/desktop-pet) — drop a static PNG
skin in, get a play-once GIF ready for `pet_interact_image`.

## Usage

```bash
python qbounce.py skin.png                     # writes skin_q.gif
python qbounce.py skin.png -o bouncy.gif       # explicit output
python qbounce.py skin.png --amplitude 1.3     # exaggerate the bounce
python qbounce.py skin.png --duration 40       # faster timing (ms per frame)
```

You can also drag a PNG onto `拖拽转换.bat`.

A standalone `png-q-bounce.exe` is available on the [Releases](https://github.com/toki-2004/png-q-bounce/releases) page - no Python required.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `--duration` | 55 | Milliseconds per frame; lower is faster |
| `--amplitude` | 1.0 | Bounce intensity; 1.3 ≈ more dramatic, 0.6 ≈ subtler |

## How it works

* 7 frames of decaying wobble: squash (wider) → stretch (taller bounce) →
  settling back to the original size, anchored to the bottom edge.
* **Plays once**: no GIF NETSCAPE loop extension is written, so browsers,
  image viewers and Qt QMovie stop on the last frame (the original image).
* Transparency is preserved (reserved palette index + disposal=2), so the
  result overlays cleanly on the desktop.

## Requirements

* Python 3 + [Pillow](https://pypi.org/project/Pillow/) (`pip install pillow`)

## License

MIT License, see [LICENSE](LICENSE).
