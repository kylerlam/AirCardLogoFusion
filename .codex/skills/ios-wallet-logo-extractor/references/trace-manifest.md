# 高对比度标识描摹配置

`trace_regions.py` 使用已安装的 Pillow。不要为辅助描摹单独安装依赖；若当前环境没有 Pillow，改用现有图像运行时或其他矢量描摹方式。

```bash
python3 -B .codex/skills/ios-wallet-logo-extractor/scripts/trace_regions.py screenshot.jpg regions.json foreground.svg
```

`card_box` 和每个 `box` 均为原图像素 `[左, 上, 右, 下]`。先人工判断哪些元素应属于前景，再按其实际边界设置区域；脚本不决定内容取舍。

```json
{
  "title": "卡名 reusable marks",
  "card_box": [28, 111, 563, 449],
  "regions": [{
    "id": "issuer-name",
    "box": [47, 128, 246, 166],
    "supersample": 3,
    "layers": [{
      "id": "dark-wordmark",
      "fill": "#202124",
      "min": [0, 0, 0],
      "max": [165, 165, 165],
      "min_area": 8,
      "tolerance": 0.9
    }]
  }]
}
```

每层的 `min`/`max` 是 RGB 通道范围；需要区分相近色时可加 `diff_min` 或 `diff_max`，例如 `{"b-r": 25}`。脚本将二值区域描成闭合 SVG 路径并保留孔洞，`tolerance` 以放大后的像素为单位简化轮廓。低分辨率、压缩伪影和复杂背景会影响精度，需看预览并适当缩小区域或修改阈值。
