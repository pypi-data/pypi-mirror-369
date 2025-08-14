# PromptGuru

**Modular prompt engineering library** for BERT, Mistral, LLaMA, and FLAN-T5 using YAML templates.
Includes modes like **ELI5**, **DevMode**, **Refine**, **Classification**, and **QA**.

## Why
- Lightweight and framework-agnostic
- YAML-first: edit prompts without changing code
- Consistent modes across multiple model families

## Install (Local Dev)
```bash
pip install PyYAML
```
> For now, clone or copy this repo. PyPI packaging steps are included below.

## Usage
```python
from promptguru.engine import PromptEngine

engine = PromptEngine(model_type="mistral", mode="eli5")
prompt = engine.generate_prompt("What is quantum entanglement?")
print(prompt)
```

## Templates
Templates live in `promptguru/templates/`:
- `bert.yaml` → `classification`, `fill_mask`, `qa`
- `mistral.yaml` → `eli5`, `devmode`, `refine`
- `llama.yaml` → `eli5`, `devmode`, `refine`
- `flan_t5.yaml` → `eli5`, `devmode`, `explain_and_tag`

## Roadmap
- Add inference adapters (HF Inference API, OpenRouter) behind a common interface
- Add more modes (contrastive QA, chain-of-thought, safety/risk tags)

## License
Apache 2.0
