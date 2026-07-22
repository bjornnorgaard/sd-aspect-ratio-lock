from __future__ import annotations

import itertools
import logging

import gradio as gr
from modules import shared

from lib_aspect_ratio_lock import components
from lib_aspect_ratio_lock import constants
from lib_aspect_ratio_lock import util

logger = logging.getLogger(__name__)

PREDEFINED_PERCENTAGES_DISPLAY_MAP = {
    constants.DEFAULT_PERCENTAGES_DISPLAY_KEY: util.display_minus_and_plus,
    "Raw percentage (50%, 150%)": util.display_raw_percentage,
    "Multiplication (x0.5, x1.5)": util.display_multiplication,
}

COMPONENTS = (
    components.MaxDimensionScaler,
    components.MinDimensionScaler,
    components.PredefinedAspectRatioButtons,
    components.PredefinedPercentageButtons,
)

DEFAULT_UI_COMPONENT_ORDER_KEY_LIST = [e.__name__ for e in COMPONENTS]
DEFAULT_UI_COMPONENT_ORDER_KEY = ", ".join(DEFAULT_UI_COMPONENT_ORDER_KEY_LIST)

OPT_KEY_TO_DEFAULT_MAP: dict[str, object] = {
    constants.ARL_EXPAND_BY_DEFAULT_KEY: False,
    constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY: True,
    constants.ARL_UI_COMPONENT_ORDER_KEY: DEFAULT_UI_COMPONENT_ORDER_KEY,
    constants.ARL_UI_JAVASCRIPT_SELECTION_METHOD: "Aspect Ratios Dropdown",
    constants.ARL_JAVASCRIPT_ASPECT_RATIO_SHOW_KEY: True,
    constants.ARL_JAVASCRIPT_ASPECT_RATIOS_KEY: "1:1, 3:2, 4:3, 5:4, 16:9",
    constants.ARL_JAVASCRIPT_RESOLUTION_PRESETS_SHOW_KEY: True,
    constants.ARL_SHOW_MAX_WIDTH_OR_HEIGHT_KEY: False,
    constants.ARL_MAX_WIDTH_OR_HEIGHT_KEY: constants.MAX_DIMENSION / 2,
    constants.ARL_SHOW_MIN_WIDTH_OR_HEIGHT_KEY: False,
    constants.ARL_MIN_WIDTH_OR_HEIGHT_KEY: constants.MAX_DIMENSION / 2,
    constants.ARL_SHOW_PREDEFINED_PERCENTAGES_KEY: False,
    constants.ARL_PREDEFINED_PERCENTAGES_KEY: "25, 50, 75, 125, 150, 175, 200",
    constants.ARL_PREDEFINED_PERCENTAGES_DISPLAY_KEY: (
        constants.DEFAULT_PERCENTAGES_DISPLAY_KEY
    ),
    constants.ARL_SHOW_PREDEFINED_ASPECT_RATIOS_KEY: False,
    constants.ARL_PREDEFINED_ASPECT_RATIO_USE_MAX_DIM_KEY: False,
    constants.ARL_PREDEFINED_ASPECT_RATIOS_KEY: "1:1, 4:3, 16:9, 9:16, 21:9",
}


def safe_opt(key: str):
    return util.safe_opt_util(shared.opts, key, OPT_KEY_TO_DEFAULT_MAP)


def sort_components_by_keys(
    items: list[components.ArhUIComponent],
) -> list[components.ArhUIComponent]:
    ordered_component_keys = safe_opt(constants.ARL_UI_COMPONENT_ORDER_KEY).split(",")

    # Old settings may omit components added in a later version.
    if len(ordered_component_keys) != len(COMPONENTS):
        all_components = set(DEFAULT_UI_COMPONENT_ORDER_KEY_LIST)
        missing_components = all_components - {k.strip() for k in ordered_component_keys}
        ordered_component_keys.extend(sorted(missing_components))

    try:
        component_key_to_order_dict = {
            key: order
            for order, key in enumerate([k.strip() for k in ordered_component_keys])
        }
        return sorted(
            items,
            key=lambda c: component_key_to_order_dict.get(c.__class__.__name__, 999),
        )
    except ValueError:
        logger.warning(
            "%s UI component order is invalid; defaulting to built-in order. "
            'Expected something like "%s".',
            constants.EXTENSION_NAME,
            DEFAULT_UI_COMPONENT_ORDER_KEY,
        )
        return items


def on_ui_settings() -> None:
    shared.opts.add_option(
        key=constants.ARL_JAVASCRIPT_ASPECT_RATIO_SHOW_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(
                constants.ARL_JAVASCRIPT_ASPECT_RATIO_SHOW_KEY,
            ),
            label="Enable JavaScript aspect ratio controls",
            section=constants.SECTION,
        ),
    )
    shared.opts.add_option(
        key=constants.ARL_JAVASCRIPT_ASPECT_RATIOS_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(
                constants.ARL_JAVASCRIPT_ASPECT_RATIOS_KEY,
            ),
            label="JavaScript aspect ratio list (1:1, 4:3, 16:9, …)",
            section=constants.SECTION,
        ),
    )
    shared.opts.add_option(
        key=constants.ARL_JAVASCRIPT_RESOLUTION_PRESETS_SHOW_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(
                constants.ARL_JAVASCRIPT_RESOLUTION_PRESETS_SHOW_KEY,
            ),
            label=(
                "Include SDXL / Pony / Illustrious resolution presets "
                "in the aspect ratio dropdown"
            ),
            section=constants.SECTION,
        ),
    )
    shared.opts.add_option(
        key=constants.ARL_UI_JAVASCRIPT_SELECTION_METHOD,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(
                constants.ARL_UI_JAVASCRIPT_SELECTION_METHOD,
            ),
            label="JavaScript selection method",
            component=gr.Dropdown,
            component_args=lambda: {
                "choices": [
                    "Aspect Ratios Dropdown",
                    "Default Options Button",
                ],
            },
            section=constants.SECTION,
        ),
    )

    shared.opts.add_option(
        key=constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(
                constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY,
            ),
            label="Hide accordion by default",
            section=constants.SECTION,
        ),
    )
    shared.opts.add_option(
        key=constants.ARL_EXPAND_BY_DEFAULT_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(constants.ARL_EXPAND_BY_DEFAULT_KEY),
            label="Expand accordion by default",
            section=constants.SECTION,
        ),
    )
    shared.opts.add_option(
        key=constants.ARL_UI_COMPONENT_ORDER_KEY,
        info=shared.OptionInfo(
            default=OPT_KEY_TO_DEFAULT_MAP.get(constants.ARL_UI_COMPONENT_ORDER_KEY),
            label="UI component order",
            component=gr.Dropdown,
            component_args=lambda: {
                "choices": [
                    ", ".join(p)
                    for p in itertools.permutations(DEFAULT_UI_COMPONENT_ORDER_KEY_LIST)
                ],
            },
            section=constants.SECTION,
        ),
    )

    for component in COMPONENTS:
        component.add_options(shared)
