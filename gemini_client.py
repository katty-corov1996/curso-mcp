"""Calls Gemini with a system instruction and explicit generation parameters."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = (
    "Eres un instructor de programación para principiantes. "
    "Respondes en español, máximo 3 frases. "
    "Sin jerga sin explicar, sin inventar funciones."
)

CONTEXT_WINDOW_LIMIT = 1_048_576


def ask(prompt: str, temperature: float = 0.7) -> tuple[str, str]:
    """Returns (text, finish_reason)."""

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=temperature,
            max_output_tokens=500,
            thinking_config=types.ThinkingConfig(
                thinking_level="minimal"
            ),
        ),
    )

    u = response.usage_metadata
    print(f"prompt    : {u.prompt_token_count}")
    print(f"respuesta : {u.candidates_token_count}")
    print(f"TOTAL     : {u.total_token_count}")

    finish_reason = str(response.candidates[0].finish_reason)
    print(f"finish    : {finish_reason}")

    if "MAX_TOKENS" in finish_reason:
        print(
            "[warning] La respuesta viene truncada "
            "por max_output_tokens."
        )

    return response.text, finish_reason


def print_budget(contents: list[dict]) -> None:
    tokens = client.models.count_tokens(
        model=MODEL,
        contents=contents,
    )

    used_ratio = tokens.total_tokens / CONTEXT_WINDOW_LIMIT

    print(
        f"Historial: {tokens.total_tokens} tokens "
        f"({used_ratio:.4%} de la ventana)"
    )


def main() -> None:
    r1_text, _ = ask("Hola, me llamo Valeria.")
    print("\nBOT:", r1_text)

    r2_text, _ = ask("¿Cómo me llamo?")
    print("\nBOT:", r2_text)


if __name__ == "__main__":
    main()

