from __future__ import annotations

import sys
import unittest
from pathlib import Path

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
if str(EXTENSION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXTENSION_ROOT))

from lib_aspect_ratio_lock import constants
from lib_aspect_ratio_lock import util


class DisplayFormatTests(unittest.TestCase):
    def test_display_multiplication(self):
        self.assertEqual(util.display_multiplication(50), "x0.5")
        self.assertEqual(util.display_multiplication(150), "x1.5")
        self.assertEqual(util.display_multiplication(175), "x1.75")
        self.assertEqual(util.display_multiplication(250), "x2.5")

    def test_display_raw_percentage(self):
        self.assertEqual(util.display_raw_percentage(50), "50%")
        self.assertEqual(util.display_raw_percentage(100), "100%")
        self.assertEqual(util.display_raw_percentage(150), "150%")

    def test_display_minus_and_plus(self):
        self.assertEqual(util.display_minus_and_plus(150), "+50%")
        self.assertEqual(util.display_minus_and_plus(100), "0%")
        self.assertEqual(util.display_minus_and_plus(50), "-50%")
        self.assertEqual(util.display_minus_and_plus(0), "-100%")
        self.assertEqual(util.display_minus_and_plus(200), "+100%")
        self.assertEqual(util.display_minus_and_plus(75), "-25%")


class ScaleByPercentageTests(unittest.TestCase):
    def test_scale_down_50(self):
        self.assertEqual(util.scale_by_percentage(200, 400, 0.5), (96, 200))

    def test_scale_up_200(self):
        self.assertEqual(util.scale_by_percentage(100, 200, 2.0), (200, 400))

    def test_scale_up_10(self):
        self.assertEqual(util.scale_by_percentage(100, 200, 1.1), (112, 224))

    def test_scale_down_10(self):
        self.assertEqual(util.scale_by_percentage(100, 200, 0.9), (88, 176))

    def test_scale_full_down(self):
        self.assertEqual(util.scale_by_percentage(100, 200, 0.0), (64, 128))

    def test_scale_below_min(self):
        below = constants.MIN_DIMENSION - 1
        self.assertEqual(
            util.scale_by_percentage(below, below, 0.5),
            (constants.MIN_DIMENSION, constants.MIN_DIMENSION),
        )

    def test_scale_above_max(self):
        above = constants.MAX_DIMENSION + 1
        self.assertEqual(
            util.scale_by_percentage(above, above, 2.0),
            (constants.MAX_DIMENSION, constants.MAX_DIMENSION),
        )


class ScaleToMaxDimTests(unittest.TestCase):
    def test_scale_up_portrait(self):
        self.assertEqual(util.scale_dimensions_to_max_dim(100, 200, 400), (200, 400))

    def test_scale_up_landscape(self):
        self.assertEqual(util.scale_dimensions_to_max_dim(200, 100, 400), (400, 200))

    def test_already_at_max_width(self):
        self.assertEqual(util.scale_dimensions_to_max_dim(400, 64, 400), (400, 64))

    def test_already_at_max_height(self):
        self.assertEqual(util.scale_dimensions_to_max_dim(64, 400, 400), (64, 400))

    def test_min_to_max(self):
        self.assertEqual(
            util.scale_dimensions_to_max_dim(
                constants.MIN_DIMENSION,
                constants.MIN_DIMENSION,
                constants.MAX_DIMENSION,
            ),
            (constants.MAX_DIMENSION, constants.MAX_DIMENSION),
        )

    def test_max_to_min(self):
        self.assertEqual(
            util.scale_dimensions_to_max_dim(
                constants.MAX_DIMENSION,
                constants.MAX_DIMENSION,
                constants.MIN_DIMENSION,
            ),
            (constants.MIN_DIMENSION, constants.MIN_DIMENSION),
        )

    def test_clamp_retains_ar_below_min_height(self):
        self.assertEqual(
            util.scale_dimensions_to_max_dim(
                constants.MIN_DIMENSION,
                32,
                constants.MIN_DIMENSION,
            ),
            (128, constants.MIN_DIMENSION),
        )

    def test_clamp_retains_ar_below_min_width(self):
        self.assertEqual(
            util.scale_dimensions_to_max_dim(
                32,
                constants.MIN_DIMENSION,
                constants.MIN_DIMENSION,
            ),
            (constants.MIN_DIMENSION, 128),
        )


