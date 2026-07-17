from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial

import gradio as gr

from lib_aspect_ratio_lock import constants
from lib_aspect_ratio_lock import settings
from lib_aspect_ratio_lock import util


class ArhUIComponent(ABC):
    def __init__(self, script):
        self.script = script

    @abstractmethod
    def render(self): ...

    @staticmethod
    @abstractmethod
    def should_show() -> bool: ...

    @staticmethod
    @abstractmethod
    def add_options(shared): ...


class MaxDimensionScaler(ArhUIComponent):
    def render(self):
        max_dim_default = settings.safe_opt(constants.ARL_MAX_WIDTH_OR_HEIGHT_KEY)
        self.script.max_dimension = float(max_dim_default)

        inputs = outputs = [self.script.wc, self.script.hc]

        with gr.Row(visible=self.should_show()):
            # Gradio 4 (Forge Neo): use gr.Slider(value=...), not gr.inputs.Slider.
            max_dimension_slider = gr.Slider(
                minimum=constants.MIN_DIMENSION,
                maximum=constants.MAX_DIMENSION,
                step=8,
                value=max_dim_default,
                label="Maximum dimension",
            )

            def _update_max_dimension(_max_dimension):
                self.script.max_dimension = _max_dimension

            max_dimension_slider.change(
                _update_max_dimension,
                inputs=[max_dimension_slider],
                show_progress=False,
            )

            gr.Button(
                value="Scale to maximum dimension",
                visible=self.should_show(),
            ).click(
                fn=util.scale_dimensions_to_max_dim,
                inputs=[*inputs, max_dimension_slider],
                outputs=outputs,
            )

    @staticmethod
    def should_show() -> bool:
        return settings.safe_opt(constants.ARL_SHOW_MAX_WIDTH_OR_HEIGHT_KEY)

    @staticmethod
    def add_options(shared):
        shared.opts.add_option(
            key=constants.ARL_SHOW_MAX_WIDTH_OR_HEIGHT_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_SHOW_MAX_WIDTH_OR_HEIGHT_KEY,
                ),
                label="Show maximum dimension button",
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_MAX_WIDTH_OR_HEIGHT_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_MAX_WIDTH_OR_HEIGHT_KEY,
                ),
                label="Maximum dimension default",
                component=gr.Slider,
                component_args={
                    "minimum": constants.MIN_DIMENSION,
                    "maximum": constants.MAX_DIMENSION,
                    "step": 8,
                },
                section=constants.SECTION,
            ),
        )


class MinDimensionScaler(ArhUIComponent):
    def render(self):
        min_dim_default = settings.safe_opt(constants.ARL_MIN_WIDTH_OR_HEIGHT_KEY)
        self.script.min_dimension = float(min_dim_default)

        inputs = outputs = [self.script.wc, self.script.hc]

        with gr.Row(visible=self.should_show()):
            min_dimension_slider = gr.Slider(
                minimum=constants.MIN_DIMENSION,
                maximum=constants.MAX_DIMENSION,
                step=8,
                value=min_dim_default,
                label="Minimum dimension",
            )

            def _update_min_dimension(_min_dimension):
                self.script.min_dimension = _min_dimension

            min_dimension_slider.change(
                _update_min_dimension,
                inputs=[min_dimension_slider],
                show_progress=False,
            )

            gr.Button(
                value="Scale to minimum dimension",
                visible=self.should_show(),
            ).click(
                fn=util.scale_dimensions_to_min_dim,
                inputs=[*inputs, min_dimension_slider],
                outputs=outputs,
            )

    @staticmethod
    def should_show() -> bool:
        return settings.safe_opt(constants.ARL_SHOW_MIN_WIDTH_OR_HEIGHT_KEY)

    @staticmethod
    def add_options(shared):
        shared.opts.add_option(
            key=constants.ARL_SHOW_MIN_WIDTH_OR_HEIGHT_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_SHOW_MIN_WIDTH_OR_HEIGHT_KEY,
                ),
                label="Show minimum dimension button",
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_MIN_WIDTH_OR_HEIGHT_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_MIN_WIDTH_OR_HEIGHT_KEY,
                ),
                label="Minimum dimension default",
                component=gr.Slider,
                component_args={
                    "minimum": constants.MIN_DIMENSION,
                    "maximum": constants.MAX_DIMENSION,
                    "step": 8,
                },
                section=constants.SECTION,
            ),
        )


