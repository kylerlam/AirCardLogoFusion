# AirCardLogoFusion

AirCardLogoFusion 是一套由 Codex 辅助完成的卡面标志提取与融色流程：从 iPhone 已通过面容识别、显示目标卡片的 Wallet NFC 支付界面截图中确认需要保留的标志，再参考一张新卡面背景图调整标志颜色，交付可叠加到卡面的透明 SVG。

目前通过项目内的两个 Skill 分步制作和检查。AirCardLogoFusion 是独立项目，与 AirCard 没有官方关联。

## 需要提供什么

1. **Wallet 支付界面截图**：用于识别目标卡片上的机构名称、Logo、支付网络标志及截图实际显示的遮蔽尾号，并确定它们的位置。
2. **目标背景图**：作为最终卡面的背景和标志融色的配色参考。
3. **可选的清晰标志原件**：如已有 SVG 或透明 PNG，请一并提供。截图上的低清字样可能无法准确还原原版笔画，清晰原件应优先用于确定字形。

包含个人信息的原始输入图如需暂存在项目内，可放进 `private-inputs/`；该目录已列入 `.gitignore`。确认可以公开的参考图与交付文件则保存在 `Assets/`。

## 制作流程

1. **提取前景**：使用 [iOS Wallet 标志提取 Skill](.codex/skills/ios-wallet-logo-extractor/SKILL.md) 检查截图，只选需要在新背景上复用的卡片身份标志。联名插画、角色、装饰、版权字样和系统界面元素不自动进入前景。输出透明矢量母版，并核对字形、比例和位置。
2. **确认字形底稿**：对照清晰原件或用户认可的版本检查笔画。截图描摹若出现扭曲，先解决来源与字形问题，再进行融色；不能把失真的提取物当作原版。
3. **背景融色**：使用 [Logo 融色 Skill](.codex/skills/wallet-logo-color-fusion/SKILL.md)，以已认可的透明 SVG 和背景图为输入，分析背景色与标志所在区域的对比度，只调整颜色。保持文字内容、路径、字距、位置、比例和透明度；不自行换字体、重描或添加轮廓。
4. **预览与交付**：检查纯色底近景和新背景叠加图，确认笔画清晰且颜色可读。交付透明 SVG 母版及适配 AirCard 画布的上传版；需要时另导出 PNG。

若只有已认可的透明 PNG，可以保持 alpha 蒙版原样进行换色并交付 PNG；仅凭 PNG 换色不会产生真正的矢量 SVG。

## 文件组织

每张卡的文件位于 `Assets/<卡名>/`；截图确实显示四位尾号时，使用 `Assets/<卡名 •••• 尾号>/`。原始提取物和后续融色方案分别保存，避免覆盖已认可的底稿。

八達通示例中，`Assets/八達通 Octopus/背景融色-粉蓝白-清晰字形/foreground-clean.svg` 是已认可的清晰字形底稿；同目录的 `upload-fusion.svg` 是粉蓝白融色上传版。该目录的预览和色彩报告用于复核效果。早期的 `Assets/八達通 Octopus/foreground.svg` 与 `upload.png` 存在字形失真，仅作为历史资料保留。

## 在 AirCard 使用

在 [AirCard 卡面制作页](https://aircardios.github.io/cards/custom.html) 中，将目标图放入「卡面背景图片」，将透明 SVG 上传版放入「Logo 与图章」图层，再对照预览检查位置和颜色。该页面支持 SVG Logo，导出卡面尺寸为 1536 × 969 像素；本项目的 SVG 母版不以这个像素数作为矢量画质要求。

[卡面模板库](https://aircardios.github.io/cards/index.html)可用于查看 AirCard 的卡面参考。
