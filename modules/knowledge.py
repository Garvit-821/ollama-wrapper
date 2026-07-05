"""
VISION AI Assistant - Knowledge Module
Study help, concept explanation, quizzes, and flashcards.
"""


def explain_concept(topic: str, mode: str = "explain", level: str = "intermediate", llm_engine=None) -> str:
    """Explain a concept using the LLM."""
    if not llm_engine:
        return "Error: LLM engine not available."

    result = llm_engine.explain_topic(topic, mode, level)

    mode_labels = {
        "explain": "[EXPLANATION]",
        "summarize": "[SUMMARY]",
        "quiz": "[QUIZ]",
        "flashcards": "[FLASHCARDS]",
    }
    label = mode_labels.get(mode, "[KNOWLEDGE]")

    return f"{label} {topic}:\n\n{result}"
