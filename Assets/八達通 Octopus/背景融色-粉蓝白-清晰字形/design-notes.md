# 八達通 Octopus · 清晰字形粉蓝白融色

## 依据

- 用户新附的 Photo 1 中，顶部「八達通 Octopus」笔画清晰。此前的 `foreground.svg` 和用户附的 `upload.png` 来自同一份带锯齿的截图描摹，因此不能直接给旧路径换色。
- 新附 `upload.png` 用于锁定透明卡面尺寸 `1536 × 969` 和标识范围 `(70, 70, 605, 148)`；字形参考 Photo 1 重建。只取顶部机构名称，照片里的联名图案和装饰不进入 Logo 图层。
- 中文以本机 Arial Unicode MS、英文以 Helvetica Neue Regular 的轮廓匹配照片，转换为 SVG 路径；交付 SVG 不依赖字体安装或外链。它们是照片匹配的重建轮廓，不宣称为品牌官方矢量源文件。

## 融色与交付

- 正式配色沿用用户选定的 `#FFC2DD → #FFF9FC → #8DD3FF`。色相取自背景的灰粉、近白和蓝色光泽，并提亮以保证左上暗区的对比度。
- 标识保持完全不透明，不新增描边、阴影、底衬或滤镜。`upload-fusion-readable.svg` 仅作更亮的颜色比较，正式上传使用 `upload-fusion.svg` 或透明 `upload-fusion.png`。
- `foreground-clean.svg` 是清晰黑色字形源；`fusion-master.svg` 是 85.60 × 53.98 mm 的融色母版；`upload-fusion.svg` 是 AirCard 1536 × 969 固有尺寸版。所有 SVG 都是自包含的矢量路径。
- `preview-plain.png` 在纯深色背景上展示真实字形；`preview-background.png` 与 `preview.html` 展示旧卡面背景叠加。旧背景已烙入深色字样，叠加时会有重影；要获得干净的正式卡面，需要无字背景。
