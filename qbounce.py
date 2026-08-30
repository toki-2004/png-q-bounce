# -*- coding: utf-8 -*-
"""png-q-bounce：把一张 PNG 做成"按钮式轻按回弹"的 GIF。

一次点击一次回弹：底部锚定，轻微按下（整体小幅缩小，顶部下沉）→ 平滑
回到原尺寸静止，**没有反复回弹、没有过冲**。居中缩放、幅度克制。
**GIF 画布与原图分辨率完全一致，首帧即原图 1:1 像素**；动画共 12 帧、
时长精确 0.5 秒，**只循环播放一遍**（不写入 NETSCAPE 循环扩展）。

用法：
    python qbounce.py input.png [-o output.gif] [--duration 500] [--amplitude 1.0]

也支持把 PNG 直接拖到 拖拽转换.bat 上使用。
"""

import argparse
import os
import sys

from PIL import Image

# 12 帧：一次"按下 → 回弹"，底部锚定（底边贴地不动，顶边下沉再抬起），
# 无过冲、无反复回弹。首帧与末帧均为 (1,1)：首帧即原图 1:1，末帧静止收尾；
# 回到原尺寸后的静止帧会被 Pillow 合并，帧时长按实际帧数精确分配（合计 0.5 秒）。
WOBBLE = [
    (1.000, 1.000),
    (0.975, 0.975),
    (0.950, 0.950),
    (0.930, 0.930),   # 按压最低点
    (0.950, 0.950),
    (0.970, 0.970),
    (0.985, 0.985),
    (0.995, 0.995),
    (1.000, 1.000),
    (1.000, 1.000),
    (1.000, 1.000),
    (1.000, 1.000),
]
DEFAULT_TOTAL_MS = 500  # 全部帧合计时长（GIF 按 1/100 秒存储，逐帧分配凑满）


def build_frames(img, amplitude=1.0):
    """返回 (帧列表, 画布尺寸)。画布=原图尺寸：首帧即原图 1:1 像素。
    底部锚定：按压时顶边下沉、底边不动，因此任何帧都不会超出画布。"""
    img = img.convert("RGBA")
    w, h = img.size
    frames = []
    for sx, sy in WOBBLE:
        sx = 1.0 + (sx - 1.0) * amplitude
        sy = 1.0 + (sy - 1.0) * amplitude
        nw = max(1, int(round(w * sx)))
        nh = max(1, int(round(h * sy)))
        scaled = img.resize((nw, nh), Image.LANCZOS)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x = (w - nw) // 2  # 水平居中
        y = h - nh         # 底部锚定：底边贴住画布底
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
    # 相邻完全相同的帧会被 Pillow 合并（本动画的静止收尾帧），先自行去重，
    # 再把 0.5 秒精确分配到实际帧数——无论合并后剩几帧，总时长都保持不变。
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
                    help="按压幅度系数（默认 1.0，越大按得越深）")
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
