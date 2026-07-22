# Agent guidance — Aspect Ratio Lock

This repo is a Forge Neo extension. Keep it aligned with sibling `sd-dynamic-placeholders` structure and voice.

## Scope

- Target **Forge Neo** (Gradio 4.40) first. Do not assume A1111 Gradio 3 APIs exist.
- No extra runtime pip dependencies. Tests must run with stdlib `unittest` and no WebUI process.
- Do not reintroduce `gr.inputs.Slider` / other Gradio 3-only APIs.

## Layout

| Path | Role |
|---|---|
| `scripts/aspect_ratio_lock.py` | WebUI entry: `scripts.Script` + `on_ui_settings` |
| `lib_aspect_ratio_lock/` | Pure / Gradio helpers (`util`, `settings`, `components`, `constants`) |
| `javascript/arl_core.js` | Pure ratio/flip math (shared with Node tests) |
| `javascript/aspect_ratio_lock.js` | Client-side ratio lock (main interactive behaviour) |
| `style.css` | Scoped styles (`arl-` / `#*_size_toolbox`) |
| `tests/` | Standalone unit tests |
| `docs/` | User-facing settings docs |

Option keys and CSS/JS IDs use the `arl_` / `arl-` prefix. Settings section id is `aspect_ratio_lock`.

## Behaviour contracts

- Capture width/height via `after_component` + `elem_id` (`txt2img_width`, `txt2img_height`, `img2img_width`, `img2img_height`).
- Live linking while dragging is **JS-only**; Python accordion buttons call pure functions in `util.py`.
- Clamp to `MIN_DIMENSION=64` / `MAX_DIMENSION=2048` and round to multiples of 8.
- img2img “Image” ratio must work with ForgeCanvas: prefer `div.forge-image-container img` and `input.forge-file-upload`.
- Call global `dimensionChange` when present so the built-in AR overlay stays correct.

## JavaScript / Forge globals

- Read settings from the bare global `opts` (Forge `javascript/ui.js`). **Never use `window.opts`** — Forge Neo does not assign it.
- Boot with `onOptionsAvailable(...)` so init runs after `opts` is parsed from `#settings_json`. Do not rely only on a MutationObserver after `onUiLoaded`: `opts` can become ready without a further DOM mutation.
- Try mounting immediately when width/height exist; keep a MutationObserver only as a fallback until init succeeds.
- Resolution presets (SDXL / Pony / Illustrious) live in `arl_core.js` as `RESOLUTION_PRESETS` and are rendered by `aspect_ratio_lock.js` above the ratio picker.

## When changing math

1. Edit `lib_aspect_ratio_lock/util.py`.
2. Extend `tests/test_util.py`.
3. Run `python -m unittest discover -s tests -v`.

Keep UI wiring thin: Gradio `.click(fn=...)` should point at `util` functions (or small `partial`s), not inline lambdas with business logic.

## Inspiration / attribution

Behaviour comes from the archived `sd-webui-aspect-ratio-helper`. Prefer fixing Forge Neo incompatibilities over redesigning UX. Credit that project in the README when behaviour is carried over.