class PredefinedAspectRatioButtons(ArhUIComponent):
    def render(self):
        use_max_dim_op = settings.safe_opt(
            constants.ARL_PREDEFINED_ASPECT_RATIO_USE_MAX_DIM_KEY,
        )
        aspect_ratios = settings.safe_opt(
            constants.ARL_PREDEFINED_ASPECT_RATIOS_KEY,
        ).split(",")

        with (
            gr.Column(variant="panel", visible=self.should_show()),
            gr.Row(
                variant="compact",
                visible=self.should_show(),
                elem_classes="arl-btn-row",
            ),
        ):
            for ar_str in aspect_ratios:
                w, h, *_ = (abs(float(d)) for d in ar_str.split(":"))

                inputs = []
                if use_max_dim_op:
                    ar_func = partial(
                        util.scale_dimensions_to_max_dim_func,
                        width=w,
                        height=h,
                        max_dim=lambda: self.script.max_dimension,
                    )
                else:
                    inputs.extend([self.script.wc, self.script.hc])
                    ar_func = partial(
                        util.scale_dimensions_to_ui_width_or_height,
                        arw=w,
                        arh=h,
                    )

                gr.Button(
                    value=self.display_func(ar_str) or ar_str.strip(),
                    visible=self.should_show(),
                ).click(
                    fn=ar_func,
                    inputs=inputs,
                    outputs=[self.script.wc, self.script.hc],
                )

    @staticmethod
    def should_show() -> bool:
        return settings.safe_opt(constants.ARL_SHOW_PREDEFINED_ASPECT_RATIOS_KEY)

    @staticmethod
    def add_options(shared):
        shared.opts.add_option(
            key=constants.ARL_SHOW_PREDEFINED_ASPECT_RATIOS_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_SHOW_PREDEFINED_ASPECT_RATIOS_KEY,
                ),
                label="Show pre-defined aspect ratio buttons",
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_PREDEFINED_ASPECT_RATIO_USE_MAX_DIM_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_PREDEFINED_ASPECT_RATIO_USE_MAX_DIM_KEY,
                ),
                label=(
                    'Use "Maximum dimension" for aspect ratio buttons '
                    "(by default we use the max of current width/height)"
                ),
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_PREDEFINED_ASPECT_RATIOS_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_PREDEFINED_ASPECT_RATIOS_KEY,
                ),
                label="Pre-defined aspect ratio buttons (1:1, 4:3, 16:9, …)",
                section=constants.SECTION,
            ),
        )

    @property
    def display_func(self) -> Callable[[str], str | None]:
        return lambda _: None


class PredefinedPercentageButtons(ArhUIComponent):
    def render(self):
        inputs = outputs = [self.script.wc, self.script.hc]
        with (
            gr.Column(variant="panel", visible=self.should_show()),
            gr.Row(
                variant="compact",
                visible=self.should_show(),
                elem_classes="arl-btn-row",
            ),
        ):
            pps = settings.safe_opt(constants.ARL_PREDEFINED_PERCENTAGES_KEY)
            percentages = [abs(int(x)) for x in pps.split(",")]

            for percentage in percentages:
                display = self.display_func(percentage)
                gr.Button(
                    value=display,
                    visible=self.should_show(),
                ).click(
                    fn=partial(
                        util.scale_by_percentage,
                        pct=percentage / 100,
                    ),
                    inputs=inputs,
                    outputs=outputs,
                )

    @staticmethod
    def should_show() -> bool:
        return settings.safe_opt(constants.ARL_SHOW_PREDEFINED_PERCENTAGES_KEY)

    @staticmethod
    def add_options(shared):
        shared.opts.add_option(
            key=constants.ARL_SHOW_PREDEFINED_PERCENTAGES_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_SHOW_PREDEFINED_PERCENTAGES_KEY,
                ),
                label="Show pre-defined percentage buttons",
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_PREDEFINED_PERCENTAGES_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_PREDEFINED_PERCENTAGES_KEY,
                ),
                label="Pre-defined percentage buttons (75, 125, 150)",
                section=constants.SECTION,
            ),
        )
        shared.opts.add_option(
            key=constants.ARL_PREDEFINED_PERCENTAGES_DISPLAY_KEY,
            info=shared.OptionInfo(
                default=settings.OPT_KEY_TO_DEFAULT_MAP.get(
                    constants.ARL_PREDEFINED_PERCENTAGES_DISPLAY_KEY,
                ),
                label="Pre-defined percentage display format",
                component=gr.Dropdown,
                component_args=lambda: {
                    "choices": tuple(settings.PREDEFINED_PERCENTAGES_DISPLAY_MAP.keys()),
                },
                section=constants.SECTION,
            ),
        )

    @property
    def display_func(self) -> Callable[[int], str]:
        return settings.PREDEFINED_PERCENTAGES_DISPLAY_MAP.get(
            settings.safe_opt(constants.ARL_PREDEFINED_PERCENTAGES_DISPLAY_KEY),
        )
