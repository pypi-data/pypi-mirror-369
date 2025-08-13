"""Simple rules engine for pre-execution checks."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Pattern, Tuple, Union
import logging
import yaml

RuleResult = Tuple[str, str]


@dataclass
class Rule:
    """Representation of a single rule definition."""

    id: str
    pattern: Pattern[str]
    action: str = "reject"
    description: str = ""
    severity: str = "low"

    def apply(self, text: str) -> Optional[Tuple[str, str]]:
        """Return the action and payload if this rule matches ``text``.

        Args:
            text: The string to evaluate against the rule pattern.

        Returns:
            A two-tuple of action and payload when matched, otherwise ``None``.
        """
        if self.pattern.search(text):
            if self.action == "reject":
                return "reject", self.description or f"Rule {self.id} violated"
            if self.action == "refine":
                return "refine", text
        return None


_rules: List[Rule] = []


def register_rule(
    rule: Union[Rule, Callable[[str], Optional[Tuple[str, str]]]],
) -> None:
    """Register a new rule callback or ``Rule`` instance.

    Args:
        rule: Either a ``Rule`` object or a callable that accepts text and
            returns an optional ``(action, payload)`` tuple.

    Returns:
        None
    """
    if isinstance(rule, Rule):
        _rules.append(rule)
    else:
        # Wrap legacy callable into a ``Rule`` for compatibility
        class _Wrapper(Rule):
            def __init__(
                self, func: Callable[[str], Optional[Tuple[str, str]]]
            ):
                self.func = func
                super().__init__(
                    id=getattr(func, "__name__", "anon"),
                    # Match anything; func filters
                    pattern=re.compile(".*"),
                )

            def apply(self, text: str) -> Optional[Tuple[str, str]]:
                return self.func(text)

        _rules.append(_Wrapper(rule))


def clear_rules() -> None:
    """Remove all registered rules.

    Returns:
        None
    """
    _rules.clear()


def load_rules(directory: str = ".rules") -> None:
    """Load rule definitions from JSON or YAML files.

    Args:
        directory: Path to a folder containing ``.json`` or ``.yaml`` rule
            definitions.

    Returns:
        None
    """
    # Always include the built-in dangerous command rule
    register_rule(
        Rule(
            id="dangerous-cmd",
            pattern=re.compile(r"rm -rf"),  # Block destructive shell commands
            action="reject",
            description="Destructive command detected",
            severity="high",
        )
    )

    if not os.path.isdir(directory):
        return
    for path in Path(directory).iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = (
                    json.load(f)
                    if path.suffix.lower() == ".json"
                    else yaml.safe_load(f)
                )
        except Exception as exc:
            logging.warning("Failed to load rule file %s: %s", path, exc)
            continue
        pattern = data.get("pattern")
        action = data.get("action", "reject")
        description = data.get("description", "")
        rule_id = data.get("id", path.stem)
        severity = data.get("severity", "low")
        if not pattern:
            continue
        regex = re.compile(pattern)
        register_rule(
            Rule(
                id=rule_id,
                pattern=regex,
                action=action,
                description=description,
                severity=severity,
            )
        )


def apply_rules(step: str) -> dict:
    """Evaluate a workflow step against registered rules.

    Args:
        step: Text representing the proposed step to validate.

    Returns:
        A dictionary containing ``approved`` and either ``step`` or
        ``message`` keys depending on the outcome.
    """
    current = step
    for rule in _rules:
        res = rule.apply(current)
        if res is None:
            continue
        action, payload = res
        if action == "reject":
            return {"approved": False, "message": payload}
        if action == "refine":
            current = payload
    return {"approved": True, "step": current}


def evaluate(change_set) -> dict:
    """Evaluate a diff or list of modifications against registered rules.

    Args:
        change_set: Either a diff string or a list of change objects to
            validate.

    Returns:
        Dictionary describing approval status and any rule matches.
    """

    if isinstance(change_set, list):
        text = "\n".join(
            (
                item.get("diff", item.get("new_content", str(item)))
                if isinstance(item, dict)
                else str(item)
            )
            for item in change_set
        )  # Flatten change objects into one string for pattern matching
    else:
        text = str(change_set)

    matches = []
    block = False
    for rule in _rules:
        if rule.pattern.search(text):
            matches.append(
                {
                    "rule_id": rule.id,
                    "severity": rule.severity,
                    "description": rule.description,
                }
            )
            if rule.severity.lower() in {"high"}:
                block = True

    return {"approved": not block, "matches": matches}


# --- Default Rules ----------------------------------------------------------

# Load any external rules from the .rules directory when the module is imported
load_rules()
