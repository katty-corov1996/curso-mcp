"""In-memory conversation history — the model 'remembers' because we resend it."""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types


load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = (
    "Eres un asistente breve. "
    "Respondes en español."
)

# Conversation history.
history: list[dict] = []

# Keeps the last 10 user/model exchanges.
MAX_TURNS = 10


def trim_history() -> None:
    """Keeps only the most recent conversation turns."""

    max_entries = MAX_TURNS * 2

    if len(history) > max_entries:
        del history[:-max_entries]


def send(message: str, _retries: int = 0) -> str:
    """Sends a message while preserving conversation history."""

    trim_history()

    history.append(
        {
            "role": "user",
            "parts": [
                {
                    "text": message,
                }
            ],
        }
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=500,
                thinking_config=types.ThinkingConfig(
                    thinking_level="minimal"
                ),
            ),
        )

    except errors.ClientError as exc:
        # 429 = requests-per-minute limit.
        if exc.code == 429 and _retries < 3:
            wait = 2 ** _retries

            print(
                f"[429] Límite de RPM alcanzado. "
                f"Reintentando en {wait}s..."
            )

            time.sleep(wait)

            # Remove the duplicated user message before retrying.
            history.pop()

            return send(
                message,
                _retries=_retries + 1,
            )

        # Other client errors should not be retried.
        history.pop()

        return (
            f"Error del cliente ({exc.code}): "
            f"{exc.message}. No se reintenta."
        )

    except errors.ServerError as exc:
        # Retry temporary server errors such as 500 or 503.
        if _retries < 3:
            wait = 2 ** _retries

            print(
                f"[{exc.code}] Error del servidor. "
                f"Reintentando en {wait}s..."
            )

            time.sleep(wait)

            history.pop()

            return send(
                message,
                _retries=_retries + 1,
            )

        history.pop()

        return (
            "El servicio no respondió tras varios "
            f"intentos ({exc.code})."
        )

    # Token usage for this request.
    usage = response.usage_metadata

    print(
        f"[tokens] total_token_count="
        f"{usage.total_token_count}"
    )

    # Check why generation stopped.
    finish_reason = str(
        response.candidates[0].finish_reason
    )

    print(f"[finish] {finish_reason}")

    if "MAX_TOKENS" in finish_reason:
        print(
            "[warning] Respuesta truncada "
            "por max_output_tokens."
        )

    # Save Gemini's response in conversation history.
    history.append(
        {
            "role": "model",
            "parts": [
                {
                    "text": response.text,
                }
            ],
        }
    )

    return response.text


def main() -> None:
    """Runs the graded 8-turn conversation."""

    print("\nTurno 1:")
    print(
        send(
            "Me llamo Alex y mi color favorito es el verde."
        )
    )
    time.sleep(4)

    print("\nTurno 2:")
    print(
        send(
            "¿Qué framework de Python vimos en la Clase 1?"
        )
    )
    time.sleep(4)

    print("\nTurno 3:")
    print(
        send(
            "Dame un ejemplo de dato que no cabe en un int."
        )
    )
    time.sleep(4)

    print("\nTurno 4:")
    print(
        send(
            "¿Qué hace el comando uv init?"
        )
    )
    time.sleep(4)

    print("\nTurno 5:")
    print(
        send(
            "Explica en una frase qué es un token."
        )
    )
    time.sleep(4)

    print("\nTurno 6:")
    print(
        send(
            "¿Qué significa que una API sea stateless?"
        )
    )
    time.sleep(4)

    print("\nTurno 7:")
    print(
        send(
            "¿Para qué sirve un archivo .env?"
        )
    )
    time.sleep(4)

    print("\nTurno 8:")
    print(
        send(
            "¿Cómo me llamo y cuál es mi color favorito?"
        )
    )


if __name__ == "__main__":
    main()