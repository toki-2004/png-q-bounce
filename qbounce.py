# -*- coding: utf-8 -*-
"""png-q-bounce：把一张 PNG 做成"按钮式轻按回弹"的 GIF。

动画模仿按钮交互：轻微按下（整体小幅缩小）→ 轻柔回弹（略过冲）→ 静止，
居中缩放、幅度克制。**GIF 画布与原图分辨率完全一致，首帧即原图 1:1 像素**；
动画共 12 帧、时长精确 0.5 秒，**只循环播放一遍**（不写入 NETSCAPE 循环扩展）。

用法：
    python qbounce.py input.png [-o output.gif] [--duration 500] [--amplitude 1.0]

也支持把 PNG 直接拖到 拖拽转换.bat 上使用。
"""

import argparse
import os
import sys

from PIL import Image

# 12 帧：整体等比缩放（居中）。按压段缩到 0.95，回弹段带 1.005 的轻微过冲。
# 首帧与末帧均为 (1,1)：首帧即原图 1:1，末帧静止收尾；相邻帧两两可分辨
# （Pillow 会合并完全相同的相邻帧，因此末尾用 1px 级的微移过渡）。
WOBBLE = [
    (1.000, 1.000, 0.000),
    (0.990, 0.990, 0.000),
    (0.965, 0.965, 0.000),
    (0.950, 0.950, 0.000),   # 按压最低点
    (0.970, 0.970, 0.000),
    (0.990, 0.990, 0.000),
    (1.005, 1.005, 0.000),   # 释放轻微过冲
    (1.000, 1.000, 0.000),
    (0.995, 0.995, 0.000),
    (1.003, 1.003, 0.000),
    (1.000, 1.000, -0.004),  # 1px 级微移：与末帧可分辨
    (1.000, 1.000, 0.000),
]
DEFAULT_TOTAL_MS = 500  # 12 帧合计时长（GIF 按 1/100 秒存储，逐帧分配凑满）


def build_frames(img, amplitude=1.0):
    """返回 (帧列表, 画布尺寸)。画布=原图尺寸：首帧即原图 1:1 像素，
    整体居中缩放，缩小帧四周留出透明边、放大帧对称裁切。"""
    img = img.convert("RGBA")
    w, h = img.size
    frames = []
    for sx, sy, dy_ratio in WOBBLE:
        sx = 1.0 + (sx - 1.0) * amplitude
        sy = 1.0 + (sy - 1.0) * amplitude
        dy = dy_ratio * amplitude
        nw = max(1, int(round(w * sx)))
        nh = max(1, int(round(h * sy)))
        scaled = img.resize((nw, nh), Image.LANCZOS)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x = (w - nw) // 2
        y = (h - nh) // 2 + int(round(h * dy))
        frame.paste(scaled, (x, y), scaled)
        frames.append(frame)
    return frames, (w, h)


def to_p_frame(frame, transparent_index=255):
    """RGBA → P 模式（255 色 + 索引 transparent_index 作全透明），保住透明背景。"""
    alpha = frame.getchannel("A")
    mask = alpha.point(lambda a: 255 if a <= 16 else 0)  # 255 = 需要透明的像素
    p = frame.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
    p.paste(transparent_index, mask)  # 透明像素统一指向保留索引
    return p


def distribute(total_cs, count):
    """把总厘秒数尽量均匀分配到 count 帧，总和精确等于 total_cs。"""
    base = total_cs // count
    cs = [base] * count
    for i in range(total_cs - base * count):
        cs[-1 - i] += 1
    return [c * 10 for c in cs]  # 转回毫秒


def make_gif(in_path, out_path, total_ms=DEFAULT_TOTAL_MS, amplitude=1.0):
    img = Image.open(in_path)
    frames, _ = build_frames(img, amplitude=amplitude)
    p_frames = [to_p_frame(f) for f in frames]
    # 相邻完全相同的帧会被 Pillow 合并，先自行去重，保证时长分配准确
    merged = [p_frames[0]]
    for f in p_frames[1:]:
        if f.tobytes() != merged[-1].tobytes():
            merged.append(f)
    durations = distribute(max(120, total_ms) // 10, len(merged))
    # 不传 loop 参数 → 不写入 NETSCAPE 循环扩展 → 播放器只播一遍即停在末帧
    merged[0].save(
        out_path, save_all=True, append_images=merged[1:],
        duration=durations, disposal=2, transparency=255, optimize=False,
    )
    return out_path, len(merged)


def main():
    ap = argparse.ArgumentParser(description="把 PNG 做成只播一遍的按钮式轻按回弹 GIF")
    ap.add_argument("input", help="输入 PNG 路径")
    ap.add_argument("-o", "--output", help="输出 GIF 路径（默认同名 _q.gif）")
    ap.add_argument("--duration", type=int, default=DEFAULT_TOTAL_MS,
                    help="动画总时长毫秒数（默认 500）")
    ap.add_argument("--amplitude", type=float, default=1.0,
                    help="按压幅度系数（默认 1.0，越大按压越深）")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print("Error: file not found: {}".format(args.input))
        sys.exit(1)
    out = args.output or os.path.splitext(args.input)[0] + "_q.gif"
    out, n = make_gif(args.input, out, total_ms=max(120, args.duration),
                      amplitude=max(0.1, args.amplitude))
    size = os.path.getsize(out)
    print("OK: {}".format(out))
    print("   {} frames, {:.1f} KB".format(n, size / 1024))


if __name__ == "__main__":
    main()