class ScaleToMinDimTests(unittest.TestCase):
    def test_scale_up_portrait(self):
        self.assertEqual(util.scale_dimensions_to_min_dim(100, 200, 400), (400, 800))

    def test_scale_up_landscape(self):
        self.assertEqual(util.scale_dimensions_to_min_dim(200, 100, 400), (800, 400))

    def test_square(self):
        self.assertEqual(util.scale_dimensions_to_min_dim(100, 100, 400), (400, 400))

    def test_min_to_max(self):
        self.assertEqual(
            util.scale_dimensions_to_min_dim(
                constants.MIN_DIMENSION,
                constants.MIN_DIMENSION,
                constants.MAX_DIMENSION,
            ),
            (constants.MAX_DIMENSION, constants.MAX_DIMENSION),
        )

    def test_max_to_min(self):
        self.assertEqual(
            util.scale_dimensions_to_min_dim(
                constants.MAX_DIMENSION,
                constants.MAX_DIMENSION,
                constants.MIN_DIMENSION,
            ),
            (constants.MIN_DIMENSION, constants.MIN_DIMENSION),
        )


class RoundAndClampTests(unittest.TestCase):
    def test_round_to_multiple_of_8(self):
        cases = [
            (0, 0),
            (7, 8),
            (10, 8),
            (16, 16),
            (23, 24),
            (32, 32),
            (33, 32),
            (100, 96),
            (10.5, 8),
            (15.3, 16),
            (21.8, 24),
            (33.9, 32),
            (98.7, 96),
        ]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(util.round_to_multiple_of_8(value), expected)

    def test_clamp_to_boundaries(self):
        cases = [
            (100, 100, 1.0, (96, 96)),
            (3000, 2000, 1.5, (2048, 1368)),
            (500, 8000, 0.5, (1024, 2048)),
            (500, 300, 2.0, (496, 304)),
            (100, 200, 0.5, (96, 200)),
            (500, 500, 1.2, (496, 496)),
            (2048, 2048, 1.0, (2048, 2048)),
            (2049, 2048, 1.0, (2048, 2048)),
            (2048, 2049, 1.0, (2048, 2048)),
            (2049, 2049, 1.0, (2048, 2048)),
            (63, 63, 1.0, (64, 64)),
            (2050, 2050, 1.0, (2048, 2048)),
            (63, 64, 1.0, (64, 64)),
            (64, 63, 1.0, (64, 64)),
            (64, 64, 1.0, (64, 64)),
            (2050, 63, 1.0, (2048, 2048)),
            (63, 2050, 1.0, (2048, 2048)),
            (2050, 2050, 0.01, (64, 2048)),
            (100.5, 100.5, 1.0, (104, 104)),
            (200.3, 100.7, 0.5, (200, 104)),
        ]
        for width, height, aspect_ratio, expected in cases:
            with self.subTest(width=width, height=height, ar=aspect_ratio):
                self.assertEqual(
                    util.clamp_to_boundaries(width, height, aspect_ratio),
                    expected,
                )


class SharedOpts:
    def __init__(self, options=None, defaults=None):
        self.options = options or {}
        self.defaults = defaults or {}

    def __getattr__(self, key):
        try:
            return self.options[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def get_default(self, key):
        return self.defaults.get(key, None)


class SafeOptTests(unittest.TestCase):
    def test_live_value(self):
        shared_opts = SharedOpts(options={"key": "value"})
        self.assertEqual(util.safe_opt_util(shared_opts, "key", {}), "value")

    def test_none_falls_back_to_default(self):
        shared_opts = SharedOpts(options={"key": None}, defaults={"key": "value"})
        self.assertEqual(util.safe_opt_util(shared_opts, "key", {}), "value")

    def test_registered_default(self):
        shared_opts = SharedOpts(defaults={"key": "default_a"})
        self.assertEqual(
            util.safe_opt_util(shared_opts, "key", {"key": "default_b"}),
            "default_a",
        )

    def test_hardcoded_default(self):
        shared_opts = SharedOpts(defaults={"key": None})
        self.assertEqual(
            util.safe_opt_util(shared_opts, "key", {"key": "default_b"}),
            "default_b",
        )

    def test_unknown_key(self):
        for options in ({"key": None}, {}):
            with self.subTest(options=options):
                shared_opts = SharedOpts(options=options)
                self.assertIsNone(util.safe_opt_util(shared_opts, "unknown_key", {}))


if __name__ == "__main__":
    unittest.main()
