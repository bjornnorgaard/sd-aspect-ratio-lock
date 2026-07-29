/**
 * Pure aspect-ratio helpers shared by the UI script and Node tests.
 * Loaded as a plain script in Forge (sets globalThis.ArlCore) and via require() in tests.
 */
(function (root, factory) {
    const api = factory();
    if (typeof module === "object" && module.exports) {
        module.exports = api;
    }
    root.ArlCore = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
    "use strict";

    const OFF = "Off";
    const LOCK = "🔒";
    const IMAGE = "🖼️";
    const MAXIMUM_DIMENSION = 2048;
    const MINIMUM_DIMENSION = 64;

    function roundToClosestMultiple(num, multiple) {
        return Math.round(Number(num) / multiple) * multiple;
    }

    function aspectRatioFromStr(ar) {
        if (!ar || !String(ar).includes(":")) return null;
        const parts = String(ar).split(":").map((x) => Number(x));
        if (parts.length !== 2 || parts.some((n) => !Number.isFinite(n) || n <= 0)) {
            return null;
        }
        return parts;
    }

    function reverseAspectRatio(ar) {
        const parts = aspectRatioFromStr(ar);
        if (!parts) return null;
        return `${parts[1]}:${parts[0]}`;
    }

    function clampToBoundaries(width, height) {
        const aspectRatio = width / height;
        width = Math.max(Math.min(width, MAXIMUM_DIMENSION), MINIMUM_DIMENSION);
        height = Math.max(Math.min(height, MAXIMUM_DIMENSION), MINIMUM_DIMENSION);
        if (width / height > aspectRatio) {
            height = Math.round(width / aspectRatio);
        } else if (width / height < aspectRatio) {
            width = Math.round(height * aspectRatio);
        }

        if (width > MAXIMUM_DIMENSION) {
            width = MAXIMUM_DIMENSION;
        } else if (width < MINIMUM_DIMENSION) {
            width = MINIMUM_DIMENSION;
        }

        if (height < MINIMUM_DIMENSION) {
            height = MINIMUM_DIMENSION;
        } else if (height > MAXIMUM_DIMENSION) {
            height = MAXIMUM_DIMENSION;
        }

        return [width, height];
    }

    function isLandscapeOrSquare(widthRatio, heightRatio) {
        return widthRatio >= heightRatio;
    }

    /**
     * Ratios to store after the user hits Forge's W/H swap button.
     * Dimensions themselves are swapped by Gradio — we must not rewrite them here.
     */
    function ratiosAfterFlip(picked, widthRatio, heightRatio) {
        if (picked === OFF) {
            return null;
        }

        if (picked === LOCK || picked === IMAGE) {
            if (widthRatio == null || heightRatio == null) return null;
            return {
                aspectRatio: picked,
                widthRatio: heightRatio,
                heightRatio: widthRatio,
            };
        }

        const parsed = aspectRatioFromStr(picked);
        if (!parsed) return null;
        const [wR, hR] = clampToBoundaries(parsed[0], parsed[1]);
        return {
            aspectRatio: picked,
            widthRatio: wR,
            heightRatio: hR,
        };
    }

    /**
     * Compute W×H after a slider/number change (or after picking a ratio with no
     * specific side changed — then the larger current side is treated as dominant).
     */
    function maintainDimensions({
        widthRatio,
        heightRatio,
        changedValue,
        changedIsWidth,
        currentWidth,
        currentHeight,
    }) {
        const aspectRatio = widthRatio / heightRatio;
        let w;
        let h;

        if (changedIsWidth === undefined || changedIsWidth === null) {
            const value =
                changedValue != null
                    ? changedValue
                    : Math.max(Number(currentWidth), Number(currentHeight));
            if (isLandscapeOrSquare(widthRatio, heightRatio)) {
                w = Math.round(value);
                h = Math.round(value / aspectRatio);
            } else {
                h = Math.round(value);
                w = Math.round(value * aspectRatio);
            }
        } else if (changedIsWidth) {
            w = Math.round(changedValue);
            h = Math.round(changedValue / aspectRatio);
        } else {
            h = Math.round(changedValue);
            w = Math.round(changedValue * aspectRatio);
        }

        return clampToBoundaries(w, h);
    }

    function reverseRatioOptions(values) {
        return values.map((value) => reverseAspectRatio(value) || value);
    }

    return {
        OFF,
        LOCK,
        IMAGE,
        MAXIMUM_DIMENSION,
        MINIMUM_DIMENSION,
        roundToClosestMultiple,
        aspectRatioFromStr,
        reverseAspectRatio,
        clampToBoundaries,
        isLandscapeOrSquare,
        ratiosAfterFlip,
        maintainDimensions,
        reverseRatioOptions,
    };
});
