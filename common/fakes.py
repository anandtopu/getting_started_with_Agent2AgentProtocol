"""Scripted model outputs: no API keys, network, sampling or hidden reasoning."""

from dataclasses import dataclass, field


@dataclass
class ScriptedModel:
    replies: list[dict]
    calls: list[str] = field(default_factory=list)

    async def decide(self, prompt: str) -> dict:
        self.calls.append(prompt)
        if not self.replies:
            raise ValueError("The scripted model ran out of replies.")
        return self.replies.pop(0)
