# -*- coding: utf-8 -*-
"""png-q-bounce：把一张 PNG 做成 Q 弹（果冻挤压回弹）的 GIF。

Q 弹动画 = 底部锚定的挤压/拉伸摇摆（squash & stretch），幅度逐帧衰减，
最终回到原始尺寸静止。生成的 GIF **只循环播放一遍**（不写入 NETSCAPE
循环扩展，各端播放器播完即停在最后一帧=原始画面）。

用法：
    python qbounce.py input.png [-o output.gif] [--duration 55] [--amplitude 1.0]

也支持把 PNG 直接拖到 拖拽转换.bat 上使用。
"""

import argparse
import os
import sys

from PIL import Image

# (水平缩放, 垂直缩放, 底部基准的垂直偏移占原高比例)：挤压 → 回弹 → 衰减 → 静止
WOBBLE = [
    (1.00, 1.00, 0.000),
    (1.12, 0.88, 0.040),   # 落地压扁
    (0.94, 1.10, -0.030),  # 弹起拉长
    (1.06, 0.94, 0.018),
    (0.97, 1.03, -0.008),
    (1.02, 0.98, 0.004),
    (1.00, 1.00, 0.000),
]
DEFAULT_DURATION_MS = 55


def build_frames(img, amplitude=1.0, headroom=1.25, side=1.20):
    """返回 (帧列表, 画布尺寸)。底部锚定：挤压时底边贴住画布底、向两侧变宽。"""
    img = img.convert("RGBA")
    w, h = img.size
    cw = max(1, int(round(w * max(1.0, side))))
    ch = max(1, int(round(h * max(1.0, headroom))))
    baseline = ch  # 底边基准线
    frames = []
    for sx, sy, dy_ratio in WOBBLE:
        sx = 1.0 + (sx - 1.0) * amplitude
        sy = 1.0 + (sy - 1.0) * amplitude
        dy = dy_ratio * amplitude
        nw = max(1, int(round(w * sx)))
        nh = max(1, int(round(h * sy)))
        scaled = img.resize((nw, nh), Image.LANCZOS)
        frame = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        x = (cw - nw) // 2
        # 底边锚定在 baseline，dy<0 表示向上弹起
        y = baseline - nh + int(round(h * dy))
        frame.alpha_composite(scaled, (x, y))
        frames.append(frame)
    return frames, (cw, ch)


def to_p_frame(frame, transparent_index=255):
    """RGBA → P 模式（255 色 + 索引 transparent_index 作全透明），保住透明背景。"""
    alpha = frame.getchannel("A")
    mask = alpha.point(lambda a: 255 if a <= 16 else 0)  # 255 = 需要透明的像素
    p = frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    p.paste(transparent_index, mask)  # 透明像素统一指向保留索引
    return p


def make_gif(in_path, out_path, duration=DEFAULT_DURATION_MS, amplitude=1.0):
    img = Image.open(in_path)
    frames, _ = build_frames(img, amplitude=amplitude)
    p_frames = [to_p_frame(f) for f in frames]
    # 不传 loop 参数 → 不写入 NETSCAPE 循环扩展 → 播放器只播一遍即停在末帧
    p_frames[0].save(
        out_path, save_all=True, append_images=p_frames[1:],
        duration=duration, disposal=2, transparency=255, optimize=False,
    )
    return out_path


def main():
    ap = argparse.ArgumentParser(description="把 PNG 做成只播一遍的 Q 弹 GIF")
    ap.add_argument("input", help="输入 PNG 路径")
    ap.add_argument("-o", "--output", help="输出 GIF 路径（默认同名 _q.gif）")
    ap.add_argument("--duration", type=int, default=DEFAULT_DURATION_MS,
                    help="每帧毫秒数（默认 55）")
    ap.add_argument("--amplitude", type=float, default=1.0,
                    help="Q 弹幅度系数（默认 1.0，越大越夸张）")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print("Error: file not found: {}".format(args.input))
        sys.exit(1)
    out = args.output or os.path.splitext(args.input)[0] + "_q.gif"
    make_gif(args.input, out, duration=max(20, args.duration),
             amplitude=max(0.1, args.amplitude))
    size = os.path.getsize(out)
    print("OK: {}".format(out))
    print("   {} frames, {:.1f} KB".format(len(WOBBLE), size / 1024))


if __name__ == "__main__":
    main()
