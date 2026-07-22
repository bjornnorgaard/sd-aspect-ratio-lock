/**
 * Node tests for javascript/arl_core.js (flip + maintain math).
 * Run: node tests/js/test_arl_core.mjs
 */
import { createRequire } from "module";
import { fileURLToPath } from "url";
import path from "path";

const require = createRequire(import.meta.url);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const Core = require(path.resolve(__dirname, "../../javascript/arl_core.js"));

let failed = 0;

function assertEqual(actual, expected, msg) {
    const a = JSON.stringify(actual);
    const e = JSON.stringify(expected);
    if (a !== e) {
        console.error(`FAIL: ${msg}\n  expected: ${e}\n  actual:   ${a}`);
        failed += 1;
    }
}

function assert(cond, msg) {
    if (!cond) {
        console.error(`FAIL: ${msg}`);
        failed += 1;
    }
}

// reverseAspectRatio
assertEqual(Core.reverseAspectRatio("16:9"), "9:16", "reverse 16:9");
assertEqual(Core.reverseAspectRatio("1:1"), "1:1", "reverse 1:1");
assertEqual(Core.reverseAspectRatio("Off"), null, "reverse Off");
assertEqual(Core.reverseAspectRatio("🔒"), null, "reverse LOCK");

// reverseRatioOptions leaves non-ratios alone
assertEqual(
    Core.reverseRatioOptions(["Off", "🔒", "16:9", "4:3"]),
    ["Off", "🔒", "9:16", "3:4"],
    "reverse option list",
);

// ratiosAfterFlip: preset — use flipped picker value, do not touch dims
{
    const before = Core.clampToBoundaries(16, 9);
    const flippedPick = Core.reverseAspectRatio("16:9");
    const next = Core.ratiosAfterFlip(flippedPick, before[0], before[1]);
    assert(next, "flip preset returns ratios");
    assertEqual(next.aspectRatio, "9:16", "flip preset stores 9:16");
    assert(
        next.widthRatio < next.heightRatio,
        "flip preset is portrait",
    );
}

// ratiosAfterFlip: LOCK swaps stored ratio components
{
    const next = Core.ratiosAfterFlip(Core.LOCK, 1920, 1080);
    assertEqual(
        next,
        { aspectRatio: Core.LOCK, widthRatio: 1080, heightRatio: 1920 },
        "flip LOCK swaps ratio components",
    );
}

// ratiosAfterFlip: OFF is a no-op (Gradio still swaps dims freely)
assertEqual(Core.ratiosAfterFlip(Core.OFF, 1024, 576), null, "flip OFF");

// maintain after flip: Gradio swapped dims; slider adjust must keep portrait
{
    const landscape = Core.clampToBoundaries(16, 9);
    const flipped = Core.ratiosAfterFlip("9:16", landscape[0], landscape[1]);
    // Simulate Forge swap: 1024×576 → 576×1024
    const afterSwapW = 576;
    const afterSwapH = 1024;
    const [w1, h1] = Core.maintainDimensions({
        widthRatio: flipped.widthRatio,
        heightRatio: flipped.heightRatio,
        changedValue: afterSwapW,
        changedIsWidth: true,
        currentWidth: afterSwapW,
        currentHeight: afterSwapH,
    });
    assert(w1 < h1, "width change after flip stays portrait");
    assert(
        Math.abs(w1 / h1 - flipped.widthRatio / flipped.heightRatio) < 0.05,
        "width change after flip keeps AR",
    );

    const [w2, h2] = Core.maintainDimensions({
        widthRatio: flipped.widthRatio,
        heightRatio: flipped.heightRatio,
        changedValue: 1280,
        changedIsWidth: false,
        currentWidth: afterSwapW,
        currentHeight: afterSwapH,
    });
    assert(w2 < h2, "height change after flip stays portrait");
    assert(
        Math.abs(w2 / h2 - flipped.widthRatio / flipped.heightRatio) < 0.05,
        "height change after flip keeps AR",
    );
}

// Regression: old bug path — dims swapped but ratios left landscape → snap back
{
    const landscape = Core.clampToBoundaries(16, 9);
    const [w, h] = Core.maintainDimensions({
        widthRatio: landscape[0],
        heightRatio: landscape[1],
        changedValue: 576,
        changedIsWidth: true,
        currentWidth: 576,
        currentHeight: 1024,
    });
    assert(w > h, "stale landscape ratios force landscape (the bug)");
}

// maintain with no changed side uses max dimension as dominant
{
    const [lw, lh] = Core.maintainDimensions({
        widthRatio: 16,
        heightRatio: 9,
        changedValue: null,
        changedIsWidth: undefined,
        currentWidth: 512,
        currentHeight: 512,
    });
    assert(lw >= lh, "landscape pick from square stays landscape");

    const [pw, ph] = Core.maintainDimensions({
        widthRatio: 9,
        heightRatio: 16,
        changedValue: null,
        changedIsWidth: undefined,
        currentWidth: 512,
        currentHeight: 512,
    });
    assert(pw <= ph, "portrait pick from square stays portrait");
}

// RESOLUTION_PRESETS: SDXL/Pony + Illustrious buckets stay in-bounds / step-8
{
    assert(Array.isArray(Core.RESOLUTION_PRESETS), "presets is an array");
    assertEqual(
        Core.RESOLUTION_PRESETS.map((g) => g.label),
        ["SDXL / Pony", "Illustrious"],
        "preset group labels",
    );

    for (const group of Core.RESOLUTION_PRESETS) {
        assert(group.options.length > 0, `${group.label} has options`);
        for (const opt of group.options) {
            assert(
                opt.width % 8 === 0 && opt.height % 8 === 0,
                `${opt.label} is multiple of 8`,
            );
            assert(
                opt.width >= Core.MINIMUM_DIMENSION &&
                    opt.width <= Core.MAXIMUM_DIMENSION &&
                    opt.height >= Core.MINIMUM_DIMENSION &&
                    opt.height <= Core.MAXIMUM_DIMENSION,
                `${opt.label} within dimension bounds`,
            );
            const key = Core.resolutionPresetKey(opt.width, opt.height);
            assertEqual(
                Core.parseResolutionPreset(key),
                [opt.width, opt.height],
                `parse ${key}`,
            );
        }
    }

    assertEqual(
        Core.parseResolutionPreset("1024x1024"),
        [1024, 1024],
        "parse square SDXL",
    );
    assertEqual(
        Core.parseResolutionPreset("832x1216"),
        [832, 1216],
        "parse Pony portrait",
    );
    assertEqual(
        Core.parseResolutionPreset("1536x1536"),
        [1536, 1536],
        "parse Illustrious square",
    );
    assertEqual(Core.parseResolutionPreset(""), null, "parse empty");
    assertEqual(Core.parseResolutionPreset("Off"), null, "parse Off");
}

if (failed) {
    console.error(`\n${failed} failure(s)`);
    process.exit(1);
}
console.log("All arl_core JS tests passed.");
