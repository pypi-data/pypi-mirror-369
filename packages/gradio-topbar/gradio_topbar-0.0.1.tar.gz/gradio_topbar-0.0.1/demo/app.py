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
        """
        # TopBar Demo
        This demo shows the `TopBar` with `width="50%"` and `bring_to_front=True`.
        Notice how the bar is now horizontally centered and no longer full-width.
        """
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