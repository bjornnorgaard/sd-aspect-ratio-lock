# Settings

All options live under **Settings → Aspect Ratio Lock**. Keys use the `arl_` prefix.

Restart (or reload UI) after changing JS-related options so the client script picks them up. The ratio dropdown next to the W/H swap appears only after a full UI load once `opts` is available — a hard refresh or WebUI restart is enough.

## JavaScript controls

| Setting | Key | Default |
|---|---|---|
| Enable JavaScript aspect ratio controls | `arl_javascript_aspect_ratio_show` | `True` |
| JavaScript aspect ratio list | `arl_javascript_aspect_ratio` | `1:1, 3:2, 4:3, 5:4, 16:9` |
| Include resolution presets in dropdown | `arl_javascript_resolution_presets_show` | `True` |
| JavaScript selection method | `arl_ui_javascript_selection_method` | `Aspect Ratios Dropdown` |

Selection methods:

- **Aspect Ratios Dropdown** — native `<select>` with Off / Lock / configured ratios (plus Image on img2img). When resolution presets are enabled, SDXL / Pony / Illustrious sizes appear as optgroups in the same control.
- **Default Options Button** — single button that cycles Off → Lock (→ Image on img2img). Configured ratio strings and resolution presets are not included in cycle mode.

**Resolution presets** (dropdown mode only) set exact width × height, then select `🔒`:

| Group | Resolutions |
|---|---|
| SDXL / Pony (~1024²) | `1024×1024`, `1152×896`, `896×1152`, `1216×832`, `832×1216`, `1344×768`, `768×1344`, `1536×640`, `640×1536` |
| Illustrious (~1536²) | `1536×1536`, `1024×1536`, `1536×1024`, `1248×1824`, `1824×1248` |

Pony shares SDXL’s native buckets. Illustrious is trained around 1536px.

While a ratio is active, changing width or height updates the other side, clamps to `64–2048`, and rounds to a multiple of 8. The WebUI `dimensionChange` helper is called so the img2img aspect-ratio overlay stays in sync.

On img2img, **🖼️ Image** reads the active tab’s ForgeCanvas / Gradio image (`naturalWidth` / `naturalHeight`). Dropping or selecting a new file while Image is selected updates the lock.

## Accordion

The accordion is hidden unless you opt in. By default **Hide accordion by default** is `True`, and every accordion component is off — only the JS dropdown is visible.

| Setting | Key | Default |
|---|---|---|
| Hide accordion by default | `arl_hide_accordion_by_default` | `True` |
| Expand accordion by default | `arl_expand_by_default` | `False` |
| UI component order | `arl_ui_component_order_key` | `MaxDimensionScaler, MinDimensionScaler, PredefinedAspectRatioButtons, PredefinedPercentageButtons` |

### Maximum / minimum dimension

| Setting | Key | Default |
|---|---|---|
| Show maximum dimension button | `arl_show_max_width_or_height` | `False` |
| Maximum dimension default | `arl_max_width_or_height` | `1024` |
| Show minimum dimension button | `arl_show_min_width_or_height` | `False` |
| Minimum dimension default | `arl_min_width_or_height` | `1024` |

**Scale to maximum dimension** sets the larger side to the slider value and scales the other to keep aspect ratio.

**Scale to minimum dimension** sets the smaller side to the slider value and scales the other accordingly.

### Pre-defined aspect ratios

| Setting | Key | Default |
|---|---|---|
| Show pre-defined aspect ratio buttons | `arl_show_predefined_aspect_ratios` | `False` |
| Use Maximum dimension for ratio buttons | `arl_predefined_aspect_ratio_use_max_dim` | `False` |
| Pre-defined aspect ratio buttons | `arl_predefined_aspect_ratios` | `1:1, 4:3, 16:9, 9:16, 21:9` |

When “use max dim” is off, buttons scale from `max(current width, current height)`. When on, they use the Maximum dimension slider value instead.

### Pre-defined percentages

| Setting | Key | Default |
|---|---|---|
| Show pre-defined percentage buttons | `arl_show_predefined_percentages` | `False` |
| Pre-defined percentage buttons | `arl_predefined_percentages` | `25, 50, 75, 125, 150, 175, 200` |
| Percentage display format | `arl_predefined_percentages_display_key` | Incremental (`-50%`, `+50%`) |

Display formats:

- Incremental/decremental (`-50%`, `+50%`)
- Raw percentage (`50%`, `150%`)
- Multiplication (`x0.5`, `x1.5`)

## Notes

JavaScript lock and accordion scale buttons can both change W/H. Prefer one workflow at a time if the results feel surprising.
