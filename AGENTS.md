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
## When changing math

1. Edit `lib_aspect_ratio_lock/util.py`.
2. Extend `tests/test_util.py`.
3. Run `python -m unittest discover -s tests -v`.

Keep UI wiring thin: Gradio `.click(fn=...)` should point at `util` functions (or small `partial`s), not inline lambdas with business logic.

## Inspiration / attribution

Behaviour comes from the archived `sd-webui-aspect-ratio-helper`. Prefer fixing Forge Neo incompatibilities over redesigning UX. Credit that project in the README when behaviour is carried over.

## Versioning and releases

This repo follows [Semantic Versioning](https://semver.org). **Git tags are the version of record** — there is no version file to keep in sync.

- Tags are annotated and named `vMAJOR.MINOR.PATCH` (e.g. `v0.3.1`), created on `main`.
- **MAJOR stays `0`.** Do not release `1.0.0` (or any `1.x`) unless the owner explicitly says the project is ready. While on `0.x`, a breaking change bumps MINOR.
- **MINOR** — a new user-facing feature (a new control, ratio behaviour, or preset group); a new, renamed, or changed-default `arl_*` setting; any breaking change.
- **PATCH** — a bug fix or a Forge Neo / Gradio compatibility fix with no new capability.
- **No tag** — docs, tests, refactors, or `AGENTS.md` edits that do not change shipped behaviour.
- If `git tag` is empty, the first release is `v0.1.0`.

Whenever you commit and push a releasable change to `main`, tag it in the same push:

```bash
git describe --tags --abbrev=0                      # latest version (none yet -> v0.1.0)
# ... commit the change on main ...
git tag -a vX.Y.Z -m "vX.Y.Z: <one-line summary>"    # on the commit that ships the change
git push origin main vX.Y.Z                         # commit and tag together
git ls-remote --tags origin vX.Y.Z                  # verify it arrived
```

Rules:

- Pick the bump from the *whole* change, not the last commit. When several changes ship together, use the highest bump.
- Never move, delete, or re-push a tag that has been pushed. If a release was wrong, ship a new PATCH.
- Never push a tag without its commit, and never tag a commit that is not on `main`.
- Only commit / push when the user has asked you to (as elsewhere); the tag is part of that push, not a separate ask.
- In your reply, state the version you tagged and why that bump.
