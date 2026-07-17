from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

# settings.py imports modules.shared / gradio — stub them for standalone tests.
sys.modules.setdefault("gradio", MagicMock())
sys.modules.setdefault("modules", MagicMock())
sys.modules.setdefault("modules.shared", MagicMock())
sys.modules.setdefault("modules.scripts", MagicMock())
sys.modules.setdefault("modules.script_callbacks", MagicMock())

from lib_aspect_ratio_lock import constants  # noqa: E402
from lib_aspect_ratio_lock import settings  # noqa: E402
from lib_aspect_ratio_lock.components import (  # noqa: E402
    MaxDimensionScaler,
    MinDimensionScaler,
    PredefinedAspectRatioButtons,
    PredefinedPercentageButtons,
)


class SettingsDefaultsTests(unittest.TestCase):
    def test_default_order_lists_all_components(self):
        names = settings.DEFAULT_UI_COMPONENT_ORDER_KEY_LIST
        self.assertEqual(
            names,
            [
                "MaxDimensionScaler",
                "MinDimensionScaler",
                "PredefinedAspectRatioButtons",
                "PredefinedPercentageButtons",
            ],
        )
        self.assertEqual(
            settings.DEFAULT_UI_COMPONENT_ORDER_KEY,
            ", ".join(names),
        )

    def test_opt_defaults_cover_all_constant_keys(self):
        expected_keys = {
            constants.ARL_EXPAND_BY_DEFAULT_KEY,
            constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY,
            constants.ARL_UI_COMPONENT_ORDER_KEY,
            constants.ARL_UI_JAVASCRIPT_SELECTION_METHOD,
            constants.ARL_JAVASCRIPT_ASPECT_RATIO_SHOW_KEY,
            constants.ARL_JAVASCRIPT_ASPECT_RATIOS_KEY,
            constants.ARL_SHOW_MAX_WIDTH_OR_HEIGHT_KEY,
            constants.ARL_MAX_WIDTH_OR_HEIGHT_KEY,
            constants.ARL_SHOW_MIN_WIDTH_OR_HEIGHT_KEY,
            constants.ARL_MIN_WIDTH_OR_HEIGHT_KEY,
            constants.ARL_SHOW_PREDEFINED_PERCENTAGES_KEY,
            constants.ARL_PREDEFINED_PERCENTAGES_KEY,
            constants.ARL_PREDEFINED_PERCENTAGES_DISPLAY_KEY,
            constants.ARL_SHOW_PREDEFINED_ASPECT_RATIOS_KEY,
            constants.ARL_PREDEFINED_ASPECT_RATIO_USE_MAX_DIM_KEY,
            constants.ARL_PREDEFINED_ASPECT_RATIOS_KEY,
        }
        self.assertEqual(set(settings.OPT_KEY_TO_DEFAULT_MAP), expected_keys)

    def test_js_enabled_by_default(self):
        self.assertTrue(
            settings.OPT_KEY_TO_DEFAULT_MAP[
                constants.ARL_JAVASCRIPT_ASPECT_RATIO_SHOW_KEY
            ],
        )

    def test_accordion_hidden_by_default(self):
        self.assertTrue(
            settings.OPT_KEY_TO_DEFAULT_MAP[
                constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY
            ],
        )

    def test_percentage_display_map(self):
        self.assertIn(
            constants.DEFAULT_PERCENTAGES_DISPLAY_KEY,
            settings.PREDEFINED_PERCENTAGES_DISPLAY_MAP,
        )
        self.assertEqual(len(settings.PREDEFINED_PERCENTAGES_DISPLAY_MAP), 3)


class SortComponentsTests(unittest.TestCase):
    def setUp(self):
        self.script = MagicMock()
        self.instances = [
            MaxDimensionScaler(self.script),
            MinDimensionScaler(self.script),
            PredefinedAspectRatioButtons(self.script),
            PredefinedPercentageButtons(self.script),
        ]

    def test_sort_respects_configured_order(self):
        order = (
            "PredefinedPercentageButtons, MaxDimensionScaler, "
            "MinDimensionScaler, PredefinedAspectRatioButtons"
        )
        with patch.object(settings, "safe_opt", return_value=order):
            sorted_components = settings.sort_components_by_keys(list(self.instances))
        self.assertEqual(
            [c.__class__.__name__ for c in sorted_components],
            [
                "PredefinedPercentageButtons",
                "MaxDimensionScaler",
                "MinDimensionScaler",
                "PredefinedAspectRatioButtons",
            ],
        )

    def test_sort_appends_missing_components(self):
        # Simulate a stale user setting that only lists two components.
        with patch.object(
            settings,
            "safe_opt",
            return_value="MaxDimensionScaler, MinDimensionScaler",
        ):
            sorted_components = settings.sort_components_by_keys(list(self.instances))
        names = [c.__class__.__name__ for c in sorted_components]
        self.assertEqual(names[:2], ["MaxDimensionScaler", "MinDimensionScaler"])
        self.assertCountEqual(
            names[2:],
            ["PredefinedAspectRatioButtons", "PredefinedPercentageButtons"],
        )


class ConstantsTests(unittest.TestCase):
    def test_dimension_bounds(self):
        self.assertEqual(constants.MIN_DIMENSION, 64)
        self.assertEqual(constants.MAX_DIMENSION, 2048)

    def test_section_tuple(self):
        self.assertEqual(
            constants.SECTION,
            ("aspect_ratio_lock", "Aspect Ratio Lock"),
        )

    def test_option_keys_use_arl_prefix(self):
        for name in dir(constants):
            if name.startswith("ARL_") and name.endswith("_KEY"):
                value = getattr(constants, name)
                self.assertTrue(
                    str(value).startswith("arl_"),
                    f"{name}={value!r} should start with arl_",
                )


if __name__ == "__main__":
    unittest.main()
