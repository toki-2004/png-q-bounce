# -*- coding: utf-8 -*-
"""qbounce.py 产物自检：对生成 GIF 断言规格。用法：python tests/verify_gif.py [gif 路径] [原 png 路径]"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import qbounce  # noqa: E402


def bbox(im):
    return im.getchannel("A").getbbox()


def verify(gif_path, png_path):
    g = Image.open(gif_path)
    src = Image.open(png_path).convert("RGBA")
    orig = bbox(src)
    orig_w = orig[2] - orig[0]
    durs, bbs = [], []
    for i in range(g.n_frames):
        g.seek(i)
        durs.append(g.info.get("duration", 0))
        bbs.append(g.convert("RGBA").getchannel("A").getbbox())

    assert g.size == src.size, ("画布必须与原图一致", g.size, src.size)
    assert sum(durs) == 300, ("总时长必须精确 300ms", durs)
    assert g.info.get("loop") is None, "不得写入 NETSCAPE 循环扩展（只播一遍）"
    assert max(abs(b[3] - orig[3]) for b in bbs) <= 3, ("底部锚定（内容底边 ±3px）", bbs)
    assert max(b[2] for b in bbs) <= orig[2] + 1, ("无过冲（不得超出原宽度）", bbs)
    g.seek(0)
    assert bbox(g.convert("RGBA")) == orig, "首帧必须与原图 1:1"
    assert g.convert("RGBA").getpixel((0, 0))[3] == 0 or orig[0] > 0, "透明保留"
    return g.n_frames, sum(durs)


def main():
    png = sys.argv[1] if len(sys.argv) > 1 else None
    gif = sys.argv[2] if len(sys.argv) > 2 else None
    tmp_png = tmp_gif = None
    if not gif:
        # 无输入时生成一张测试图自检
        from PIL import Image, ImageDraw
        tmp_png = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_verify.png")
        gif = tmp_gif = tmp_png.replace(".png", "_q.gif")
        im = Image.new("RGBA", (200, 260), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([20, 20, 180, 240], fill=(86, 130, 240, 255), outline=(30, 60, 160, 255), width=6)
        im.save(tmp_png)
        qbounce_out, _ = make = None, None
        make_gif(tmp_png, gif)
    n, total = verify(gif, png or tmp_png)
    print("OK: {} frames, {} ms, canvas {}".format(n, total, Image.open(gif).size))
    if tmp_png:
        os.remove(tmp_png)
    if tmp_gif:
        os.remove(tmp_gif)


def make_gif(png, gif):
    import qbounce
    qbounce.make_gif(png, gif)


if __name__ == "__main__":
    main()
