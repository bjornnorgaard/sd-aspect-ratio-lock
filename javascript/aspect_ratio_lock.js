/**
 * Client-side aspect-ratio lock for Forge Neo width/height sliders.
 *
 * Injects a dropdown (or cycle button) next to the swap control and keeps W/H
 * linked while dragging. Reads settings from the Forge global `opts` (not
 * window.opts — that property is never set on Forge Neo).
 *
 * Inspired by thomasasfk/sd-webui-aspect-ratio-helper; adapted for Gradio 4 /
 * ForgeCanvas (forge-image-container img selectors).
 */
(function () {
    "use strict";

    const Core = globalThis.ArlCore;
    if (!Core) {
        console.error(
            "[Aspect Ratio Lock] arl_core.js missing — load order broken?",
        );
        return;
    }

    const { OFF, LOCK, IMAGE, MAXIMUM_DIMENSION, MINIMUM_DIMENSION } = Core;

    // Match Forge Neo's own aspectRatioOverlay.js tab → container mapping.
    const IMAGE_INPUT_CONTAINER_IDS = [
        "img2img_image",
        "img2img_sketch",
        "img2maskimg",
        "inpaint_sketch",
        "img_inpaint_base",
    ];

    const IMAGE_SELECTORS = [
        "div.forge-image-container img",
        "div[data-testid=image] img",
        "img",
    ];

    function getOpts() {
        // Forge Neo: top-level `let opts` in ui.js — bare global, not window.opts.
        try {
            return typeof opts !== "undefined" ? opts : null;
        } catch (_) {
            return null;
        }
    }

    function getSelectedImage2ImageTab() {
        if (typeof get_tab_index === "function") {
            try {
                return get_tab_index("mode_img2img");
            } catch (_) {
                /* fall through */
            }
        }
        const mode = gradioApp().getElementById("mode_img2img");
        if (!mode) return 0;
        const selectedButton = mode.querySelector("button.selected");
        const allButtons = mode.querySelectorAll("button");
        return Array.prototype.indexOf.call(allButtons, selectedButton);
    }

    function getCurrentImage() {
        const currentTabIndex = getSelectedImage2ImageTab();
        const currentTabImageId = IMAGE_INPUT_CONTAINER_IDS[currentTabIndex];
        const container = document.getElementById(currentTabImageId);
        if (!container) return null;
        for (const sel of IMAGE_SELECTORS) {
            const img = container.querySelector(sel);
            if (img && img.naturalWidth) return img;
        }
        return container.querySelector("img");
    }

    function getConfiguredRatios() {
        const o = getOpts();
        const raw = (o && o.arl_javascript_aspect_ratio) || "";
        return raw
            .split(",")
            .map((x) => x.trim())
            .filter(Boolean);
    }

    function resolutionPresetsEnabled() {
        const o = getOpts();
        return !!(o && o.arl_javascript_resolution_presets_show);
    }

    function reverseAllOptions() {
        const allAspectRatioOptions = Array.from(
            gradioApp().querySelectorAll(".arl-ar-option"),
        );
        allAspectRatioOptions.forEach((el) => {
            const reversed = Core.reverseAspectRatio(el.value);
            if (reversed) {
                el.value = reversed;
                el.textContent = reversed;
            }
        });
    }

    class OptionPickingController {
        constructor(page, defaultOptions, controller) {
            this.page = page;
            this.options = this.getOptions(defaultOptions);
            this.switchButton = gradioApp().getElementById(page + "_res_switch_btn");
            if (!this.switchButton) {
                throw new Error(`Missing ${page}_res_switch_btn`);
            }

            const wrapperDiv = document.createElement("div");
            wrapperDiv.id = `${this.page}_size_toolbox`;
            wrapperDiv.className = "flex flex-col relative col gap-4 arl-size-toolbox";
            wrapperDiv.style.minWidth = "min(320px, 100%)";
            wrapperDiv.style.flexGrow = "0";
            wrapperDiv.innerHTML = this.getElementInnerHTML();

            const parent = this.switchButton.parentNode;
            parent.removeChild(this.switchButton);
            wrapperDiv.appendChild(this.switchButton);

            // Prefer anchoring inside the dimensions-tools column when present.
            const toolsCol = gradioApp().getElementById(`${page}_dimensions_row`);
            if (toolsCol && toolsCol.contains(parent)) {
                parent.appendChild(wrapperDiv);
            } else if (parent.lastChild && parent.lastChild.previousElementSibling) {
                parent.insertBefore(wrapperDiv, parent.lastChild.previousElementSibling);
            } else {
                parent.appendChild(wrapperDiv);
            }

            this.getPickerElement().onchange = this.pickerChanged(controller);
            this.switchButton.addEventListener(
                "click",
                this.switchButtonOnclick(controller),
            );

            if (resolutionPresetsEnabled()) {
                this.presetsController = new ResolutionPresetsController(
                    page,
                    controller,
                    wrapperDiv,
                );
            }
        }

        getOptions(defaultOptions) {
            return [...new Set([...defaultOptions, ...getConfiguredRatios()])];
        }

        pickerChanged(controller) {
            return () => {
                const picked = this.getCurrentOption();
                if (picked !== IMAGE) {
                    this.switchButton.removeAttribute("disabled");
                }
                controller.setAspectRatio(picked);
            };
        }

        /**
         * Forge Neo already swaps W↔H via Gradio on this button. Only flip the
         * stored ratio / dropdown labels so a later slider drag keeps the new
         * orientation — do not rewrite dimensions here (that races Gradio).
         */
        switchButtonOnclick(controller) {
            return () => {
                reverseAllOptions();
                this.reverseLocalOptions();
                controller.flipAspectRatio(this.getCurrentOption());
            };
        }

        reverseLocalOptions() {
            this.options = Core.reverseRatioOptions(this.options);
        }

        getElementInnerHTML() {
            throw new Error("Not implemented");
        }

        getPickerElement() {
            throw new Error("Not implemented");
        }

        getCurrentOption() {
            throw new Error("Not implemented");
        }
    }

    class SelectOptionPickingController extends OptionPickingController {
        getElementInnerHTML() {
            return `
        <div id="${this.page}_ratio" class="gr-block gr-box relative w-full border-solid border border-gray-200 gr-padded">
            <select id="${this.page}_select_aspect_ratio" class="gr-box gr-input w-full disabled:cursor-not-allowed">
                ${this.options
                    .map((r) => `<option class="arl-ar-option" value="${r}">${r}</option>`)
                    .join("\n")}
            </select>
        </div>
        `;
        }

        getPickerElement() {
            return gradioApp().getElementById(`${this.page}_select_aspect_ratio`);
        }

        getCurrentOption() {
            const selectElement = this.getPickerElement();
            const options = Array.from(selectElement.options);
            return options[selectElement.selectedIndex].value;
        }
    }

    class DefaultOptionsButtonOptionPickingController extends OptionPickingController {
        constructor(page, defaultOptions, controller) {
            super(page, defaultOptions, controller);
            this.currentIndex = 0;
            this.getPickerElement().onclick = this.pickerChanged(controller);
        }

        pickerChanged(controller) {
            return () => {
                this.currentIndex = (this.currentIndex + 1) % this.options.length;
                this.getPickerElement().querySelector("button").textContent =
                    this.getCurrentOption();
                super.pickerChanged(controller)();
            };
        }

        reverseLocalOptions() {
            super.reverseLocalOptions();
            const button = this.getPickerElement().querySelector("button");
            if (button) {
                button.textContent = this.getCurrentOption();
            }
        }

        getElementInnerHTML() {
            const classes = Array.from(this.switchButton.classList);
            return `
        <div id="${this.page}_ar_default_options_button" class="arl-cycle-btn" style="margin-bottom: 10px;">
            <button class="${classes.join(" ")}">
                ${this.getCurrentOption()}
            </button>
        </div>
        `;
        }

        getPickerElement() {
            return gradioApp().getElementById(`${this.page}_ar_default_options_button`);
        }

        getOptions(defaultOptions) {
            return defaultOptions;
        }

        getCurrentOption() {
            return this.options[this.currentIndex || 0];
        }
    }

    class ResolutionPresetsController {
        constructor(page, controller, toolbox) {
            this.page = page;
            this.controller = controller;

            const wrap = document.createElement("div");
            wrap.id = `${page}_resolution_presets`;
            wrap.className = "arl-resolution-presets";
            wrap.innerHTML = this.buildSelectHtml();

            // Place above the aspect-ratio picker, still next to the swap button.
            toolbox.insertBefore(wrap, toolbox.firstChild);

            this.select = wrap.querySelector("select");
            this.select.addEventListener("change", () => this.onPresetPicked());
        }

        buildSelectHtml() {
            const groups = Core.RESOLUTION_PRESETS.map((group) => {
                const options = group.options
                    .map((opt) => {
                        const key = Core.resolutionPresetKey(opt.width, opt.height);
                        return `<option value="${key}">${opt.label}</option>`;
                    })
                    .join("\n");
                return `<optgroup label="${group.label}">${options}</optgroup>`;
            }).join("\n");

            return `
        <select id="${this.page}_select_resolution_preset" class="gr-box gr-input w-full disabled:cursor-not-allowed" title="Set width × height to a model-native resolution">
            <option value="">Presets…</option>
            ${groups}
        </select>
        `;
        }

        onPresetPicked() {
            const parsed = Core.parseResolutionPreset(this.select.value);
            if (!parsed) return;
            this.controller.applyResolutionPreset(parsed[0], parsed[1]);
            // Reset so the same preset can be re-applied after manual edits.
            this.select.value = "";
        }
    }

    class SliderController {
        constructor(element) {
            this.element = element;
            this.numberInput = this.element.querySelector("input[type=number]");
            this.rangeInput = this.element.querySelector("input[type=range]");
            this.inputs = [this.numberInput, this.rangeInput].filter(Boolean);
            this.inputs.forEach((input) => {
                input.isWidth = element.isWidth;
            });
        }

        getVal() {
            return Number(this.numberInput.value);
        }

        updateVal(value) {
            this.inputs.forEach((input) => {
                input.value = Number(value);
            });
        }

        updateMin(value) {
            this.inputs.forEach((input) => {
                input.min = Core.roundToClosestMultiple(Number(value), 8);
            });
        }

        updateMax(value) {
            this.inputs.forEach((input) => {
                input.max = Core.roundToClosestMultiple(Number(value), 8);
            });
        }

        triggerEvent(event) {
            if (this.numberInput) {
                this.numberInput.dispatchEvent(event);
            }
        }

        setVal(value) {
            const newValue = Core.roundToClosestMultiple(Number(value), 8);
            this.updateVal(newValue);
        }
    }

    class AspectRatioController {
        constructor(page, widthContainer, heightContainer, defaultOptions) {
            widthContainer.isWidth = true;
            heightContainer.isWidth = false;
            this.widthContainer = new SliderController(widthContainer);
            this.heightContainer = new SliderController(heightContainer);
            this.inputs = [
                ...this.widthContainer.inputs,
                ...this.heightContainer.inputs,
            ];
            this.inputs.forEach((input) => {
                input.addEventListener("change", (e) => {
                    e.preventDefault();
                    this.maintainAspectRatio(input);
                });
            });

            const o = getOpts();
            const method = o && o.arl_ui_javascript_selection_method;
            if (method === "Default Options Button") {
                this.optionPickingControler = new DefaultOptionsButtonOptionPickingController(
                    page,
                    defaultOptions,
                    this,
                );
            } else {
                this.optionPickingControler = new SelectOptionPickingController(
                    page,
                    defaultOptions,
                    this,
                );
            }

            this.setAspectRatio(OFF);
        }

        /**
         * Snap W×H to an exact preset resolution. If a ratio lock is active,
         * switch to 🔒 with the preset’s ratio so later drags stay aligned.
         */
        applyResolutionPreset(width, height) {
            const [w, h] = Core.clampToBoundaries(width, height);
            const roundedW = Core.roundToClosestMultiple(w, 8);
            const roundedH = Core.roundToClosestMultiple(h, 8);

            const inputEvent = new Event("input", { bubbles: true });
            this.widthContainer.setVal(roundedW);
            this.widthContainer.triggerEvent(inputEvent);
            this.heightContainer.setVal(roundedH);
            this.heightContainer.triggerEvent(inputEvent);

            if (this.aspectRatio !== OFF) {
                this.aspectRatio = LOCK;
                this.widthRatio = roundedW;
                this.heightRatio = roundedH;
                this.updateInputStates();
                this.syncPickerToLock();
            }

            if (typeof dimensionChange === "function") {
                this.heightContainer.inputs.forEach((input) => {
                    dimensionChange({ target: input }, false, true);
                });
                this.widthContainer.inputs.forEach((input) => {
                    dimensionChange({ target: input }, true, false);
                });
            }
        }

        syncPickerToLock() {
            const picker = this.optionPickingControler;
            if (!picker) return;

            const el = picker.getPickerElement();
            if (el && el.tagName === "SELECT") {
                const options = Array.from(el.options);
                const lockIdx = options.findIndex((o) => o.value === LOCK);
                if (lockIdx >= 0) {
                    el.selectedIndex = lockIdx;
                }
                return;
            }

            if (typeof picker.currentIndex === "number" && Array.isArray(picker.options)) {
                const lockIdx = picker.options.indexOf(LOCK);
                if (lockIdx < 0) return;
                picker.currentIndex = lockIdx;
                const button = el && el.querySelector("button");
                if (button) {
                    button.textContent = LOCK;
                }
            }
        }

        updateInputStates() {
            if (Core.isLandscapeOrSquare(this.widthRatio, this.heightRatio)) {
                const AR = this.widthRatio / this.heightRatio;

                const minWidthByAr = Math.round(MINIMUM_DIMENSION * AR);
                const minWidth = Math.max(minWidthByAr, MINIMUM_DIMENSION);
                this.widthContainer.updateMin(minWidth);
                this.heightContainer.updateMin(MINIMUM_DIMENSION);

                const maxHeightByAr = Math.round(MAXIMUM_DIMENSION / AR);
                const maxHeight = Math.min(MAXIMUM_DIMENSION, maxHeightByAr);
                this.heightContainer.updateMax(maxHeight);
                this.widthContainer.updateMax(MAXIMUM_DIMENSION);
            } else {
                const AR = this.heightRatio / this.widthRatio;

                const minHeightByAr = Math.round(MINIMUM_DIMENSION * AR);
                const minHeight = Math.max(minHeightByAr, MINIMUM_DIMENSION);
                this.heightContainer.updateMin(minHeight);
                this.widthContainer.updateMin(MINIMUM_DIMENSION);

                const maxWidthByAr = Math.round(MAXIMUM_DIMENSION / AR);
                const maxWidth = Math.min(MAXIMUM_DIMENSION, maxWidthByAr);
                this.widthContainer.updateMax(maxWidth);
                this.heightContainer.updateMax(MAXIMUM_DIMENSION);
            }
        }

        disable() {
            this.widthContainer.updateMin(MINIMUM_DIMENSION);
            this.heightContainer.updateMin(MINIMUM_DIMENSION);
            this.widthContainer.updateMax(MAXIMUM_DIMENSION);
            this.heightContainer.updateMax(MAXIMUM_DIMENSION);
        }

        isLandscapeOrSquare() {
            return Core.isLandscapeOrSquare(this.widthRatio, this.heightRatio);
        }

        setAspectRatio(aspectRatio) {
            this.aspectRatio = aspectRatio;

            let wR;
            let hR;
            if (aspectRatio === OFF) {
                return this.disable();
            } else if (aspectRatio === IMAGE) {
                const img = getCurrentImage();
                wR = (img && img.naturalWidth) || 1;
                hR = (img && img.naturalHeight) || 1;
            } else if (aspectRatio === LOCK) {
                wR = this.widthContainer.getVal();
                hR = this.heightContainer.getVal();
            } else {
                const parsed = Core.aspectRatioFromStr(aspectRatio);
                if (!parsed) return this.disable();
                [wR, hR] = parsed;
            }

            [wR, hR] = Core.clampToBoundaries(wR, hR);

            this.widthRatio = wR;
            this.heightRatio = hR;
            this.updateInputStates();
            this.maintainAspectRatio();
        }

        /**
         * Sync internal ratios after Forge swaps W/H. Does not touch slider
         * values — Gradio owns that swap on `_res_switch_btn`.
         */
        flipAspectRatio(picked) {
            const next = Core.ratiosAfterFlip(
                picked,
                this.widthRatio,
                this.heightRatio,
            );
            if (!next) return;

            this.aspectRatio = next.aspectRatio;
            this.widthRatio = next.widthRatio;
            this.heightRatio = next.heightRatio;
            this.updateInputStates();
        }

        maintainAspectRatio(changedElement) {
            if (this.aspectRatio === OFF) return;

            let changedValue;
            let changedIsWidth;
            if (!changedElement) {
                changedValue = Math.max(
                    ...this.inputs.map((x) => Number(x.value)),
                );
                changedIsWidth = undefined;
            } else {
                changedValue = Number(changedElement.value);
                changedIsWidth = changedElement.isWidth;
            }

            const [width, height] = Core.maintainDimensions({
                widthRatio: this.widthRatio,
                heightRatio: this.heightRatio,
                changedValue,
                changedIsWidth,
                currentWidth: this.widthContainer.getVal(),
                currentHeight: this.heightContainer.getVal(),
            });

            const inputEvent = new Event("input", { bubbles: true });
            this.widthContainer.setVal(width);
            this.widthContainer.triggerEvent(inputEvent);
            this.heightContainer.setVal(height);
            this.heightContainer.triggerEvent(inputEvent);

            if (typeof dimensionChange === "function") {
                this.heightContainer.inputs.forEach((input) => {
                    dimensionChange({ target: input }, false, true);
                });
                this.widthContainer.inputs.forEach((input) => {
                    dimensionChange({ target: input }, true, false);
                });
            }
        }

        /**
         * Try to mount once opts + width/height exist. Returns true when done
         * (mounted, disabled by setting, or already present).
         */
        static tryInit(key, page, defaultOptions, postSetup) {
            const o = getOpts();
            if (!o || o.arl_javascript_aspect_ratio_show === undefined) {
                return false;
            }

            if (!o.arl_javascript_aspect_ratio_show) {
                console.warn(
                    "[Aspect Ratio Lock] JavaScript controls disabled in Settings.",
                );
                return true;
            }

            if (gradioApp().getElementById(`${page}_size_toolbox`)) {
                return true;
            }

            const widthContainer = gradioApp().querySelector(`#${page}_width`);
            const heightContainer = gradioApp().querySelector(`#${page}_height`);
            if (!widthContainer || !heightContainer) {
                return false;
            }

            try {
                const controller = new AspectRatioController(
                    page,
                    widthContainer,
                    heightContainer,
                    defaultOptions,
                );
                if (typeof postSetup === "function") {
                    postSetup(controller);
                }
                window[key] = controller;
            } catch (err) {
                console.warn("[Aspect Ratio Lock] init failed:", err);
                return true;
            }
            return true;
        }

        static observeStartup(key, page, defaultOptions, postSetup) {
            if (AspectRatioController.tryInit(key, page, defaultOptions, postSetup)) {
                return;
            }

            const observer = new MutationObserver(() => {
                if (AspectRatioController.tryInit(key, page, defaultOptions, postSetup)) {
                    observer.disconnect();
                }
            });
            observer.observe(gradioApp(), { childList: true, subtree: true });
        }
    }

    function addImg2ImgTabSwitchClickListeners(controller) {
        const img2imgTabButtons = Array.from(
            document.querySelectorAll(
                "#img2img_settings > div > div > button:not(.selected):not(.arl-has-tab-listener)",
            ),
        );
        img2imgTabButtons.forEach((button) => {
            button.addEventListener("click", () => {
                if (controller.optionPickingControler.getCurrentOption() === IMAGE) {
                    controller.setAspectRatio(IMAGE);
                }
                addImg2ImgTabSwitchClickListeners(controller);
            });
            button.classList.add("arl-has-tab-listener");
        });
    }

    function postImageControllerSetupFunction(controller) {
        const scaleToImg2ImgImage = (e) => {
            const picked = controller.optionPickingControler.getCurrentOption();
            if (picked !== IMAGE) return;
            const files = e.dataTransfer ? e.dataTransfer.files : e.target.files;
            if (!files || !files[0]) return;
            const img = new Image();
            img.src = URL.createObjectURL(files[0]);
            img.onload = () => {
                controller.setAspectRatio(`${img.naturalWidth}:${img.naturalHeight}`);
            };
        };

        IMAGE_INPUT_CONTAINER_IDS.forEach((imageContainerId) => {
            const imageContainer = document.getElementById(imageContainerId);
            if (!imageContainer) return;
            const inputElement =
                imageContainer.querySelector("input.forge-file-upload") ||
                imageContainer.querySelector('input[type="file"]');
            if (!inputElement) return;
            const dropTarget = inputElement.parentElement || imageContainer;
            dropTarget.addEventListener("drop", scaleToImg2ImgImage);
            inputElement.addEventListener("change", scaleToImg2ImgImage);
        });

        addImg2ImgTabSwitchClickListeners(controller);
    }

    function start() {
        AspectRatioController.observeStartup("__txt2imgAspectRatioController", "txt2img", [
            OFF,
            LOCK,
        ]);
        AspectRatioController.observeStartup(
            "__img2imgAspectRatioController",
            "img2img",
            [OFF, LOCK, IMAGE],
            postImageControllerSetupFunction,
        );
    }

    // Prefer onOptionsAvailable: opts is filled async after UI load, without a
    // guaranteed follow-up DOM mutation for our MutationObserver.
    if (typeof onOptionsAvailable === "function") {
        onOptionsAvailable(start);
    } else if (typeof onUiLoaded === "function") {
        onUiLoaded(start);
    } else {
        document.addEventListener("DOMContentLoaded", start);
    }
})();
