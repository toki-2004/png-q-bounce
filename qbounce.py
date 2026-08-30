# -*- coding: utf-8 -*-
"""png-q-bounce：把一张 PNG 做成 Q 弹（果冻挤压回弹）的 GIF。

Q 弹动画 = 底部锚定的挤压/拉伸摇摆（squash & stretch），幅度逐帧衰减，
最终回到原始尺寸静止。**GIF 画布与原图分辨率完全一致，首帧即原图 1:1 像素**；
摇摆帧超出画布的部分会被裁掉（挤压裁两侧、拉长裁顶部）。动画共 12 帧、
约 0.5 秒，**只循环播放一遍**（不写入 NETSCAPE 循环扩展，播完停在末帧）。

用法：
    python qbounce.py input.png [-o output.gif] [--duration 40] [--amplitude 1.0]

也支持把 PNG 直接拖到 拖拽转换.bat 上使用。
"""

import argparse
import os
import sys

from PIL import Image

# 12 帧：首帧与末帧均为 (1,1,0)——首帧即原图 1:1，末帧静止收尾；其余帧两两不同
# （Pillow 会合并完全相同的相邻帧，因此每帧缩放都要有可分辨的差异）。
# 压扁帧底边贴地不动，拉伸帧整体向上弹起（dy<0），偏移只取非正值。
WOBBLE = [
    (1.000, 1.000, 0.000),
    (1.100, 0.900, 0.000),   # 落地压扁（两侧超出画布被裁，底边贴地）
    (0.950, 1.080, -0.025),  # 弹起拉长（顶部超出被裁）
    (1.060, 0.950, 0.000),
    (0.970, 1.040, -0.010),
    (1.030, 0.980, 0.000),
    (0.980, 1.020, -0.004),
    (1.020, 0.990, 0.000),
    (0.990, 1.010, -0.001),
    (1.010, 1.000, 0.000),
    (0.995, 1.005, 0.000),
    (1.000, 1.000, 0.000),
]
DEFAULT_DURATION_MS = 40   # 默认总时长：10 x 40ms + 2 x 50ms = 恰好 500ms


def build_frames(img, amplitude=1.0):
    """返回 (帧列表, 画布尺寸)。画布=原图尺寸：首帧即原图 1:1 像素，
    底部锚定，挤压向两侧扩、拉长向顶部弹，超出画布的部分裁掉。"""
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
        x = (w - nw) // 2  # 水平居中：压扁变宽时两侧对称裁切
        # 底部锚定在画布底，dy<0 表示向上弹起；paste 自动裁掉越界部分
        y = h - nh + int(round(h * dy))
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


def make_gif(in_path, out_path, duration=DEFAULT_DURATION_MS, amplitude=1.0):
    img = Image.open(in_path)
    frames, _ = build_frames(img, amplitude=amplitude)
    p_frames = [to_p_frame(f) for f in frames]
    # GIF 帧时长按 1/100 秒存储。默认配置精确凑满 0.5 秒：10 x 40ms + 2 x 50ms；
    # 自定义 duration 时每帧统一使用该值。不传 loop → 只播一遍。
    if duration == DEFAULT_DURATION_MS:
        durations = [40] * (len(p_frames) - 2) + [50, 50]
    else:
        durations = [duration] * len(p_frames)
    p_frames[0].save(
        out_path, save_all=True, append_images=p_frames[1:],
        duration=durations, disposal=2, transparency=255, optimize=False,
    )
    return out_path


def main():
    ap = argparse.ArgumentParser(description="把 PNG 做成只播一遍的 Q 弹 GIF")
    ap.add_argument("input", help="输入 PNG 路径")
    ap.add_argument("-o", "--output", help="输出 GIF 路径（默认同名 _q.gif）")
    ap.add_argument("--duration", type=int, default=DEFAULT_DURATION_MS,
                    help="每帧毫秒数（默认 40，12 帧合计 0.5 秒）")
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
