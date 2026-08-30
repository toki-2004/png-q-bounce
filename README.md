# png-q-bounce

把一张 PNG 一次性做成 **Q 弹（果冻挤压回弹）GIF**：底部锚定的挤压 → 拉伸 → 衰减摇摆 → 静止，动画**只循环播放一遍**（播完停在原始画面），并保留透明背景。

典型用途：给 [desktop-pet](../desktop-pet) 桌宠做互动动画皮肤——把静态 PNG 皮肤拖进来，得到可直接设置为 `pet_interact_image` 的单次播放 GIF。

## 使用方法

```bash
python qbounce.py 皮肤.png                     # 输出 皮肤_q.gif
python qbounce.py 皮肤.png -o 动画.gif         # 指定输出
python qbounce.py 皮肤.png --amplitude 1.3     # 更夸张的 Q 弹
python qbounce.py 皮肤.png --duration 40       # 更快的节奏（毫秒/帧）
```

也可以直接把 PNG 拖到 `拖拽转换.bat` 上使用。

## 参数

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--duration` | 55 | 每帧毫秒数，越小越快 |
| `--amplitude` | 1.0 | Q 弹幅度系数，1.3 ≈ 更夸张，0.6 ≈ 更含蓄 |

## 动画说明

* 7 帧衰减摇摆：压扁（横向变宽）→ 拉长（纵向弹起）→ 逐帧衰减回原尺寸，底部锚定（像落在地面上）。
* **只播一遍**：保存时不写入 GIF 的 NETSCAPE 循环扩展，浏览器 / 看图器 / Qt QMovie 播完即停在最后一帧（即原始画面）。
* 透明背景保留（GIF 索引透明 + disposal=2），可直接叠在桌宠上。

## 依赖

* Python 3 + [Pillow](https://pypi.org/project/Pillow/)（`pip install pillow`）

## 许可证

MIT License。
