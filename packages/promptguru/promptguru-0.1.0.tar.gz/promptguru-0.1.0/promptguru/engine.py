# promptguru/engine.py
from pathlib import Path
import yaml

def load_template(model_type: str) -> dict:
    """Load a YAML template file for a given model type (e.g., 'mistral', 'bert')."""
    model_type = model_type.lower()
    template_path = Path(__file__).parent / "templates" / f"{model_type}.yaml"
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found for model: {model_type}")
    with open(template_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class PromptEngine:
    """Minimal prompt templating engine.

    Usage:
        engine = PromptEngine(model_type="mistral", mode="eli5")
        prompt = engine.generate_prompt("Explain quantum entanglement")
    """
    def __init__(self, model_type: str, mode: str):
        self.model_type = model_type.lower()
        self.mode = mode.lower()
        self._template_dict = load_template(self.model_type)

    def generate_prompt(self, user_input: str) -> str:
        """Render a template with the given input text."""
        if self.mode not in self._template_dict:
            raise ValueError(f"Mode '{self.mode}' not found in {self.model_type}.yaml")
        template = self._template_dict[self.mode]
        return template.replace("{{input}}", user_input)
