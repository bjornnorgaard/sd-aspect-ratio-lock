# Aspect Ratio Lock

A [Stable Diffusion WebUI Forge - Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) extension that keeps width and height linked while you change dimensions, and adds optional scale / ratio / percentage shortcuts.

**Only tested with Forge Neo.** It may work on other Automatic1111-compatible frontends, but that is unsupported.

Functionality is inspired by the archived [sd-webui-aspect-ratio-helper](https://github.com/thomasasfk/sd-webui-aspect-ratio-helper) extension. This port targets Gradio 4.40 (Forge Neo) — the original breaks there because it still uses the removed `gr.inputs.Slider` API.

## Features

- **JavaScript aspect ratio controls** next to the width/height swap button (txt2img and img2img)
  - Dropdown (or cycle button) of configurable ratios (`1:1`, `16:9`, …) plus SDXL / Pony / Illustrious resolution presets
  - `🔒` locks to the current W×H ratio
  - `🖼️` (img2img) locks to the loaded image’s ratio, including ForgeCanvas inputs
  - Swap (`⇅`) also flips configured ratio labels (`4:3` ↔ `3:4`)
- **Optional accordion** with:
  - Scale to maximum / minimum dimension
  - Pre-defined aspect ratio buttons
  - Pre-defined percentage scale buttons (`-50%`, `x1.5`, …)

Dimensions stay within `64–2048` and snap to multiples of 8 (Forge Neo slider step).

## Install

1. Copy or clone this folder into your Forge Neo `extensions/` directory:

   ```
   .../Stable Diffusion WebUI Forge - Neo/extensions/sd-aspect-ratio-lock/
   ```

2. Restart the WebUI (Stability Matrix → restart package, or rerun `webui.sh`).

3. Confirm a ratio dropdown (or cycle button) appears next to the width/height swap control.

No extra Python packages are required.

If you previously installed `sd-webui-aspect-ratio-helper`, disable or remove it to avoid duplicate controls.

## Quick start

1. Leave **Enable JavaScript aspect ratio controls** on (Settings → Aspect Ratio Lock). Default ratios: `1:1, 3:2, 4:3, 5:4, 16:9`.
2. Pick a ratio or an SDXL / Pony / Illustrious resolution from the dropdown, then drag width or height — the other dimension follows.
3. Use `🔒` to freeze whatever ratio you already have, or `🖼️` on img2img to follow the source image.
4. To enable the accordion tools, turn off **Hide accordion by default** and enable the individual button groups under Settings → Aspect Ratio Lock.

## Documentation

| Doc | Contents |
|---|---|
| [docs/settings.md](docs/settings.md) | Settings page keys, defaults, and accordion / JS behaviour |

For agents working in this repo: [AGENTS.md](AGENTS.md).

## Tests

From the extension directory (WebUI does not need to be running):

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).

Portions adapted from [sd-webui-aspect-ratio-helper](https://github.com/thomasasfk/sd-webui-aspect-ratio-helper) (MIT).
