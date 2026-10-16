from pathlib import Path

def load_prompt(name: str) -> str:
    """Carrega o conteúdo de um arquivo de prompt pelo nome."""
    prompt_path = Path(__file__).parent.parent / 'prompts' / f'{name}.md'
    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt '{name}' não encontrado em {prompt_path}"
        )
    return prompt_path.read_text(encoding='utf-8')
