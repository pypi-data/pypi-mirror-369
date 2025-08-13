"""A minimal example agent to demonstrate the agent interface.

This agent is intentionally simple and deterministic so it can be used in
documentation and unit tests without external dependencies.
"""

from typing import Dict, Any

from server.agents.base import BaseAgent


class EchoAgent(BaseAgent):
    """Example agent that echoes the provided input with metadata.

    Usage:

        from server.agents.example_agent import EchoAgent

        with EchoAgent() as agent:
            result = agent.run({"text": "hello"})
            assert result["text"] == "hello"
    """

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = payload.get("text")
        # no external calls — deterministic result for docs/tests
        return {
            "status": "ok",
            "text": text,
            "length": len(text) if text else 0,
        }
