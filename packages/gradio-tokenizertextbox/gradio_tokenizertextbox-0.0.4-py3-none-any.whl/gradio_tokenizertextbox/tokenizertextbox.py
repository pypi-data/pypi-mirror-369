#
# backend/tokenizer_playground/__init__.py
#
from __future__ import annotations
from typing import Any, Callable, List, Literal, Sequence

from gradio.components.base import Component, FormComponent
from gradio.events import Events
import gradio as gr

class TokenizerTextBox(FormComponent):
    """
    Creates a textarea for user to enter string input or display string output,
    with built-in, client-side tokenization visualization powered by Transformers.js.
    The component's value is a JSON object containing the text and tokenization results.
    """
    EVENTS = [Events.change, Events.input, Events.submit, Events.blur, Events.select]

    def __init__(
        self,
        value: str | dict | Callable | None = None,
        *,
        # Custom parameters for this component
        model: str = "Xenova/gpt-3",
        display_mode: Literal['text', 'token_ids', 'hidden'] = 'text',
        hide_input: bool = False,           
        model_max_length: int | None = None,
        lines: int = 2,
        max_lines: int | None = None,
        placeholder: str | None = None,
        autofocus: bool = False,
        autoscroll: bool = True,
        text_align: Literal["left", "right"] | None = None,
        rtl: bool = False,
        show_copy_button: bool = False,
        max_length: int | None = None,
        
        # Standard FormComponent props that are passed to super()
        label: str | None = None,
        info: str | None = None,
        every: float | None = None,
        show_label: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,      
      
        **kwargs,
    ):
        """
        Initializes the TokenizerTextBox component.

        Parameters:
            value: The initial value. Can be a string to initialize the text, or a dictionary for full state. If a function is provided, it will be called when the app loads to set the initial value.
            model: The name of a Hugging Face tokenizer to use (must be compatible with Transformers.js). Defaults to "Xenova/gpt-2".
            display_mode: Controls the content of the token visualization panel. Can be 'text' (default), 'token_ids', or 'hidden'.
            hide_input: If True, the component's own textbox is hidden, turning it into a read-only visualizer. Defaults to False.
            model_max_length: The maximum number of tokens for the model. If the token count exceeds this, the counter will turn red. If not provided, the component will try to detect it from the loaded tokenizer.
            lines: The minimum number of line rows for the textarea.
            max_lines: The maximum number of line rows for the textarea.
            placeholder: A placeholder hint to display in the textarea when it is empty.
            label: The label for this component, displayed above the component.
            info: Additional component description, displayed below the label.
            every: If `value` is a callable, this sets a timer to run the function repeatedly.
            show_label: If False, the label is not displayed.
            container: If False, the component will not be wrapped in a container.
            scale: The relative size of the component compared to others in a `gr.Row` or `gr.Column`.
            min_width: The minimum-width of the component in pixels.
            interactive: If False, the user will not be able to edit the text.
            visible: If False, the component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM.
            autofocus: If True, will focus on the textbox when the page loads.
            autoscroll: If True, will automatically scroll to the bottom of the textbox when the value changes.
            text_align: How to align the text in the textbox, can be: "left" or "right".
            rtl: If True, sets the direction of the text to right-to-left.
            show_copy_button: If True, a copy button will be shown.
            max_length: The maximum number of characters allowed in the textbox.
        """
        # Store all the custom/frontend-specific props on the instance.
        # Gradio will automatically pass these to the Svelte component.
        
                 
        self.model = model
        self.display_mode = display_mode       
        self.hide_input = hide_input
        self.model_max_length = model_max_length
        self.lines = lines
        self.max_lines = max_lines
        self.placeholder = placeholder
        self.autofocus = autofocus
        self.autoscroll = autoscroll
        self.text_align = text_align
        self.rtl = rtl
        self.show_copy_button = show_copy_button
        self.max_length = max_length
        
        # Call the parent constructor with ONLY the arguments it expects,
        # plus the catch-all kwargs.
        super().__init__(
            label=label,
            info=info,
            every=every,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            value=value,            
            **kwargs, # Pass any extra arguments up the chain.
        )

    def preprocess(self, payload: dict | None) -> dict | None:
        """
        Processes the main value of the component, which is a dictionary.
        Enriches it with character and token counts before passing it to the Python function.
        
        Parameters:
            payload: The dictionary value from the frontend, e.g., {"text": "...", "tokens": [...], ...}.
        Returns:
            A dictionary enriched with 'char_count' and 'token_count'.
        """
        if payload is None:
            return {"text": "", "tokens": [], "token_ids": [], "char_count": 0, "token_count": 0}

        text = payload.get("text", "")
        tokens = payload.get("tokens", [])
        
        payload["char_count"] = len(text)
        payload["token_count"] = len(tokens)
        
        return payload

    def postprocess(self, value: str | dict | None) -> dict | None:
        """
        Handles setting the component's value from Python.
        If a simple string is provided, it wraps it in the dictionary
        structure that the frontend expects.

        Parameters:
            value: The value to set for the component, can be a string or a dictionary.
        Returns:
            A dictionary formatted for the frontend.
        """
        if value is None:
            return None
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, str):
            return {"text": value, "tokens": [], "token_ids": []}
        
        return None
  
    def api_info(self) -> dict[str, Any]:
        """
        Defines the API info for the component. The output is a JSON object.
        """
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "tokens": {"type": "array", "items": {"type": "string"}},
                "token_ids": {"type": "array", "items": {"type": "integer"}},
                "char_count": {"type": "integer"},
                "token_count": {"type": "integer"},
            },
            "description": "An object containing the tokenization results and counts.",
        }

    def example_payload(self) -> Any:
        """
        An example of the JSON object that this component's `preprocess` method returns.
        """
        return {
            "text": "Gradio is great!",
            "tokens": ["Gradio", " is", " great", "!"],
            "token_ids": [35345, 318, 1049, 0],
            "char_count": 16,
            "token_count": 4,
        }

    def example_value(self) -> Any:
        """
        An example of the value that can be passed to the component.
        """
        return {"text": "This is the initial text.", "tokens": [], "token_ids": []}