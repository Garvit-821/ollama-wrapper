"""
VISION AI Assistant - Code Generator Module
Generate code using the LLM and optionally save to files.
"""
import os
from pathlib import Path
import config


def generate_code(description: str, language: str = "python", save_to_file: str = None, llm_engine=None) -> str:
    """Generate code using the LLM."""
    if not llm_engine:
        return "Error: LLM engine not available for code generation."

    code = llm_engine.generate_code(description, language)

    if save_to_file:
        try:
            save_path = Path(save_to_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(code)
            return f"[CODE] Generated and saved to: {save_path}\n\n{code}"
        except Exception as e:
            return f"[CODE] Generated but could not save ({e}):\n\n{code}"

    return f"[CODE] Generated {language} code:\n\n{code}"
