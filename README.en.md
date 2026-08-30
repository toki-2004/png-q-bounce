# png-q-bounce

> **Language:** English | [简体中文](README.md)

Turn a single PNG into a **one-shot button-press GIF**: a gentle press-down
(uniform scale) with a slight overshoot on release, scaling from the center.
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
| `--duration` | 500 | Total animation duration in ms (exactly 0.5 s); lower is faster |
| `--amplitude` | 1.0 | Press depth; 1.3 ≈ deeper press, 0.6 ≈ subtler |

## How it works

* 12 frames of button-style press-and-release (exactly 0.5 s): uniform
  center scaling with a slight overshoot on release.
* **The first frame matches the original resolution exactly**: the GIF canvas
  equals the PNG size and frame 1 is a 1:1 copy of the original pixels.
* **Plays once**: no GIF NETSCAPE loop extension is written, so browsers,
  image viewers and Qt QMovie stop on the last frame (the original image).
* Transparency is preserved (reserved palette index + disposal=2), so the
  result overlays cleanly on the desktop.

## Requirements

* Python 3 + [Pillow](https://pypi.org/project/Pillow/) (`pip install pillow`)

## License

MIT License, see [LICENSE](LICENSE).
