
import gradio as gr
from app import demo as app
import os

_docs = {'TopBar': {'description': 'TopBar is a collapsible panel that renders child components in a fixed bar at the top of the page.\n    with gr.Blocks() as demo:\n        with gr.TopBar(height=200, width="80%"):\n            gr.Textbox(label="Enter your text here")\n            gr.Button("Submit")', 'members': {'__init__': {'label': {'type': 'str | gradio.i18n.I18nData | None', 'default': 'None', 'description': 'name of the top bar. Not displayed to the user.'}, 'open': {'type': 'bool', 'default': 'True', 'description': 'if True, top bar is open by default.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, the component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'height': {'type': 'int | str', 'default': '320', 'description': 'The height of the top bar, specified in pixels if a number is passed, or in CSS units if a string is passed.'}, 'width': {'type': 'int | str', 'default': '"100%"', 'description': 'The width of the top bar, specified in pixels if a number is passed, or in CSS units (like "80%") if a string is passed. The bar will be horizontally centered.'}, 'bring_to_front': {'type': 'bool', 'default': 'False', 'description': 'If True, the TopBar will be rendered on top of all other elements with a higher z-index. Defaults to False.'}, 'key': {'type': 'int | str | tuple[int | str, Ellipsis] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': 'None', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}}, 'postprocess': {}}, 'events': {'expand': {'type': None, 'default': None, 'description': 'This listener is triggered when the TopBar is expanded.'}, 'collapse': {'type': None, 'default': None, 'description': 'This listener is triggered when the TopBar is collapsed.'}}}, '__meta__': {'additional_interfaces': {}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_topbar`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

A TopBar for Gradio Interface
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_topbar
```

## Usage

```python
# demo/app.py

import gradio as gr
import time
from gradio_topbar import TopBar

def chat_response(message, history):
    history = history or ""
    history += f"You: {message}\n"
    time.sleep(1) # Simulate thinking
    history += f"Bot: Thanks for the message! You said: '{message}'\n"
    return history, ""

def update_label(value):
    return f"Current temperature is: {value}"

with gr.Blocks(theme=gr.themes.Ocean(), title="Full Layout Demo") as demo:
    gr.Markdown(
        \"\"\"
        # TopBar Demo
        This demo shows the `TopBar` with `width="50%"` and `bring_to_front=True`.
        Notice how the bar is now horizontally centered and no longer full-width.
        \"\"\"
    )

    with TopBar(open=True, height=180, width="50%", bring_to_front=True):
        with gr.Row():
            message_box = gr.Textbox(
                show_label=False,
                placeholder="Type your message here...",
                elem_id="message-input",
                scale=7
            )
            send_button = gr.Button("Send", variant="primary", scale=1)
        with gr.Row():
            gr.Button("Upload File")
            gr.Button("Record Audio")
            gr.ClearButton([message_box])

    with gr.Row(equal_height=True):
        with gr.Column(scale=3):
            gr.Markdown("### 🤖 Chat Interface")
            chatbot_display = gr.Textbox(
                label="Chat History",
                lines=25,
                interactive=False
            )

    send_button.click(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )
    message_box.submit(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )

if __name__ == "__main__":
    demo.launch(debug=True)
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `TopBar`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["TopBar"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["TopBar"]["events"], linkify=['Event'])







    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {};
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
