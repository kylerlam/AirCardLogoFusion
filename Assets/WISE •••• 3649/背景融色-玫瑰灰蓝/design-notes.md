# WISE •••• 3649 · Color Fusion

保留：Wise、VISA Infinite、•••• 3649。標誌與尾號按照本次 Wallet 截圖提取，位置映射自原圖卡面框 [54, 222, 1125, 896]。未保留卡面原有的裝飾、紋理及 Wallet 系統介面。

## 檔案

- `upload-fusion.svg`：融色上傳版，1536 × 969，透明純向量。
- `upload-fusion-readable.svg`：較深的高可讀配色，尺寸與路徑相同。
- `fusion-master.svg` / `fusion-readable-master.svg`：85.60 × 53.98 mm 母版，viewBox 0 0 1536 969。
- `foreground.svg`：本次截圖提取的換色底稿。
- `background-card.jpg`：背景保持比例、居中裁切為 1536 × 969，與預覽一致。
- `preview.html`：背景疊加比較；`preview-plain.png` / `preview-plain-readable.png`：純色底檢查。

融合配色：#985D6D → #7A5A79 → #48677F。
高可讀配色：#603344 → #4C3C5A → #274458。
背景局部普遍明亮，因此高可讀版使用更深的同系色。色彩取樣與局部亮度見 `palette-analysis.json`。

已驗證所有版本的形狀、座標、位置、比例與透明度一致；同尺寸渲染的 alpha 位元組完全相同。無嵌入位圖、字型、外鏈、描邊、陰影、底衬或濾鏡。截圖描摹精度受來源解析度限制，並非官方 Logo 向量檔。

上傳時以 `background-card.jpg` 作背景、`upload-fusion.svg` 作 Logo 圖層，居中、縮放 100%、旋轉 0°、不透明度 100%。

背景的角色、線稿與日文字是原有插畫；原位置的 Wise / VISA Infinite 會與插畫交疊，已保留標誌原排版。高可讀版只提高深淺對比，不移動標誌或添加底板。

渲染驗收使用已內建的 Sharp / SVG 引擎；原 Chrome 渲染器啟動失敗，未安裝額外套件。
