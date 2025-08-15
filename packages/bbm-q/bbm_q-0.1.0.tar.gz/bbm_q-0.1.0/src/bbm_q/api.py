import json
import requests
from typing import Optional
from ._config import API_KEY, DEFAULT_MODEL, OPENROUTER_URL, HTTP_REFERER, X_TITLE

def _headers():
    if not API_KEY or API_KEY.startswith("REPLACE_WITH_"):
        raise RuntimeError("В _config.py не задан API_KEY.")
    h = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    if HTTP_REFERER:
        h["HTTP-Referer"] = HTTP_REFERER
    if X_TITLE:
        h["X-Title"] = X_TITLE
    return h

def q(prompt: str,
      model: Optional[str] = None,
      system: Optional[str] = None,
      echo: bool = True) -> str:
    """
    Отправляет один промпт в OpenRouter и возвращает текст ответа.
    Минимум зависимостей, без переменных окружения.
    """
    m = model or DEFAULT_MODEL

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {"model": m, "messages": messages}

    resp = requests.post(
        OPENROUTER_URL,
        headers=_headers(),
        data=json.dumps(payload),
        timeout=120,
    )

    # Пытаемся распарсить ответ
    try:
        data = resp.json()
    except Exception:
        resp.raise_for_status()
        raise

    if resp.status_code >= 400:
        # Дадим осмысленную ошибку
        msg = None
        if isinstance(data, dict):
            msg = (data.get("error") or {}).get("message") or data.get("message")
        raise RuntimeError(f"OpenRouter error {resp.status_code}: {msg or data}")

    try:
        text = data["choices"][0]["message"]["content"]
    except Exception:
        raise RuntimeError(f"Unexpected response format: {data}")

    if echo:
        print(text)
    return text
