from __future__ import annotations

import gradio as gr
from modules import script_callbacks, scripts

from lib_aspect_ratio_lock import constants
from lib_aspect_ratio_lock import settings


class Script(scripts.Script):
    """Always-visible accordion that scales the captured W/H sliders."""

    def __init__(self):
        self.t2i_w: gr.components.Slider | None = None
        self.t2i_h: gr.components.Slider | None = None
        self.i2i_w: gr.components.Slider | None = None
        self.i2i_h: gr.components.Slider | None = None
        self.wc: gr.components.Slider | None = None
        self.hc: gr.components.Slider | None = None
        self.max_dimension: float = float(constants.MAX_DIMENSION / 2)
        self.min_dimension: float = float(constants.MAX_DIMENSION / 2)

    def title(self) -> str:
        return constants.EXTENSION_NAME

    def show(self, _is_img2img) -> scripts.AlwaysVisible:
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        if is_img2img:
            self.wc, self.hc = self.i2i_w, self.i2i_h
        else:
            self.wc, self.hc = self.t2i_w, self.t2i_h

        component_instances = settings.sort_components_by_keys(
            [component(self) for component in settings.COMPONENTS],
        )

        hide_accordion: bool = settings.safe_opt(
            constants.ARL_HIDE_ACCORDION_BY_DEFAULT_KEY,
        )

        if hide_accordion or not any(c.should_show() for c in component_instances):
            return

        start_expanded: bool = settings.safe_opt(constants.ARL_EXPAND_BY_DEFAULT_KEY)
        with gr.Group(), gr.Accordion(constants.EXTENSION_NAME, open=start_expanded):
            for component in component_instances:
                # Always call render() so Gradio components exist; visibility is
                # controlled per-component via should_show() / visible=.
                component.render()

    def after_component(self, component: gr.components.Component, **kwargs):
        element_id = kwargs.get("elem_id")

        if not isinstance(component, gr.components.Slider):
            return

        if element_id == "txt2img_width":
            self.t2i_w = component
        elif element_id == "txt2img_height":
            self.t2i_h = component
        elif element_id == "img2img_width":
            self.i2i_w = component
        elif element_id == "img2img_height":
            self.i2i_h = component


script_callbacks.on_ui_settings(settings.on_ui_settings)
