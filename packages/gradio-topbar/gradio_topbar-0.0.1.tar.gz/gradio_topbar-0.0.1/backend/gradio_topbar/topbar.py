# gradio_topbar/topbar.py

from __future__ import annotations

from typing import Literal

from gradio_client.documentation import document

from gradio.blocks import BlockContext
from gradio.component_meta import ComponentMeta
from gradio.events import Events
from gradio.i18n import I18nData


@document()
class TopBar(BlockContext, metaclass=ComponentMeta):
    """
    TopBar is a collapsible panel that renders child components in a fixed bar at the top of the page.
    Example:
        with gr.Blocks() as demo:
            with gr.TopBar(height=200, width="80%"):
                gr.Textbox(label="Enter your text here")
                gr.Button("Submit")
    Guides: controlling-layout
    """

    EVENTS = [Events.expand, Events.collapse]

    def __init__(
        self,
        label: str | I18nData | None = None,
        *,
        open: bool = True,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        height: int | str = 320,
        width: int | str = "100%",
        bring_to_front: bool = False,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = None,
    ):
        """
        Parameters:
            label: name of the top bar. Not displayed to the user.
            open: if True, top bar is open by default.
            visible: If False, the component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            height: The height of the top bar, specified in pixels if a number is passed, or in CSS units if a string is passed.
            width: The width of the top bar, specified in pixels if a number is passed, or in CSS units (like "80%") if a string is passed. The bar will be horizontally centered.
            bring_to_front: If True, the TopBar will be rendered on top of all other elements with a higher z-index. Defaults to False.
            key: in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
        """
        self.label = label
        self.open = open
        self.height = height
        self.width = width
        self.bring_to_front = bring_to_front
        BlockContext.__init__(
            self,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
        )