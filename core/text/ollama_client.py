"""Ollama 客户端封装。"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Sequence

import requests

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class OllamaClient:
    base_url: str = "http://127.0.0.1:11434"

    def generate(self, model: str, prompt: str, retries: int = 2) -> str:
        payload = {"model": model, "prompt": prompt}
        for attempt in range(retries + 1):
            try:
                response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except requests.RequestException as exc:  # pragma: no cover
                LOGGER.warning("Ollama 请求失败，第 %s 次：%s", attempt + 1, exc)
        raise RuntimeError("Ollama 调用失败，超出重试次数")


__all__ = ["OllamaClient"]
