# VoVoice AI Service
# Licensed under GNU GPLv3
# Copyright VoVoice 2026 Onwards

import requests
from datetime import datetime, timedelta
from typing import Optional


class AIService:
    def __init__(self):
        self.api_key = None
        self.models = []
        self.system_prompt = ""
        self.max_tokens = 1024
        self.temperature = 0.7
        self.timeout = 30
        self.model_health = {}

    def configure(self, config):
        self.api_key = config.openrouter_token
        self.models = [config.ai.primary_model] + config.ai.backup_models
        self.system_prompt = config.ai.system_prompt
        self.max_tokens = config.ai.max_tokens
        self.temperature = config.ai.temperature
        self.timeout = config.ai.timeout
        self.model_health = {m: {"status": "unknown", "last_check": None} for m in self.models}

    def chat(self, messages: list, session_memory: Optional[list] = None) -> tuple:
        full_messages = [{"role": "system", "content": self.system_prompt}]

        if session_memory:
            full_messages.extend(session_memory)

        full_messages.extend(messages)

        for model in self.models:
            try:
                response = self._call_openrouter(model, full_messages)
                self._update_health(model, "available")
                return response, model
            except requests.exceptions.Timeout:
                self._update_health(model, "timeout")
                continue
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    self._update_health(model, "rate_limited")
                elif e.response.status_code >= 500:
                    self._update_health(model, "server_error")
                else:
                    self._update_health(model, "error")
                continue
            except Exception:
                self._update_health(model, "error")
                continue

        raise Exception("All AI models unavailable")

    def _call_openrouter(self, model: str, messages: list) -> str:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://vovoice.qzz.io",
                "X-Title": "VoVoice"
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _update_health(self, model: str, status: str):
        self.model_health[model] = {
            "status": status,
            "last_check": datetime.now().isoformat()
        }

    def get_health(self) -> dict:
        available_count = sum(1 for m in self.model_health.values() if m["status"] == "available")

        return {
            "status": "ready" if available_count > 0 else "unavailable",
            "primary_model": self.models[0] if self.models else None,
            "primary_status": self.model_health.get(self.models[0], {}).get("status", "unknown") if self.models else "unknown",
            "models_available": available_count,
            "models": [
                {
                    "name": m,
                    "status": self.model_health.get(m, {}).get("status", "unknown"),
                    "role": "primary" if i == 0 else "backup"
                }
                for i, m in enumerate(self.models)
            ]
        }

    def get_models_list(self) -> list:
        return [
            {
                "name": m,
                "status": self.model_health.get(m, {}).get("status", "unknown"),
                "last_check": self.model_health.get(m, {}).get("last_check"),
                "role": "primary" if i == 0 else "backup"
            }
            for i, m in enumerate(self.models)
        ]


ai_service = AIService()
