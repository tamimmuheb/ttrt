from __future__ import annotations
import os
from typing import List

from tenacity import retry, wait_exponential, stop_after_attempt

try:
    from litellm import completion
except Exception:  # LiteLLM may not be installed in some contexts
    completion = None


MODEL_DEFAULT = os.getenv("LLM_MODEL", "gpt-4o-mini")


@retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
def chat(prompt: str, system: str = "You are a helpful research assistant.") -> str:
    if completion is None:
        # Fallback: return prompt tail
        return prompt[-2000:]
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = MODEL_DEFAULT
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]
    resp = completion(model=model, messages=messages)
    try:
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return str(resp)


def summarize_text(text: str, max_words: int = 120) -> str:
    if os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"):
        prompt = (
            "Summarize the following research abstract into "
            f"~{max_words} words focusing on problem, method, and findings.\n\n{text}"
        )
        return chat(prompt)
    # Extractive fallback: simple lead-based summary
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    summary = '. '.join(sentences[:3])
    return summary[:max_words * 7]


def generate_hypothesis(query: str, ranked_notes: List[str]) -> str:
    context = "\n".join(ranked_notes[:8])
    if os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"):
        prompt = (
            "You are a senior researcher. Given the query and evidence notes, propose a clear, "
            "falsifiable hypothesis that could be tested, and briefly justify it.\n\n"
            f"Query: {query}\n\nEvidence notes:\n{context}\n\n"
            "Return only the hypothesis and 1-2 sentence justification."
        )
        return chat(prompt)
    # Fallback heuristic
    return f"Hypothesis: Based on the evidence, addressing '{query}', we expect measurable improvements under the proposed method."


def polish_latex(latex_src: str) -> str:
    if os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"):
        prompt = (
            "Improve the following LaTeX for readability and academic style without changing content.\n\n"
            f"{latex_src}"
        )
        return chat(prompt, system="You are an expert LaTeX editor.")
    return latex_src