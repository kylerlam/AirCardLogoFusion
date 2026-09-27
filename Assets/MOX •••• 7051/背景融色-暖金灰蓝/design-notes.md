# MOX •••• 7051 · Color Fusion

保留：mox、Mastercard 雙圓與字標、•••• 7051。標誌與尾號按照本次 Wallet 截圖提取，位置映射自原圖卡面框 [54, 222, 1125, 896]。未保留卡面原有的裝飾、紋理及 Wallet 系統介面。

## 檔案

- `upload-fusion.svg`：融色上傳版，1536 × 969，透明純向量。
- `upload-fusion-readable.svg`：較深的高可讀配色，尺寸與路徑相同。
- `fusion-master.svg` / `fusion-readable-master.svg`：85.60 × 53.98 mm 母版，viewBox 0 0 1536 969。
- `foreground.svg`：本次截圖提取的換色底稿。
- `background-card.jpg`：背景保持比例、居中裁切為 1536 × 969，與預覽一致。
- `preview.html`：背景疊加比較；`preview-plain.png` / `preview-plain-readable.png`：純色底檢查。

融合配色：#906031 → #A5793E → #54718F。
高可讀配色：#65421F → #76542B → #304D6B。
背景局部普遍明亮，因此高可讀版使用更深的同系色。色彩取樣與局部亮度見 `palette-analysis.json`。

已驗證所有版本的形狀、座標、位置、比例與透明度一致；同尺寸渲染的 alpha 位元組完全相同。無嵌入位圖、字型、外鏈、描邊、陰影、底衬或濾鏡。截圖描摹精度受來源解析度限制，並非官方 Logo 向量檔。

上傳時以 `background-card.jpg` 作背景、`upload-fusion.svg` 作 Logo 圖層，居中、縮放 100%、旋轉 0°、不透明度 100%。

Mastercard 雙圓按截圖的圓心、半徑與交集轉為向量幾何；銀色金屬反光以暖金、灰藍與中間色替換，字標保持截圖描摹輪廓。

渲染驗收使用已內建的 Sharp / SVG 引擎；原 Chrome 渲染器啟動失敗，未安裝額外套件。
