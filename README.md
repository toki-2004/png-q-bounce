# png-q-bounce

> **语言：** 简体中文 | [English](README.en.md)

把一张 PNG 一次性做成**按钮式轻按回弹 GIF**：底部锚定，轻微按下（顶部下沉）→ 平滑回到原尺寸，**一次点击一次回弹、无反复回弹**，动画**只循环播放一遍**（播完停在原始画面），保留透明背景。

典型用途：给 [desktop-pet](https://github.com/toki-2004/desktop-pet) 桌宠做互动动画皮肤——把静态 PNG 皮肤拖进来，得到可直接设置为 `pet_interact_image` 的单次播放 GIF。

## 使用方法

```bash
python qbounce.py 皮肤.png                     # 输出 皮肤_q.gif
python qbounce.py 皮肤.png -o 动画.gif         # 指定输出
python qbounce.py 皮肤.png --amplitude 1.3     # 更夸张的 Q 弹
python qbounce.py 皮肤.png --duration 40       # 更快的节奏（毫秒/帧）
```

也可以直接把 PNG 拖到 `拖拽转换.bat` 上使用。

单文件免安装版 exe 可在 [Releases](https://github.com/toki-2004/png-q-bounce/releases) 页面下载，无需安装 Python 环境。

## 参数

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--duration` | 500 | 动画总时长毫秒数（默认精确 0.5 秒），越小越快 |
| `--amplitude` | 1.0 | 按压幅度系数，1.2 ≈ 按得更深，0.7 ≈ 更轻 |

## 动画说明

* 12 帧按钮式单次按压回弹（总时长精确 0.5 秒）：底部锚定，轻微按下 → 平滑回弹到原尺寸，无反复回弹、无过冲（静止收尾帧自动合并）。
* **首帧与原图分辨率完全一致**：GIF 画布即原图尺寸，第一帧就是原图 1:1 像素。
* **只播一遍**：保存时不写入 GIF 的 NETSCAPE 循环扩展，浏览器 / 看图器 / Qt QMovie 播完即停在最后一帧（即原始画面）。
* 透明背景保留（GIF 索引透明 + disposal=2），可直接叠在桌宠上。

## 依赖

* Python 3 + [Pillow](https://pypi.org/project/Pillow/)（`pip install pillow`）

## 许可证

MIT License。
