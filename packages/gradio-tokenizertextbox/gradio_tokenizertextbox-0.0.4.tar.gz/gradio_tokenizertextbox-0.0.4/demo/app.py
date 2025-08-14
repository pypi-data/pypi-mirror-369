#
# demo/app.py
#
import gradio as gr
from gradio_tokenizertextbox import TokenizerTextBox 
import json

# --- Data and Helper Functions ---

TOKENIZER_OPTIONS = {
    "Xenova/clip-vit-large-patch14": "CLIP ViT-L/14",
    "Xenova/gpt-4": "gpt-4 / gpt-3.5-turbo / text-embedding-ada-002",
    "Xenova/text-davinci-003": "text-davinci-003 / text-davinci-002",
    "Xenova/gpt-3": "gpt-3",
    "Xenova/grok-1-tokenizer": "Grok-1",
    "Xenova/claude-tokenizer": "Claude",
    "Xenova/mistral-tokenizer-v3": "Mistral v3",
    "Xenova/mistral-tokenizer-v1": "Mistral v1",
    "Xenova/gemma-tokenizer": "Gemma",
    "Xenova/llama-3-tokenizer": "Llama 3",
    "Xenova/llama-tokenizer": "LLaMA / Llama 2",
    "Xenova/c4ai-command-r-v01-tokenizer": "Cohere Command-R",
    "Xenova/t5-small": "T5",
    "Xenova/bert-base-cased": "bert-base-cased",
}

dropdown_choices = [
    (display_name, model_name) 
    for model_name, display_name in TOKENIZER_OPTIONS.items()
]

def process_output(tokenization_data):
    """
    This function receives the full dictionary from the component.
    """
    if not tokenization_data:
        return {"status": "Waiting for input..."}
    return tokenization_data

# --- Gradio Application ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # --- Header and Information ---
    gr.Markdown("# TokenizerTextBox Component Demo")
    gr.Markdown("Component idea taken from the original example application on [Xenova Tokenizer Playground](https://github.com/huggingface/transformers.js-examples/tree/main/the-tokenizer-playground)")
    
    # --- Global Controls (affect both tabs) ---
    with gr.Row():
        model_selector = gr.Dropdown(
            label="Select a Tokenizer",
            choices=dropdown_choices,
            value="Xenova/clip-vit-large-patch14",
        )
        
        display_mode_radio = gr.Radio(
            ["text", "token_ids", "hidden"],
            label="Display Mode",
            value="text"
        )

    # --- Tabbed Interface for Different Modes ---
    with gr.Tabs():
        # --- Tab 1: Standalone Mode ---
        with gr.TabItem("Standalone Mode"):
            gr.Markdown("### In this mode, the component acts as its own interactive textbox.")
            gr.Markdown("<span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_tokenizertextbox'>GitHub Code</a></span>")
            
            standalone_tokenizer = TokenizerTextBox(
                label="Type your text here",
                value="Gradio is an awesome tool for building ML demos!",
                model="Xenova/clip-vit-large-patch14",                
                display_mode="text",
            )
            
            standalone_output = gr.JSON(label="Component Output")
            standalone_tokenizer.change(process_output, standalone_tokenizer, standalone_output)

        # --- Tab 2: Listener ("Push") Mode ---
        with gr.TabItem("Listener Mode"):
            gr.Markdown("### In this mode, the component is a read-only visualizer for other text inputs.")
            
            with gr.Row():
                prompt_1 = gr.Textbox(label="Prompt Part 1", value="A photorealistic image of an astronaut")
                prompt_2 = gr.Textbox(label="Prompt Part 2", value="riding a horse on Mars")

            visualizer = TokenizerTextBox(
                label="Concatenated Prompt Visualization",
                hide_input=True, # Hides the internal textbox
                model="Xenova/clip-vit-large-patch14",
                display_mode="text",
            )
            
            visualizer_output = gr.JSON(label="Visualizer Component Output")

            # --- "Push" Logic ---
            def update_visualizer_text(p1, p2):
                concatenated_text = f"{p1}, {p2}"
                # Return a new value for the visualizer.
                # The postprocess method will correctly handle this string.
                return gr.update(value=concatenated_text)

            # Listen for changes on the source textboxes
            prompt_1.change(update_visualizer_text, [prompt_1, prompt_2], visualizer)
            prompt_2.change(update_visualizer_text, [prompt_1, prompt_2], visualizer)

            # Also connect the visualizer to its own JSON output
            visualizer.change(process_output, visualizer, visualizer_output)

            # Run once on load to show the initial state
            demo.load(update_visualizer_text, [prompt_1, prompt_2], visualizer)

    # --- Link Global Controls to Both Components ---
    # Create a list of all TokenizerTextBox components that need to be updated
    all_tokenizers = [standalone_tokenizer, visualizer]

    model_selector.change(
        fn=lambda model: [gr.update(model=model) for _ in all_tokenizers],
        inputs=model_selector,
        outputs=all_tokenizers
    )
    display_mode_radio.change(
        fn=lambda mode: [gr.update(display_mode=mode) for _ in all_tokenizers],
        inputs=display_mode_radio,
        outputs=all_tokenizers
    )

if __name__ == '__main__':
    demo.launch()