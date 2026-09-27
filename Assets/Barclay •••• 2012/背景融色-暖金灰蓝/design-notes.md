# Barclay •••• 2012 · 背景融色-暖金灰蓝

暖金、奶油白與灰藍呼應室內燈光和牛仔衣。

## 文件

- `upload-fusion.svg`：推薦融色版，可直接上傳 Logo 圖層，1536 × 969。
- `upload-fusion-bright.svg`：較亮的配色比較版，淺色背景上的可讀性可能較低。
- `fusion-master.svg` / `fusion-bright-master.svg`：85.60mm × 53.98mm 矢量母版，viewBox 0 0 1536 969。
- `foreground.svg`：未融色的原始前景；`upload.png` 是對應的透明 PNG。
- `upload-fusion.png` / `upload-fusion-bright.png`：透明 PNG 備用。
- `background-card.png`：原背景置中裁剪，上方 27px、下方 28px；無拉伸、無修改人物。
- `preview.html`：兩種配色的背景疊加比較。
- `preview-plain-fusion.png` / `preview-plain-fusion-bright.png`：純灰底的前景檢查圖。
- `palette-analysis.json`、`color-plan.json`、`validation.json`：取色分析、配色與驗證記錄。

## 來源與驗證

直接沿用提供的 Barclays-Visa-foreground.svg，沒有更換字體或重描。

Barclays 完整保留提供的矢量底稿；此次未重描，亦未改字。

融色僅改填色，逐項比對保留路徑、輪廓、位置、比例、透明度與其餘非顏色屬性。未新增描邊、陰影或底襯。SVG 不含位圖、外鏈或字體文本。Chrome 的純色與漸變光柵化可能在極少數邊緣像素產生最多 1/255 的 alpha 取整差異；SVG 的透明度屬性保持原樣。

背景未含舊字樣，因此沒有舊 Logo 重影。標識仍採原卡位置，沒有為避開人物而移動或縮小。

## 使用

背景用 `background-card.png`，Logo 用 `upload-fusion.svg`；保持居中、縮放 100%、旋轉 0°、不透明度 100%，關閉白底移除及描邊。不要把背景疊加預覽當成透明 Logo 上傳。
