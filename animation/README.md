# Animasyon (Remotion)

React ile programatik video/animasyon üretmek için Remotion projesi.

## Kurulum
```bash
cd animation
npm install
```

## Kullanım
- `npm run studio` → tarayıcıda canlı önizleme/düzenleme (http://localhost:3000)
- `npm run render` → `out/video.mp4` üretir
- `npm run still` → tek bir kareyi `out/frame.png` olarak kaydeder

Animasyonlar `src/` altındadır; yeni sahne eklemek için `src/Root.tsx` içine yeni bir `<Composition>` ekleyin.

### Claude Code bulut ortamında
Chrome indirmek yerine hazır Chromium'u kullanın:
```bash
export REMOTION_BROWSER_EXECUTABLE=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
npm run render
```
