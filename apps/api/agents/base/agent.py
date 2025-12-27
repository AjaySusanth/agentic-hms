from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from datetime import datetime
from enum import Enum


StateType = TypeVar("StateType")


class InvalidStepTransition(Exception):
    pass


class BaseAgent(ABC, Generic[StateType]):
    allowed_transitions: Dict[Enum, list] = {}

    def __init__(self, state: StateType):
        self.state = state

    @abstractmethod
    def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def update_state(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)

        if hasattr(self.state, "updated_at"):
            self.state.updated_at = datetime.utcnow()

    def transition_to(self, next_step: Enum) -> None:
        current_step = self.state.step
        allowed = self.allowed_transitions.get(current_step, [])

        if next_step not in allowed:
            raise InvalidStepTransition(
                f"Invalid transition: {current_step} → {next_step}"
            )

        self.update_state(step=next_step)

    def call_tool(self, tool_fn, **kwargs):
        return tool_fn(**kwargs)
